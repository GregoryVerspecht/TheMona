from __future__ import annotations
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable, Awaitable

from .base import GameBase

@dataclass
class ReactionConfig:
    min_delay_s: float = 1.5
    max_delay_s: float = 4.0
    reaction_timeout_s: float = 2.0
    rounds: int = 5
    celebration_s: float = 4.0  # rainbow na game over

class ReactionGame(GameBase):
    key = "reaction"

    def __init__(
        self,
        mqtt,
        audio,
        registry,
        on_finished: Callable[[], Awaitable[None]],
        ledstrip=None,
        cfg: ReactionConfig | None = None,
    ):
        self.mqtt = mqtt
        self.audio = audio
        self.registry = registry
        self.ledstrip = ledstrip
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
        self._round_done: Optional[asyncio.Event] = None

    # ── LED helpers ────────────────────────────────────────────────────────────

    def _all_off(self):
        self.mqtt.publish("mona/buttons/all/cmd", {"type": "stop", "clear": True})

    def _all_dim_blue(self):
        self.mqtt.publish("mona/buttons/all/cmd", {"type": "fill", "brightness": 80, "r": 0, "g": 0, "b": 40})
        if self.ledstrip:
            self.ledstrip.set_status_idle()

    def _show_target(self, btn_id: str):
        self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {"type": "fill", "brightness": 220, "r": 0, "g": 220, "b": 0})
        if self.ledstrip:
            self.ledstrip.set_status_running()

    def _flash_success(self, btn_id: str):
        # Correcte knop: wit flitsen
        self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {
            "type": "flash", "brightness": 220,
            "r": 255, "g": 255, "b": 255,
            "interval_ms": 80, "times": 4,
        })
        # Alle andere knoppen: kort groen
        self.mqtt.publish("mona/buttons/all/cmd", {
            "type": "fill", "brightness": 120, "r": 0, "g": 200, "b": 0,
        })
        if self.ledstrip:
            self.ledstrip.set_status_success()

    def _flash_red(self, btn_id: str | None):
        if btn_id:
            self.mqtt.publish(f"mona/buttons/{btn_id}/cmd", {
                "type": "flash", "brightness": 220,
                "r": 255, "g": 0, "b": 0, "interval_ms": 120, "times": 6,
            })
        else:
            self.mqtt.publish("mona/buttons/all/cmd", {
                "type": "flash", "brightness": 200,
                "r": 255, "g": 0, "b": 0, "interval_ms": 120, "times": 6,
            })
        if self.ledstrip:
            self.ledstrip.set_status_fail()

    # ── Public API ─────────────────────────────────────────────────────────────

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
                self.cfg.rounds = int(params.get("rounds", self.cfg.rounds))
                self.cfg.reaction_timeout_s = float(params.get("reaction_timeout_s", self.cfg.reaction_timeout_s))
                self.cfg.min_delay_s = float(params.get("min_delay_s", self.cfg.min_delay_s))
                self.cfg.max_delay_s = float(params.get("max_delay_s", self.cfg.max_delay_s))
                self.cfg.celebration_s = float(params.get("celebration_s", self.cfg.celebration_s))

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
            if self._round_done:
                self._round_done.set()

        self._all_off()

    # ── Game loop ──────────────────────────────────────────────────────────────

    async def _run(self):
        await asyncio.sleep(0.6)

        while True:
            # Check game done
            async with self._lock:
                if not self.running:
                    return
                if self.round >= self.cfg.rounds:
                    self.state = "done"

            if self.state == "done":
                await self._celebrate()
                await self.on_finished()
                return

            # WAIT_RANDOM
            async with self._lock:
                self.state = "wait_random"
                self.target_id = None

            try:
                await asyncio.sleep(random.uniform(self.cfg.min_delay_s, self.cfg.max_delay_s))
            except asyncio.CancelledError:
                return

            # Check for false start
            async with self._lock:
                if not self.running:
                    return
                player_failed = (self.state == "fail")
                if not player_failed:
                    devices = self.registry.list_ids(connected_only=True)
                    if not devices:
                        self.state = "fail"
                        self.score_fail += 1

            if self.state == "fail":
                if not player_failed:
                    await self.audio.play_sfx("fail")
                    self._flash_red(None)
                    await asyncio.sleep(0.8)
                    self._all_dim_blue()
                continue

            # SHOW_TARGET
            self._round_done = asyncio.Event()
            async with self._lock:
                self.state = "show_target"
                self.target_id = random.choice(devices)
                self.round += 1
                target = self.target_id

                self._all_off()
                self._show_target(target)

                if self._timeout_task:
                    self._timeout_task.cancel()
                self._timeout_task = asyncio.create_task(
                    self._timeout_watch(round_no=self.round, target_id=target)
                )

            try:
                await self._round_done.wait()
            except asyncio.CancelledError:
                return

    async def _celebrate(self):
        """Eindanimatie: rainbow op strip + success sound."""
        if self.ledstrip:
            self.ledstrip.animate_rainbow(speed_ms=12)
        self.mqtt.publish("mona/buttons/all/cmd", {
            "type": "flash", "brightness": 220,
            "r": 0, "g": 255, "b": 100, "interval_ms": 120, "times": 8,
        })
        await self.audio.play_sfx("success")
        await asyncio.sleep(self.cfg.celebration_s)

    # ── Timeout watch ──────────────────────────────────────────────────────────

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
            await asyncio.sleep(0.8)
            self._all_dim_blue()
            if self._round_done:
                self._round_done.set()
        except asyncio.CancelledError:
            return

    # ── Button input ───────────────────────────────────────────────────────────

    async def on_button_pressed(self, btn_id: str) -> None:
        async with self._lock:
            if not self.running:
                return

            if self.state == "wait_random":
                # False start
                self.state = "fail"
                self.score_fail += 1
                fail_target = None

            elif self.state == "show_target":
                target = self.target_id
                if btn_id == target:
                    # Correct!
                    self.state = "success"
                    self.score_ok += 1
                    if self._timeout_task:
                        self._timeout_task.cancel()
                        self._timeout_task = None
                    self._flash_success(btn_id)
                    await self.audio.play_sfx("success")
                    await asyncio.sleep(0.6)
                    self._all_dim_blue()
                    if self._round_done:
                        self._round_done.set()
                    return
                else:
                    # Verkeerde knop
                    self.state = "fail"
                    self.score_fail += 1
                    fail_target = target
            else:
                return

        # Fail path (buiten lock)
        await self.audio.play_sfx("fail")
        self._flash_red(fail_target)
        await asyncio.sleep(0.8)
        self._all_dim_blue()
        if self._round_done:
            self._round_done.set()
