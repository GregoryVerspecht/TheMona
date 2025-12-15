from fastapi import APIRouter, Depends
from api.deps import get_engine, get_cfg
from schemas.game import GameStartIn

router = APIRouter(prefix="/game")

@router.post("/start")
async def start_game(body: GameStartIn, cfg = Depends(get_cfg), engine = Depends(get_engine)):
    mode = body.mode or cfg.game.default_mode
    await engine.start_mode(mode, body.params)
    return engine.get_status()

@router.post("/stop")
async def stop_game(engine = Depends(get_engine)):
    await engine.stop_mode()
    return engine.get_status()
