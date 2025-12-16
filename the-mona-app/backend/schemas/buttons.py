from pydantic import BaseModel, Field
from typing import List, Optional

class LedRGB(BaseModel):
    i: int = Field(ge=0, le=6)
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

class LedsSetIn(BaseModel):
    brightness: Optional[int] = Field(default=None, ge=0, le=255)
    leds: List[LedRGB] = Field(min_length=1, max_length=7)

class FillIn(BaseModel):
    brightness: Optional[int] = Field(default=None, ge=0, le=255)
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

class FlashIn(BaseModel):
    brightness: Optional[int] = Field(default=None, ge=0, le=255)
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    interval_ms: int = Field(default=120, ge=20, le=5000)
    times: int = Field(default=6, ge=1, le=100)
    mask: Optional[List[int]] = None

class StopIn(BaseModel):
    clear: bool = True
