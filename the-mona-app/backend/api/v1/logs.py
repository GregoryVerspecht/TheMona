import asyncio
import json
from fastapi import APIRouter, Query

router = APIRouter(prefix="/logs", tags=["logs"])


async def _journalctl(unit: str, lines: int) -> list[dict]:
    proc = await asyncio.create_subprocess_exec(
        "journalctl", "-u", unit, "-n", str(lines), "--no-pager", "--output=json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)

    entries = []
    for line in stdout.decode().splitlines():
        try:
            raw = json.loads(line)
            msg = raw.get("MESSAGE", "")
            ts = raw.get("__REALTIME_TIMESTAMP", "")
            # Try to parse JSON log lines from the Python app
            try:
                parsed = json.loads(msg)
                level = parsed.get("levelname", "INFO")
                message = parsed.get("message") or parsed.get("msg", msg)
            except (json.JSONDecodeError, TypeError):
                level = "SYS"
                message = msg

            entries.append({
                "ts": int(ts) // 1000 if ts else 0,  # microseconds → milliseconds
                "level": level,
                "message": message,
            })
        except (json.JSONDecodeError, ValueError):
            continue

    return entries


@router.get("")
async def get_logs(
    lines: int = Query(default=100, ge=1, le=500),
    unit: str = Query(default="the-mona"),
):
    entries = await _journalctl(unit, lines)
    return {"logs": entries}
