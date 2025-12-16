from fastapi import FastAPI
from api.v1.router import api_router

from mona.services.button_registry import ButtonRegistry
from mona.services.mqtt_paho import PahoMqttService, MqttConfig
from mona.audio.service import AudioService          
from mona.engine.engine import GameEngine            

def create_app(settings) -> FastAPI:
    app = FastAPI(title="The Mona API")

    # --- build services ---
    registry = ButtonRegistry()

    mqtt_cfg = MqttConfig(
        host=settings.mqtt.host,
        port=settings.mqtt.port,
        username=getattr(settings.mqtt, "username", None),
        password=getattr(settings.mqtt, "password", None),
        client_id="mona-api",
    )
    mqtt = PahoMqttService(mqtt_cfg)
    mqtt.set_handlers(on_event=registry.upsert_event, on_state=registry.upsert_state)

    audio = AudioService(settings.audio)   # of settings, cfg, ...
    engine = GameEngine(settings, mqtt, audio, registry)  # hoe jij het wired

    # --- expose to deps via app.state ---
    app.state.cfg = settings
    app.state.registry = registry
    app.state.mqtt = mqtt
    app.state.audio = audio
    app.state.engine = engine

    @app.on_event("startup")
    async def _startup():
        mqtt.start()
        await audio.start()      # als async
        await engine.start()     # optioneel, als je zoiets hebt

    @app.on_event("shutdown")
    async def _shutdown():
        await engine.stop()      # optioneel
        await audio.stop()
        mqtt.stop()

    app.include_router(api_router, prefix="/api/v1")
    return app
