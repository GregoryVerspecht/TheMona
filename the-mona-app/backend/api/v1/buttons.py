from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_mqtt, get_registry
from schemas.buttons import LedsSetIn, FillIn, FlashIn, StopIn

router = APIRouter(prefix="/buttons", tags=["buttons"])

# ---------- READ ----------
@router.get("")
async def list_buttons(reg=Depends(get_registry)):
    return {"buttons": reg.list()}

@router.get("/{btn_id}")
async def get_button(btn_id: str, reg=Depends(get_registry)):
    st = reg.get(btn_id)
    if not st:
        raise HTTPException(status_code=404, detail="Button not found")
    return st

# ---------- CONTROL (per device) ----------
@router.post("/{btn_id}/fill")
async def fill(btn_id: str, body: FillIn, mqtt=Depends(get_mqtt)):
    mqtt.publish(f"mona/buttons/{btn_id}/cmd", {
        "type": "fill",
        "brightness": body.brightness,
        "r": body.r, "g": body.g, "b": body.b,
    })
    return {"ok": True, "target": btn_id}

@router.post("/{btn_id}/leds")
async def leds_set(btn_id: str, body: LedsSetIn, mqtt=Depends(get_mqtt)):
    mqtt.publish(f"mona/buttons/{btn_id}/cmd", {
        "type": "leds_set",
        "brightness": body.brightness,
        "leds": [x.model_dump() for x in body.leds],
    })
    return {"ok": True, "target": btn_id}

@router.post("/{btn_id}/flash")
async def flash(btn_id: str, body: FlashIn, mqtt=Depends(get_mqtt)):
    payload = {
        "type": "flash",
        "brightness": body.brightness,
        "r": body.r, "g": body.g, "b": body.b,
        "interval_ms": body.interval_ms,
        "times": body.times,
    }
    if body.mask is not None:
        payload["mask"] = body.mask

    mqtt.publish(f"mona/buttons/{btn_id}/cmd", payload)
    return {"ok": True, "target": btn_id}

@router.post("/{btn_id}/stop")
async def stop(btn_id: str, body: StopIn, mqtt=Depends(get_mqtt)):
    mqtt.publish(f"mona/buttons/{btn_id}/cmd", {
        "type": "stop",
        "clear": body.clear,
    })
    return {"ok": True, "target": btn_id}

@router.post("/{btn_id}/request-state")
async def request_state(btn_id: str, mqtt=Depends(get_mqtt)):
    mqtt.publish(f"mona/buttons/{btn_id}/cmd", {"type": "request_state"})
    return {"ok": True, "target": btn_id}

# ---------- BROADCAST ----------
@router.post("/all/fill")
async def fill_all(body: FillIn, mqtt=Depends(get_mqtt)):
    mqtt.publish("mona/buttons/all/cmd", {
        "type": "fill",
        "brightness": body.brightness,
        "r": body.r, "g": body.g, "b": body.b,
    })
    return {"ok": True, "target": "all"}

@router.post("/all/flash")
async def flash_all(body: FlashIn, mqtt=Depends(get_mqtt)):
    payload = {
        "type": "flash",
        "brightness": body.brightness,
        "r": body.r, "g": body.g, "b": body.b,
        "interval_ms": body.interval_ms,
        "times": body.times,
    }
    if body.mask is not None:
        payload["mask"] = body.mask

    mqtt.publish("mona/buttons/all/cmd", payload)
    return {"ok": True, "target": "all"}

@router.post("/all/stop")
async def stop_all(body: StopIn, mqtt=Depends(get_mqtt)):
    mqtt.publish("mona/buttons/all/cmd", {"type": "stop", "clear": body.clear})
    return {"ok": True, "target": "all"}
