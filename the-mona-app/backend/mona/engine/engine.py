from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional

class GameEngine:
    def __init__(self, mqtt, audio, registry):
        self.mqtt = mqtt
        self.audio = audio
        self.registry = registry

        self.games: Dict[str, Any] = {}
        self.active: Optional[str] = None
        self.running: bool = False
        self._lock = asyncio.Lock()

    def register(self, key: str, game) -> None:
        self.games[key] = game

    async def set_idle(self):
        await self.stop()
        self.mqtt.publish("mona/buttons/all/cmd", {"type": "stop", "clear": True})
        self._publish_state()

    async def start(self, game: str, params: Dict[str, Any] | None = None):
        async with self._lock:
            if game not in self.games:
                raise ValueError(f"Unknown game: {game}")

            # stop running game
            if self.running and self.active:
                await self.games[self.active].stop()

            self.active = game
            self.running = True
            await self.games[game].start(params or {})

        self._publish_state()

    async def stop(self):
        async with self._lock:
            if self.running and self.active:
                await self.games[self.active].stop()
            self.running = False
            self.active = None

        self.mqtt.publish("mona/buttons/all/cmd", {"type": "stop", "clear": True})
        self._publish_state()

    async def on_button_pressed(self, btn_id: str):
        async with self._lock:
            if not self.running or not self.active:
                return
            game = self.games[self.active]
        await game.on_button_pressed(btn_id)
        self._publish_state()

    def list_games(self):
        return sorted(self.games.keys())

    def status(self) -> dict:
        base = {"running": self.running, "game": self.active or "idle"}
        if self.running and self.active:
            try:
                base |= self.games[self.active].status()
            except Exception:
                pass
        return base

    def _publish_state(self):
        try:
            self.mqtt.publish("mona/game/state", self.status(), retain=False)
        except Exception:
            pass
