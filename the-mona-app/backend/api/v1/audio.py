import os
from fastapi import APIRouter, Depends
from api.deps import get_audio
from schemas.audio import SfxPlayIn, SfxStopIn, VolumeIn

router = APIRouter(prefix="/audio")

def _key(name: str) -> str:
    base, _ = os.path.splitext(name)
    return base.strip().lower()

@router.get("/list")
async def list_sounds(audio = Depends(get_audio)):
    return {"sounds": await audio.list_sounds()}

@router.get("/status")
async def audio_status(audio = Depends(get_audio)):
    return await audio.status()

@router.get("/volume")
async def get_volume(audio = Depends(get_audio)):
    return {"volume": await audio.get_volume()}

@router.post("/volume")
async def set_volume(body: VolumeIn, audio = Depends(get_audio)):
    await audio.set_volume(body.volume)
    return {"ok": True, "volume": body.volume}

# router
@router.post("/sfx/play")
async def play_sfx(body: SfxPlayIn, audio = Depends(get_audio)):
    played = await audio.play_sfx(body.name)
    return {"ok": True, "played": played}


@router.post("/sfx/stop")
async def stop_sfx(body: SfxStopIn, audio = Depends(get_audio)):
    await audio.stop_sfx(_key(body.name) if body.name else None, fade_ms=body.fade_ms)
    return {"ok": True, "fade_ms": body.fade_ms}
