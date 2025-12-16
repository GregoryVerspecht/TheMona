from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict, Optional
from api.deps import get_engine

router = APIRouter(prefix="/game", tags=["game"])

class GameStartIn(BaseModel):
    game: str
    params: Optional[Dict[str, Any]] = None

@router.get("/games")
async def games(engine=Depends(get_engine)):
    return {"games": engine.list_games()}

@router.get("/status")
async def status(engine=Depends(get_engine)):
    return engine.status()

@router.post("/start")
async def start(body: GameStartIn, engine=Depends(get_engine)):
    await engine.start(body.game, body.params or {})
    return {"ok": True}

@router.post("/stop")
async def stop(engine=Depends(get_engine)):
    await engine.stop()
    return {"ok": True}
