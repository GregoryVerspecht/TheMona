from fastapi import FastAPI
from api.v1.router import api_router
from mona.services.button_registry import ButtonRegistry
from mona.services.mqtt_paho import PahoMqttService, MqttConfig

def create_app(settings) -> FastAPI:
    app = FastAPI(title="The Mona API")

    registry = ButtonRegistry()

    mqtt_cfg = MqttConfig(
        host=settings.mqtt.host,
        port=settings.mqtt.port,
        username=getattr(settings.mqtt, "username", None),
        password=getattr(settings.mqtt, "password", None),
        client_id="mona-api",
    )
    mqtt = PahoMqttService(mqtt_cfg)
    mqtt.set_handlers(
        on_event=registry.upsert_event,
        on_state=registry.upsert_state,
    )

    app.state.registry = registry
    app.state.mqtt = mqtt

    @app.on_event("startup")
    async def _startup():
        mqtt.start()

    @app.on_event("shutdown")
    async def _shutdown():
        mqtt.stop()

    app.include_router(api_router, prefix="/api/v1")
    return app
