import random
from .base import GameMode

class ReactionRace(GameMode):
    name = "ReactionRace"

    def __init__(self, mqtt, audio, devices: list[str]):
        self.mqtt = mqtt
        self.audio = audio
        self.devices = devices
        self.target: str | None = None
        self.running = False

    async def start(self):
        self.running = True
        self.target = random.choice(self.devices) if self.devices else None
        if self.target:
            self.mqtt.set_rgb(self.target, cmd=type("Cmd", (), {"model_dump": lambda s: {"color":"#00FF00","mode":"solid","duration_ms":2000}})())

    async def handle_input(self, event):
        if not self.running or not self.target: return
        if getattr(event, "button_id", None) == self.target:
            await self.audio.play_sfx("success")
            self.running = False

    async def tick(self):
        pass

    async def stop(self):
        self.running = False

    def get_ui_state(self) -> dict:
        return {"mode": self.name, "target": self.target, "running": self.running}
