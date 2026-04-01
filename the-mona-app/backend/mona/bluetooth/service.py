from __future__ import annotations
import asyncio
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BtDevice:
    mac: str
    name: str
    connected: bool
    trusted: bool
    audio_sink: bool


@dataclass
class BtStatus:
    adapter_available: bool
    adapter_powered: bool
    devices: list[BtDevice] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "adapter_available": self.adapter_available,
            "adapter_powered": self.adapter_powered,
            "devices": [
                {
                    "mac": d.mac,
                    "name": d.name,
                    "connected": d.connected,
                    "trusted": d.trusted,
                    "audio_sink": d.audio_sink,
                }
                for d in self.devices
            ],
        }


class BluetoothService:
    async def status(self) -> BtStatus:
        adapter = await self._adapter_info()
        if not adapter["available"]:
            return BtStatus(adapter_available=False, adapter_powered=False)

        devices = await self._connected_devices()
        return BtStatus(
            adapter_available=True,
            adapter_powered=adapter["powered"],
            devices=devices,
        )

    async def trusted_devices(self) -> list[BtDevice]:
        """All paired/trusted devices, connected or not."""
        try:
            out = await self._run("bluetoothctl", "devices", "Trusted")
            return [await self._device_detail(m, n) for m, n in self._parse_device_list(out)]
        except Exception:
            return []

    async def connect(self, mac: str) -> bool:
        try:
            out = await self._run("bluetoothctl", "connect", mac)
            return "Connection successful" in out
        except Exception:
            return False

    async def disconnect(self, mac: str) -> bool:
        try:
            out = await self._run("bluetoothctl", "disconnect", mac)
            return "Successful disconnected" in out
        except Exception:
            return False

    # ── helpers ────────────────────────────────────────────────────────────────

    async def _run(self, *args: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        return stdout.decode()

    async def _adapter_info(self) -> dict:
        try:
            out = await self._run("bluetoothctl", "show")
            return {
                "available": True,
                "powered": "Powered: yes" in out,
            }
        except Exception:
            return {"available": False, "powered": False}

    async def _connected_devices(self) -> list[BtDevice]:
        try:
            out = await self._run("bluetoothctl", "devices", "Connected")
            return [await self._device_detail(m, n) for m, n in self._parse_device_list(out)]
        except Exception:
            return []

    async def _device_detail(self, mac: str, fallback_name: str) -> BtDevice:
        try:
            out = await self._run("bluetoothctl", "info", mac)
            name_m = re.search(r"Name:\s+(.+)", out)
            # A2DP Sink UUID = 0000110b-..., indicates audio output device
            audio_sink = "0000110b" in out.lower()
            return BtDevice(
                mac=mac,
                name=name_m.group(1).strip() if name_m else fallback_name,
                connected="Connected: yes" in out,
                trusted="Trusted: yes" in out,
                audio_sink=audio_sink,
            )
        except Exception:
            return BtDevice(mac=mac, name=fallback_name, connected=False, trusted=False, audio_sink=False)

    @staticmethod
    def _parse_device_list(output: str) -> list[tuple[str, str]]:
        results = []
        for line in output.splitlines():
            m = re.match(r"Device\s+([0-9A-Fa-f:]{17})\s+(.*)", line.strip())
            if m:
                results.append((m.group(1), m.group(2).strip()))
        return results
