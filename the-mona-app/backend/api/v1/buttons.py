from fastapi import APIRouter, Depends
from api.deps import get_mqtt
from mona.mqtt.models import CmdRgb, CmdFlash

router = APIRouter(prefix="/buttons")

@router.get("")
async def list_buttons(mqtt = Depends(get_mqtt)):
    return mqtt.list_devices()

@router.post("/{btn_id}/rgb")
async def set_rgb(btn_id: str, body: CmdRgb, mqtt = Depends(get_mqtt)):
    mqtt.set_rgb(btn_id, body)
    return {"ok": True}

@router.post("/{btn_id}/flash")
async def flash(btn_id: str, body: CmdFlash, mqtt = Depends(get_mqtt)):
    mqtt.flash(btn_id, body)
    return {"ok": True}

@router.post("/all/rgb")
async def set_all_rgb(body: CmdRgb, mqtt = Depends(get_mqtt)):
    mqtt.set_rgb_all(body)
    return {"ok": True}
