from pydantic import BaseModel, Field

class ButtonStatus(BaseModel):
    online: bool
    fw: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    mac: str | None = None

class Heartbeat(BaseModel):
    ts: int

class ButtonEvent(BaseModel):
    type: str  # e.g. "press"
    color: str | None = None
    ts: int | None = None

class CmdRgb(BaseModel):
    color: str
    mode: str = "solid"   # solid|pulse
    duration_ms: int = 500

class CmdFlash(BaseModel):
    color: str
    times: int = 3
    period_ms: int = 200
