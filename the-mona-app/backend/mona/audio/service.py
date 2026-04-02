import asyncio
import logging
import os
import pygame

log = logging.getLogger(__name__)

def _key(name: str) -> str:
    base, _ = os.path.splitext(name)
    return base.strip().lower()

class AudioService:
    def __init__(self, cfg, sfx_subdir="sfx"):
        self.cfg = cfg
        self._ready = False
        self._sounds = {}
        self._volume = 1.0  # 0.0..1.0
        self._sfx_subdir = sfx_subdir

    async def start(self):
        # Route audio via PulseAudio so Bluetooth sinks (JBL) are used
        os.environ.setdefault("SDL_AUDIODRIVER", "pulse")
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        # Init in background so the app starts immediately
        asyncio.create_task(self._init_with_retry())

    async def _init_with_retry(self):
        attempt = 0
        while True:
            attempt += 1
            try:
                pygame.mixer.init()
                break
            except Exception as e:
                log.warning(f"Audio init attempt {attempt} failed: {e} — retrying in 5s")
                await asyncio.sleep(5)

        try:
            self._ready = True
            self._sounds = {}

            base = os.path.join(os.path.dirname(__file__), self._sfx_subdir)
            os.makedirs(base, exist_ok=True)

            for fn in os.listdir(base):
                if not fn.lower().endswith((".wav", ".ogg", ".mp3")):
                    continue
                path = os.path.join(base, fn)
                if not os.path.isfile(path):
                    continue

                key = _key(fn)  # zonder extensie, lowercase
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(self._volume)
                    self._sounds[key] = snd
                except Exception as e:
                    log.warning(f"Kon sound {fn} niet laden: {e}")

            pygame.mixer.music.set_volume(self._volume)  # voor de zekerheid
            log.info({"msg": "audio ready", "sounds": sorted(self._sounds.keys())})
        except Exception:
            log.exception("audio init failed")

    async def stop(self):
        try:
            pygame.mixer.stop()
            pygame.mixer.quit()
        except Exception:
            pass

    async def is_connected(self) -> bool:
        return self._ready

    # -------- Volume --------
    async def set_volume(self, vol: int):
        """vol in 0..100"""
        if not self._ready:
            return
        self._volume = max(0, min(100, int(vol))) / 100.0
        pygame.mixer.music.set_volume(self._volume)
        for s in self._sounds.values():
            s.set_volume(self._volume)

    async def get_volume(self) -> int:
        return int(self._volume * 100)

    # -------- Lijsten & status --------
    async def list_sounds(self):
        return sorted(self._sounds.keys())

    async def status(self):
        # actief = sounds met >0 kanalen bezig
        active = [name for name, snd in self._sounds.items() if snd.get_num_channels() > 0]
        return {
            "connected": self._ready,
            "volume": int(self._volume * 100),
            "mixer_busy": bool(pygame.mixer.get_busy()),
            "active_sfx": active,
            "count_loaded": len(self._sounds),
        }

    # -------- Afspelen / Stoppen --------
    async def test_tone(self):
        if "success" in self._sounds:
            self._sounds["success"].play()

    async def play_sfx(self, name: str) -> bool:
        if not self._ready:
            return False

        k = _key(name)
        s = self._sounds.get(k)
        if not s:
            log.warning(f"SFX '{name}' niet gevonden")
            return False

        # 🔁 restart gedrag
        if s.get_num_channels() > 0:
            s.stop()     # stopt alle lopende kanalen van deze sound

        s.play()
        return True


    async def stop_sfx(self, name: str | None = None, fade_ms: int = 200):
        """Stop één sound (alle kanalen waar die speelt) of alles wanneer name=None."""
        if not self._ready:
            return
        if name:
            k = _key(name)
            s = self._sounds.get(k)
            if s:
                try:
                    # fade out alle kanalen waar deze Sound speelt
                    s.fadeout(max(0, int(fade_ms)))
                except Exception:
                    # als fadeout niet lukt, hard stop via mixer.stop() (maar dat stopt alles)
                    pass
            else:
                log.warning(f"stop_sfx: sound '{name}' niet gevonden")
        else:
            # alles stoppen
            if fade_ms and fade_ms > 0:
                try:
                    pygame.mixer.fadeout(int(fade_ms))
                except Exception:
                    pygame.mixer.stop()
            else:
                pygame.mixer.stop()
