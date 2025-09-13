import asyncio
import logging
import os
import pygame

log = logging.getLogger(__name__)

class AudioService:
    def __init__(self, cfg):
        self.cfg = cfg
        self._ready = False

    async def start(self):
        try:
            pygame.mixer.init()
            self._ready = True
            self._sounds = {}

            base = os.path.join(os.path.dirname(__file__), "sfx")
            os.makedirs(base, exist_ok=True)

            for fn in os.listdir(base):
                if not fn.lower().endswith((".wav", ".ogg", ".mp3")):
                    continue
                path = os.path.join(base, fn)
                if not os.path.isfile(path):
                    continue

                # sleutel = bestandsnaam zonder extensie, lowercase
                key = os.path.splitext(fn)[0].lower()

                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                except Exception as e:
                    log.warning(f"Kon sound {fn} niet laden: {e}")

            log.info({"msg": "audio ready", "sounds": list(self._sounds)})
        except Exception:
            log.exception("audio init failed")


    async def stop(self):
        try:
            pygame.mixer.quit()
        except Exception:
            pass

    async def is_connected(self) -> bool:
        return self._ready

    async def set_volume(self, vol: int):
        if not self._ready: return
        v = max(0, min(100, vol)) / 100.0
        pygame.mixer.music.set_volume(v)
        for s in self._sounds.values():
            s.set_volume(v)

    async def test_tone(self):
        # simple: play 'success' if exists
        if "success" in getattr(self, "_sounds", {}):
            self._sounds["success"].play()

    async def play_sfx(self, name: str):
        if not self._ready: return
        s = self._sounds.get(name)
        if s:
            s.play()
