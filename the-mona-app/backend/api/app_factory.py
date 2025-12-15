from fastapi import FastAPI
from api.v1.router import api_router

def create_app(cfg, engine, mqtt, audio) -> FastAPI:
    app = FastAPI(title="The Mona API")

    # dependency wiring: stop je objects in app.state
    app.state.cfg = cfg
    app.state.engine = engine
    app.state.mqtt = mqtt
    app.state.audio = audio

    app.include_router(api_router, prefix="/api/v1")
    return app
