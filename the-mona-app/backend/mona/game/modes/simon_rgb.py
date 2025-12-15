from .base import GameMode

class SimonRGB(GameMode):
    name = "SimonRGB"
    def __init__(self, mqtt, audio, devices: list[str]):
        self.mqtt = mqtt
        self.audio = audio
        self.devices = devices

    async def start(self): pass
    async def handle_input(self, event): pass
    async def tick(self): pass
    async def stop(self): pass
    def get_ui_state(self) -> dict: return {"mode": self.name}
