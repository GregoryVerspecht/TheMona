from pydantic import BaseModel
from typing import Any

class GameStartIn(BaseModel):
    mode: str | None = None
    params: dict[str, Any] | None = None
