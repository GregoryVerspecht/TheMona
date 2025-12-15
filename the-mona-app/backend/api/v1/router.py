from fastapi import APIRouter
from . import status, buttons, game, audio

api_router = APIRouter()
api_router.include_router(status.router, tags=["status"])
api_router.include_router(buttons.router, tags=["buttons"])
api_router.include_router(game.router, tags=["game"])
api_router.include_router(audio.router, tags=["audio"])
