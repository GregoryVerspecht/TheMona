# apps/main.py
import asyncio
import os
import signal
import uvicorn

from mona.config.loader import settings
from mona.util.logging import setup_logging
from mona.mqtt.client import MqttClient
from mona.engine.engine import GameEngine
from mona.audio.service import AudioService
from api.app_factory import create_app

async def main():
    setup_logging(settings.app.log_level)
    mqtt = MqttClient(settings)
    audio = AudioService(settings)
    engine = GameEngine(settings, mqtt, audio)

    await mqtt.start()
    await audio.start()
    await engine.start(GameEngine.GameMode.IDLE)

    app = create_app(settings)
   
    await audio.set_volume(20)
    await audio.play_sfx("sea_shanty_2",)  # startup sound
    server = uvicorn.Server(
        uvicorn.Config(app, host=settings.web.host, port=settings.web.port, loop="asyncio")
    )

    stop_event = asyncio.Event()

    # Cross-platform shutdown:
    if os.name != "nt":
        # Unix: netjes via add_signal_handler
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
    else:
        # Windows: fallback via standaard signal.signal + thread-safe set
        def _win_stop(*_args):
            # mag vanuit signal handler: zet event thread-safe
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(stop_event.set)
            except RuntimeError:
                stop_event.set()
        signal.signal(signal.SIGINT, _win_stop)
        # SIGBREAK bestaat niet altijd, dus conditioneel
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, _win_stop)

    web_task = asyncio.create_task(server.serve())

    try:
        await stop_event.wait()  # wacht op Ctrl+C / stop
    except KeyboardInterrupt:
        pass
    finally:
        # graceful shutdown
        await engine.stop()
        await mqtt.stop()
        await audio.stop()
        # uvicorn stoppen
        if not web_task.done():
            web_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await web_task


if __name__ == "__main__":
    import contextlib
    asyncio.run(main())
