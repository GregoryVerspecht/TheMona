from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, Optional

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

@dataclass
class ButtonState:
    id: str
    last_seen: datetime
    connected: bool = False

    last_event: Optional[str] = None
    last_press: Optional[datetime] = None

    brightness: Optional[int] = None
    flashing: Optional[bool] = None
    flash_interval_ms: Optional[int] = None
    rssi: Optional[int] = None
    ip: Optional[str] = None

class ButtonRegistry:
    def __init__(self) -> None:
        self._lock = RLock()
        self._buttons: Dict[str, ButtonState] = {}

    def upsert_event(self, btn_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            st = self._buttons.get(btn_id)
            if not st:
                st = ButtonState(id=btn_id, last_seen=now_utc())
                self._buttons[btn_id] = st

            st.last_seen = now_utc()
            ev = payload.get("event") or payload.get("status")
            st.last_event = ev

            if ev == "CONNECTED":
                st.connected = True

            if ev == "PRESSED":
                st.last_press = now_utc()

            if "ip" in payload:
                st.ip = str(payload.get("ip"))

    def upsert_state(self, btn_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            st = self._buttons.get(btn_id)
            if not st:
                st = ButtonState(id=btn_id, last_seen=now_utc())
                self._buttons[btn_id] = st

            st.last_seen = now_utc()
            st.connected = True

            if "brightness" in payload:
                st.brightness = int(payload["brightness"])
            if "flashing" in payload:
                st.flashing = bool(payload["flashing"])
            if "flash_interval_ms" in payload:
                st.flash_interval_ms = int(payload["flash_interval_ms"])
            if "rssi" in payload:
                st.rssi = int(payload["rssi"])
            if "ip" in payload:
                st.ip = str(payload["ip"])

    def list(self) -> list[dict]:
        with self._lock:
            return [self._to_dict(st) for st in self._buttons.values()]

    def get(self, btn_id: str) -> Optional[dict]:
        with self._lock:
            st = self._buttons.get(btn_id)
            return self._to_dict(st) if st else None

    def list_ids(self, connected_only: bool = True) -> list[str]:
        with self._lock:
            if not connected_only:
                return list(self._buttons.keys())
            return [k for k, st in self._buttons.items() if st.connected]

    def _to_dict(self, st: ButtonState) -> dict:
        d = asdict(st)
        d["last_seen"] = st.last_seen.isoformat()
        d["last_press"] = st.last_press.isoformat() if st.last_press else None
        return d
