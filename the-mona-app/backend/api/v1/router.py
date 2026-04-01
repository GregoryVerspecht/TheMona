from fastapi import APIRouter
from . import status, buttons, game, audio
from api.v1.buttons import router as buttons_router
from api.v1.game import router as game_router
from api.v1.bluetooth import router as bluetooth_router

api_router = APIRouter()
api_router.include_router(status.router, tags=["status"])
api_router.include_router(game.router, tags=["game"])
api_router.include_router(audio.router, tags=["audio"])
api_router.include_router(buttons_router)
api_router.include_router(game_router)
api_router.include_router(bluetooth_router)