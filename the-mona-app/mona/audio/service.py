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
            # preload basic sounds if present
            self._sounds = {}
            base = os.path.join(os.path.dirname(__file__), "sfx")
            for name in ("success", "fail"):
                path = os.path.join(base, f"{name}.wav")
                if os.path.exists(path):
                    self._sounds[name] = pygame.mixer.Sound(path)
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
