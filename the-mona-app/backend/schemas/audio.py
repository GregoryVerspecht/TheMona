from pydantic import BaseModel, Field

class SfxPlayIn(BaseModel):
    name: str = Field(..., examples=["success"])

class SfxStopIn(BaseModel):
    name: str | None = Field(None, description="laat leeg om alles te stoppen")
    fade_ms: int = Field(200, ge=0, le=10000)

class VolumeIn(BaseModel):
    volume: int = Field(..., ge=0, le=100)
