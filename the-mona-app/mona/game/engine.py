import asyncio
import logging
from .state import GameState
from .events import ButtonPressed
from .modes.reaction_race import ReactionRace
from .modes.simon_rgb import SimonRGB

log = logging.getLogger(__name__)

class GameEngine:
    def __init__(self, cfg, mqtt, audio):
        self.cfg = cfg
        self.mqtt = mqtt
        self.audio = audio
        self.state = GameState.IDLE
        self.event_q: asyncio.Queue = asyncio.Queue()
        self.mode = None
        # hook mqtt → engine
        mqtt.on_button_event = self._on_button_event

    async def start(self):
        self.state = GameState.IDLE
        self._tick_task = asyncio.create_task(self._loop())

    async def stop(self):
        if hasattr(self, "_tick_task"):
            self._tick_task.cancel()
        if self.mode:
            await self.mode.stop()
            self.mode = None
        self.state = GameState.IDLE

    async def _loop(self):
        tick = self.cfg.game.tick_ms / 1000
        while True:
            try:
                # tick
                if self.mode:
                    await self.mode.tick()
                # events
                while not self.event_q.empty():
                    ev = await self.event_q.get()
                    if self.mode:
                        await self.mode.handle_input(ev)
                await asyncio.sleep(tick)
            except asyncio.CancelledError:
                break
            except Exception:
                log.exception("engine loop error")

    def _on_button_event(self, btn_id: str, ev):
        self.event_q.put_nowait(ButtonPressed(button_id=btn_id, color=ev.color, ts=ev.ts))

    def get_status(self):
        return {"state": self.state.value, "mode": getattr(self.mode, "name", None)}

    async def start_mode(self, name: str, params: dict | None = None):
        if self.mode:
            await self.mode.stop()
        devices = [d["id"] for d in self.mqtt.list_devices() if d["online"]]
        if name == "ReactionRace":
            self.mode = ReactionRace(self.mqtt, self.audio, devices)
        elif name == "SimonRGB":
            self.mode = SimonRGB(self.mqtt, self.audio, devices)
        else:
            raise ValueError(f"Unknown mode {name}")
        await self.mode.start()
        self.state = GameState.RUNNING

    async def stop_mode(self):
        if self.mode:
            await self.mode.stop()
            self.mode = None
        self.state = GameState.IDLE
