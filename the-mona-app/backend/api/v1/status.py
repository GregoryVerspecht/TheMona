from fastapi import APIRouter, Depends
from api.deps import get_engine

router = APIRouter()

@router.get("/status")
async def status(engine = Depends(get_engine)):
    return engine.get_status()
