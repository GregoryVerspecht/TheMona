from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from api.deps import get_ledstrip

router = APIRouter(prefix="/ledstrip", tags=["ledstrip"])


class FillIn(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    brightness: int | None = Field(default=None, ge=0, le=255)


class PixelIn(BaseModel):
    index: int = Field(ge=0)
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)


class BrightnessIn(BaseModel):
    brightness: int = Field(ge=0, le=255)


class AnimateIn(BaseModel):
    type: str           # "rainbow" | "pulse"
    r: int = Field(default=0, ge=0, le=255)
    g: int = Field(default=255, ge=0, le=255)
    b: int = Field(default=0, ge=0, le=255)
    speed_ms: int = Field(default=20, ge=5, le=500)


class StatusIn(BaseModel):
    status: str         # "idle" | "running" | "success" | "fail" | "off"


@router.get("/status")
def ledstrip_status(strip=Depends(get_ledstrip)):
    return strip.status()


@router.post("/fill")
def ledstrip_fill(body: FillIn, strip=Depends(get_ledstrip)):
    strip.fill(body.r, body.g, body.b, body.brightness)
    return {"ok": True}


@router.post("/pixel")
def ledstrip_pixel(body: PixelIn, strip=Depends(get_ledstrip)):
    strip.set_pixel(body.index, body.r, body.g, body.b)
    return {"ok": True}


@router.post("/brightness")
def ledstrip_brightness(body: BrightnessIn, strip=Depends(get_ledstrip)):
    strip.set_brightness(body.brightness)
    return {"ok": True}


@router.post("/off")
async def ledstrip_off(strip=Depends(get_ledstrip)):
    strip.off()
    return {"ok": True}


@router.post("/animate")
async def ledstrip_animate(body: AnimateIn, strip=Depends(get_ledstrip)):
    if body.type == "rainbow":
        strip.animate_rainbow(body.speed_ms)
    elif body.type == "pulse":
        strip.animate_pulse(body.r, body.g, body.b, body.speed_ms)
    return {"ok": True}


@router.post("/status-set")
async def ledstrip_set_status(body: StatusIn, strip=Depends(get_ledstrip)):
    mapping = {
        "idle":    strip.set_status_idle,
        "running": strip.set_status_running,
        "success": strip.set_status_success,
        "fail":    strip.set_status_fail,
        "off":     strip.set_status_off,
    }
    fn = mapping.get(body.status)
    if fn:
        fn()
    return {"ok": True, "status": body.status}
