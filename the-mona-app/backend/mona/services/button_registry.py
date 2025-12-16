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
    last_event: Optional[str] = None
    last_press: Optional[datetime] = None
    connected: bool = False

    # state snapshot fields (coming from /state messages)
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

            # optional fields
            if "ip" in payload:
                st.ip = str(payload.get("ip"))

    def upsert_state(self, btn_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            st = self._buttons.get(btn_id)
            if not st:
                st = ButtonState(id=btn_id, last_seen=now_utc())
                self._buttons[btn_id] = st

            st.last_seen = now_utc()
            st.connected = True  # state ontvangen => device leeft

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

    def mark_disconnected_if_stale(self, stale_seconds: int = 30) -> None:
        """Optioneel: periodiek stale devices als disconnected markeren."""
        cutoff = now_utc().timestamp() - stale_seconds
        with self._lock:
            for st in self._buttons.values():
                if st.last_seen.timestamp() < cutoff:
                    st.connected = False

    def list(self) -> list[dict]:
        with self._lock:
            return [self._to_dict(st) for st in self._buttons.values()]

    def get(self, btn_id: str) -> Optional[dict]:
        with self._lock:
            st = self._buttons.get(btn_id)
            return self._to_dict(st) if st else None

    def _to_dict(self, st: ButtonState) -> dict:
        d = asdict(st)
        # datetime → iso string
        d["last_seen"] = st.last_seen.isoformat()
        d["last_press"] = st.last_press.isoformat() if st.last_press else None
        return d
