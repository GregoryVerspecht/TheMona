from __future__ import annotations
import asyncio
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable, Awaitable

from .base import GameBase

@dataclass
class ReactionConfig:
    min_delay_s: float = 1.5
    max_delay_s: float = 4.0
    reaction_timeout_s: float = 2.0
    rounds: int = 5

class ReactionGame(GameBase):
    key = "reaction"

    def __init__(
        self,
        mqtt,
        audio,
        registry,
        on_finished: Callable[[], Awaitable[None]],
        cfg: ReactionConfig | None = None,
    ):
        self.mqtt = mqtt
        self.audio = audio
        self.registry = registry
        self.on_finished = on_finished
        self.cfg = cfg or ReactionConfig()

        self.running = False
        self.state = "idle"
        self.round = 0
        self.target_id: Optional[str] = None
        self.score_ok = 0
        self.score_fail = 0

        self._lock = asyncio.Lock()
        self._main_task: Optional[asyncio.Task] = None
        self._timeout_task: Optional[asyncio.Task] = None

    def _all_off(self):
        self.mqtt.publish("mona/buttons/all/cmd", {"type": "stop", "clear": True})

    def _all_dim_blue(self):
        self.mqtt.publish("mona/buttons/all/cmd", {"type": "fill", "brightness": 80, "r": 0, "g": 0, "b": 40})

    def _show_target(self, btn_id: str):
        self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {"type": "fill", "brightness": 220, "r": 0, "g": 220, "b": 0})

    def _flash_red(self, btn_id: str | None):
        if btn_id:
            self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {"type": "flash", "brightness": 220, "r": 255, "g": 0, "b": 0, "interval_ms": 120, "times": 6})
        else:
            self.mqtt.publish("mona/buttons/all/cmd", {"type": "flash", "brightness": 200, "r": 255, "g": 0, "b": 0, "interval_ms": 120, "times": 6})

    def status(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "round": self.round,
            "target": self.target_id,
            "score_ok": self.score_ok,
            "score_fail": self.score_fail,
            "rounds_total": self.cfg.rounds,
        }

    async def start(self, params: Dict[str, Any] | None = None) -> None:
        async with self._lock:
            self.running = True
            self.state = "arming"
            self.round = 0
            self.target_id = None
            self.score_ok = 0
            self.score_fail = 0

            if params:
                # optioneel override
                self.cfg.rounds = int(params.get("rounds", self.cfg.rounds))
                self.cfg.reaction_timeout_s = float(params.get("reaction_timeout_s", self.cfg.reaction_timeout_s))

            self._all_off()
            self._all_dim_blue()

            if self._main_task:
                self._main_task.cancel()
            self._main_task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        async with self._lock:
            self.running = False
            self.state = "idle"
            self.target_id = None

            if self._timeout_task:
                self._timeout_task.cancel()
                self._timeout_task = None
            if self._main_task:
                self._main_task.cancel()
                self._main_task = None

        self._all_off()

    async def _run(self):
        await self.audio.play_sfx("success")
        await asyncio.sleep(0.6)

        while True:
            async with self._lock:
                if not self.running:
                    return
                if self.round >= self.cfg.rounds:
                    self.state = "done"

            await self.on_finished()
            return

            # WAIT_RANDOM
            async with self._lock:
                self.state = "wait_random"
                self.target_id = None

            await asyncio.sleep(random.uniform(self.cfg.min_delay_s, self.cfg.max_delay_s))

            async with self._lock:
                if not self.running:
                    return
                if self.state == "fail":
                    await self.on_finished()
                    return

                devices = self.registry.list_ids(connected_only=True)
                if not devices:
                    self.state = "fail"
                    self.score_fail += 1

            if self.state == "fail":
                await self.audio.play_sfx("fail")
                self._flash_red(None)
                await asyncio.sleep(0.4)
                await self.on_finished()
                return

            # SHOW_TARGET
            async with self._lock:
                self.state = "show_target"
                self.target_id = random.choice(devices)
                self.round += 1
                target = self.target_id

                self._all_off()
                self._show_target(target)

                if self._timeout_task:
                    self._timeout_task.cancel()
                self._timeout_task = asyncio.create_task(self._timeout_watch(round_no=self.round, target_id=target))

    async def _timeout_watch(self, round_no: int, target_id: str):
        try:
            await asyncio.sleep(self.cfg.reaction_timeout_s)
            async with self._lock:
                if not self.running:
                    return
                if self.state != "show_target":
                    return
                if self.round != round_no or self.target_id != target_id:
                    return
                self.state = "fail"
                self.score_fail += 1

            await self.audio.play_sfx("fail")
            self._flash_red(target_id)
            await asyncio.sleep(0.4)
            await self.on_finished()
        except asyncio.CancelledError:
            return

    async def on_button_pressed(self, btn_id: str) -> None:
        async with self._lock:
            if not self.running:
                return

            # false start
            if self.state == "wait_random":
                self.state = "fail"
                self.score_fail += 1
                fail_target = None

            elif self.state == "show_target":
                target = self.target_id
                if btn_id == target:
                    self.state = "success"
                    self.score_ok += 1
                    # stop timeout
                    if self._timeout_task:
                        self._timeout_task.cancel()
                        self._timeout_task = None
                    # feedback
                    self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {"type": "flash", "brightness": 220, "r": 255, "g": 255, "b": 255, "interval_ms": 80, "times": 4})
                    # back to ready look
                    self._all_dim_blue()
                    return
                else:
                    self.state = "fail"
                    self.score_fail += 1
                    fail_target = target
            else:
                return

        # fail path (outside lock)
        await self.audio.play_sfx("fail")
        self._flash_red(fail_target)
        await asyncio.sleep(0.4)
        await self.on_finished()
