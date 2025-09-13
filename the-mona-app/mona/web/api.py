from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mona.mqtt.models import CmdRgb, CmdFlash

from pydantic import BaseModel, Field
import os  # voor _key helper

def _key(name: str) -> str:
    base, _ = os.path.splitext(name)
    return base.strip().lower()

def create_app(cfg, engine, mqtt, audio) -> FastAPI:
    app = FastAPI(title="The Mona")

    templates = Jinja2Templates(directory="mona/web/templates")
    app.mount("/static", StaticFiles(directory="mona/web/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse("home.html", {"request": request, "status": engine.get_status()})

    @app.get("/modes", response_class=HTMLResponse)
    async def modes(request: Request):
        return templates.TemplateResponse("modes.html", {"request": request, "modes": ["ReactionRace","SimonRGB"], "status": engine.get_status()})

    @app.get("/test", response_class=HTMLResponse)
    async def test(request: Request):
        return templates.TemplateResponse("test.html", {"request": request, "devices": mqtt.list_devices()})

    @app.get("/audio", response_class=HTMLResponse)
    async def audio_page(request: Request):
        ok = await audio.is_connected()
        return templates.TemplateResponse("audio.html", {"request": request, "connected": ok})

    @app.get("/health", response_class=HTMLResponse)
    async def health_page(request: Request):
        return templates.TemplateResponse("health.html", {"request": request})

    # REST API
    @app.get("/api/status")
    async def api_status():
        return engine.get_status()

    @app.get("/api/buttons")
    async def api_buttons():
        return mqtt.list_devices()

    @app.post("/api/game/start")
    async def api_game_start(body: dict):
        mode = body.get("mode") or cfg.game.default_mode
        await engine.start_mode(mode, body.get("params"))
        return engine.get_status()

    @app.post("/api/game/stop")
    async def api_game_stop():
        await engine.stop_mode()
        return engine.get_status()

    @app.post("/api/buttons/{btn_id}/rgb")
    async def api_btn_rgb(btn_id: str, body: CmdRgb):
        mqtt.set_rgb(btn_id, body)
        return {"ok": True}

    @app.post("/api/buttons/{btn_id}/flash")
    async def api_btn_flash(btn_id: str, body: CmdFlash):
        mqtt.flash(btn_id, body)
        return {"ok": True}

    @app.post("/api/buttons/all/rgb")
    async def api_all_rgb(body: CmdRgb):
        mqtt.set_rgb_all(body)
        return {"ok": True}

    @app.post("/api/audio/test-tone")
    async def api_audio_test():
        await audio.test_tone()
        return {"ok": True}

    @app.post("/api/audio/play")
    async def api_audio_play(body: dict):
        await audio.play_sfx(body.get("name", "success"))
        return {"ok": True}
    
        # ---------- Audio API: extra ----------
    class SfxPlayIn(BaseModel):
        name: str = Field(..., example="success")

    class SfxStopIn(BaseModel):
        name: str | None = Field(None, description="laat leeg om alles te stoppen")
        fade_ms: int = Field(200, ge=0, le=10000)

    class VolumeIn(BaseModel):
        volume: int = Field(..., ge=0, le=100, example=75)

    @app.get("/api/audio/list")
    async def api_audio_list():
        return {"sounds": await audio.list_sounds()}

    @app.get("/api/audio/status")
    async def api_audio_status():
        return await audio.status()

    @app.get("/api/audio/volume")
    async def api_audio_volume_get():
        return {"volume": await audio.get_volume()}

    @app.post("/api/audio/volume")
    async def api_audio_volume_set(body: VolumeIn):
        await audio.set_volume(body.volume)
        return {"ok": True, "volume": body.volume}

    @app.post("/api/audio/sfx/play")
    async def api_audio_sfx_play(body: SfxPlayIn):
        await audio.play_sfx(_key(body.name))
        return {"ok": True, "played": _key(body.name)}

    @app.post("/api/audio/sfx/stop")
    async def api_audio_sfx_stop(body: SfxStopIn):
        await audio.stop_sfx(_key(body.name) if body.name else None, fade_ms=body.fade_ms)
        return {
            "ok": True,
            "stopped": "all" if body.name is None else _key(body.name),
            "fade_ms": body.fade_ms
        }


    return app
