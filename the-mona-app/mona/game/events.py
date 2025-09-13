from dataclasses import dataclass

@dataclass
class ButtonPressed:
    button_id: str
    color: str | None = None
    ts: int | None = None
