from dataclasses import dataclass
from typing import Any

@dataclass
class Event:
    type: str
    payload: dict[str, Any] | None = None
