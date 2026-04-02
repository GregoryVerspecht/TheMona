from __future__ import annotations
import asyncio
import logging
import pathlib

log = logging.getLogger(__name__)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.v1.router import api_router
from mona.bluetooth.service import BluetoothService
from mona.ledstrip.service import LedStripService

from mona.services.button_registry import ButtonRegistry
from mona.services.mqtt_paho import PahoMqttService, MqttConfig
from mona.audio.service import AudioService
from mona.engine.engine import GameEngine
from mona.engine.games.reaction import ReactionGame, ReactionConfig

STARTUP_RAINBOW_SECS = 30   # hoe lang rainbow speelt na klaar-melding (instelbaar)

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
    audio = AudioService(getattr(settings, "audio", None))

    ledstrip = LedStripService()
    ledstrip.start()

    engine = GameEngine(mqtt=mqtt, audio=audio, registry=registry, ledstrip=ledstrip)

    async def on_reaction_finished():
        await engine.stop()

    reaction = ReactionGame(
        mqtt=mqtt,
        audio=audio,
        registry=registry,
        ledstrip=ledstrip,
        on_finished=on_reaction_finished,
        cfg=ReactionConfig(),
    )
    engine.register("reaction", reaction)

    # expose state
    app.state.registry = registry
    app.state.mqtt = mqtt
    app.state.audio = audio
    app.state.engine = engine
    app.state.bluetooth = BluetoothService()
    app.state.ledstrip = ledstrip

    # paho thread -> schedule into this loop
    def on_button_event(btn_id: str, payload: dict):
        registry.upsert_event(btn_id, payload)
        if payload.get("event") == "PRESSED":
            loop = app.state.loop
            loop.call_soon_threadsafe(
                asyncio.create_task,
                app.state.engine.on_button_pressed(btn_id)
            )

    def on_button_state(btn_id: str, payload: dict):
        registry.upsert_state(btn_id, payload)

    def on_game_cmd(payload: dict):
        """
        MQTT topic: mona/game/cmd
        Payload examples:
          {"type":"start","game":"reaction","params":{"rounds":5}}
          {"type":"stop"}
          {"type":"status_request"}
        """
        loop = app.state.loop
        t = payload.get("type")

        if t == "start":
            game = payload.get("game")
            params = payload.get("params") or {}
            loop.call_soon_threadsafe(asyncio.create_task, app.state.engine.start(game, params))
        elif t == "stop":
            loop.call_soon_threadsafe(asyncio.create_task, app.state.engine.stop())
        elif t == "status_request":
            # publish current state to mona/game/state
            loop.call_soon_threadsafe(app.state.engine._publish_state)
        elif t == "idle":
            loop.call_soon_threadsafe(asyncio.create_task, app.state.engine.set_idle())

    mqtt.set_handlers(
        on_button_event=on_button_event,
        on_button_state=on_button_state,
        on_game_cmd=on_game_cmd,
    )

    async def _startup_sequence():
        """Wacht tot audio klaar is, speel dan startup-sound + rainbow, daarna idle."""
        log.info("startup sequence: wachten op audio...")
        ledstrip.animate_pulse(255, 255, 255, speed_ms=5)  # wit pulseren tijdens opstart

        deadline = asyncio.get_event_loop().time() + STARTUP_RAINBOW_SECS
        while not audio._ready:
            if asyncio.get_event_loop().time() > deadline:
                log.warning("startup sequence: audio timeout, direct naar idle")
                ledstrip.set_status_idle()
                return
            await asyncio.sleep(0.5)

        remaining = deadline - asyncio.get_event_loop().time()
        log.info(f"startup sequence: audio klaar, rainbow voor {remaining:.0f}s")
        ledstrip.animate_rainbow(speed_ms=15)
        await audio.play_sfx("sea_shanty_2")
        await asyncio.sleep(max(0, remaining))
        await audio.stop_sfx(fade_ms=500)
        ledstrip.set_status_idle()
        log.info("startup sequence: klaar, idle")

    @app.on_event("startup")
    async def _startup():
        app.state.loop = asyncio.get_running_loop()
        mqtt.start()
        audio._volume = 25 / 100.0
        await audio.start()
        await engine.set_idle()
        asyncio.create_task(_startup_sequence())

    @app.on_event("shutdown")
    async def _shutdown():
        await engine.stop()
        await audio.stop()
        mqtt.stop()

    app.include_router(api_router, prefix="/api/v1")

    # Serve Astro frontend (built with `npm run build`)
    dist = pathlib.Path(__file__).parent.parent.parent / "frontend" / "dist"
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

    return app
