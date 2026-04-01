from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_bluetooth

router = APIRouter(prefix="/bluetooth", tags=["bluetooth"])


@router.get("/status")
async def bt_status(bt=Depends(get_bluetooth)):
    status = await bt.status()
    return status.to_dict()


@router.get("/devices")
async def bt_devices(bt=Depends(get_bluetooth)):
    devices = await bt.trusted_devices()
    return {"devices": [{"mac": d.mac, "name": d.name, "connected": d.connected, "trusted": d.trusted, "audio_sink": d.audio_sink} for d in devices]}


@router.post("/connect/{mac}")
async def bt_connect(mac: str, bt=Depends(get_bluetooth)):
    ok = await bt.connect(mac)
    if not ok:
        raise HTTPException(status_code=500, detail=f"Could not connect to {mac}")
    return {"ok": True, "mac": mac}


@router.post("/disconnect/{mac}")
async def bt_disconnect(mac: str, bt=Depends(get_bluetooth)):
    ok = await bt.disconnect(mac)
    if not ok:
        raise HTTPException(status_code=500, detail=f"Could not disconnect {mac}")
    return {"ok": True, "mac": mac}
