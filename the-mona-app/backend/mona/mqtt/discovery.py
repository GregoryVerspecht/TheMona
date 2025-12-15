import time

class DeviceRegistry:
    def __init__(self, heartbeat_timeout: int = 45):
        self._hb_timeout = heartbeat_timeout
        self._devices: dict[str, dict] = {}  # id -> {status, last_hb, online}

    def apply_status(self, device_id: str, status: dict):
        entry = self._devices.setdefault(device_id, {})
        entry["status"] = status
        # online veld zit ook in status, maar we bepalen uiteindelijk via hb
        entry.setdefault("last_hb", int(time.time()))
        entry["online"] = True

    def heartbeat(self, device_id: str, ts: int | None = None):
        entry = self._devices.setdefault(device_id, {})
        entry["last_hb"] = ts or int(time.time())
        entry["online"] = True

    def mark_offline_if_stale(self):
        now = int(time.time())
        for dev, entry in self._devices.items():
            last = entry.get("last_hb", 0)
            entry["online"] = (now - last) <= self._hb_timeout

    def list_devices(self) -> list[dict]:
        return [
            {"id": dev, "online": e.get("online", False), "status": e.get("status", {})}
            for dev, e in self._devices.items()
        ]
