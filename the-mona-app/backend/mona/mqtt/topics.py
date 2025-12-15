def tp(prefix: str, *parts: str) -> str:
    return "/".join([prefix.strip("/"), *[p.strip("/") for p in parts]])

def buttons_status(prefix: str) -> str:
    return tp(prefix, "buttons", "+", "status")

def buttons_hb(prefix: str) -> str:
    return tp(prefix, "buttons", "+", "heartbeat")

def buttons_events(prefix: str) -> str:
    return tp(prefix, "buttons", "+", "events")

def cmd_rgb(prefix: str, btn_id: str) -> str:
    return tp(prefix, "buttons", btn_id, "cmd", "rgb")

def cmd_flash(prefix: str, btn_id: str) -> str:
    return tp(prefix, "buttons", btn_id, "cmd", "flash")

def cmd_rgb_all(prefix: str) -> str:
    return tp(prefix, "buttons", "all", "cmd", "rgb")

def app_status(prefix: str) -> str:
    return tp(prefix, "app", "status")
