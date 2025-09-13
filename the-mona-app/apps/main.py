import asyncio
import signal
import uvicorn

from mona.config.loader import settings
from mona.util.logging import setup_logging
from mona.mqtt.client import MqttClient
from mona.game.engine import GameEngine
from mona.audio.service import AudioService
from mona.web.api import create_app


async def main():
    setup_logging(settings.app.log_level)
    mqtt = MqttClient(settings)
    audio = AudioService(settings)
    engine = GameEngine(settings, mqtt, audio)

    await mqtt.start()
    await audio.start()
    await engine.start()

    app = create_app(settings, engine, mqtt, audio)
    server = uvicorn.Server(
        uvicorn.Config(app, host=settings.web.host, port=settings.web.port, loop="asyncio")
    )

    stop_event = asyncio.Event()

    def _stop():
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _stop)

    web_task = asyncio.create_task(server.serve())
    await stop_event.wait()

    await engine.stop()
    await mqtt.stop()
    await audio.stop()
    web_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
