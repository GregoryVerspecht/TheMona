# init-tree.ps1
# Maak projectstructuur voor "the-mona"

$root = "the-mona"

$dirs = @(
  "apps",
  "mona",
  "mona/config",
  "mona/util",
  "mona/mqtt",
  "mona/game",
  "mona/game/modes",
  "mona/audio",
  "mona/audio/sfx",
  "mona/web",
  "mona/web/templates",
  "mona/web/static",
  "deploy/systemd",
  "docker",
  "tests"
)

$files = @(
  "apps/main.py",
  "mona/__init__.py",
  "mona/config/__init__.py",
  "mona/config/loader.py",
  "mona/util/__init__.py",
  "mona/util/logging.py",
  "mona/util/events.py",
  "mona/mqtt/__init__.py",
  "mona/mqtt/client.py",
  "mona/mqtt/topics.py",
  "mona/mqtt/models.py",
  "mona/mqtt/discovery.py",
  "mona/game/__init__.py",
  "mona/game/engine.py",
  "mona/game/state.py",
  "mona/game/events.py",
  "mona/game/modes/__init__.py",
  "mona/game/modes/base.py",
  "mona/game/modes/reaction_race.py",
  "mona/game/modes/simon_rgb.py",
  "mona/audio/__init__.py",
  "mona/audio/service.py",
  "mona/audio/sfx/success.wav",  # lege placeholder
  "mona/audio/sfx/fail.wav",     # lege placeholder
  "mona/web/__init__.py",
  "mona/web/api.py",
  "mona/web/ws.py",
  "mona/web/templates/base.html",
  "mona/web/templates/home.html",
  "mona/web/templates/modes.html",
  "mona/web/templates/test.html",
  "mona/web/templates/audio.html",
  "mona/web/templates/health.html",
  "mona/web/static/app.js",
  "mona/web/static/styles.css",
  "config.yaml",
  ".env.example",
  "requirements.txt",
  "Makefile",
  "README.md",
  "deploy/systemd/mona.service",
  "docker/docker-compose.yml",
  "tests/test_topics.py",
  "tests/test_engine.py",
  "tests/test_models.py"
)

function New-DirSafe($path) {
  if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

function New-FileSafe($path) {
  if (-not (Test-Path $path)) {
    # Voor .wav placeholders: maak lege file (0 bytes)
    if ($path.ToLower().EndsWith(".wav")) {
      New-Item -ItemType File -Path $path | Out-Null
    } else {
      New-Item -ItemType File -Path $path -Value "" | Out-Null
    }
  }
}

# Maak root
New-DirSafe $root
Push-Location $root

# Maak directories
$dirs | ForEach-Object { New-DirSafe $_ }

# Maak files
$files | ForEach-Object { New-FileSafe $_ }

# Minimale inhoud voor een paar handige bestanden
# (Alleen als ze nog leeg zijn)
function Ensure-Content($path, $content) {
  if ((Get-Item $path).Length -eq 0) { Set-Content -Path $path -Value $content -Encoding UTF8 }
}

# __init__.py minimal
Get-ChildItem -Path . -Recurse -Include "__init__.py" | ForEach-Object {
  Ensure-Content $_.FullName "# makes this a package"
}

Ensure-Content "apps/main.py" @"
from mona.web.api import create_app

if __name__ == "__main__":
    # Startpunt voor dev; bv. uvicorn in code of via Makefile/docker
    print("The Mona starter")
"@

Ensure-Content "mona/config/loader.py" @"
from pathlib import Path
import yaml

def load_config(path: str = "config.yaml") -> dict:
    p = Path(path)
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
"@

Ensure-Content "mona/util/logging.py" @"
import logging

def setup_logging(level: str = "INFO"):
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    return logging.getLogger("mona")
"@

Ensure-Content "mona/mqtt/topics.py" @"
# Centrale plek voor MQTT topics
DISCOVERY = "esp/discovery"
HEARTBEAT = "esp/heartbeat"
"@

Ensure-Content "mona/web/api.py" @"
from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title="The Mona API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
"@

Ensure-Content "mona/web/ws.py" @"
# WebSocket endpoints komen hier (FastAPI websockets)
"@

Ensure-Content "mona/web/templates/base.html" @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>The Mona</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <header><h1>The Mona</h1></header>
  <main>
    {% block content %}{% endblock %}
  </main>
  <script src="/static/app.js"></script>
</body>
</html>
"@

Ensure-Content "mona/web/templates/home.html" @"
{% extends "base.html" %}
{% block content %}
<h2>Home</h2>
<p>Welkom bij The Mona.</p>
{% endblock %}
"@

Ensure-Content ".env.example" @"
# Voorbeeld env vars
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USER=
MQTT_PASS=
LOG_LEVEL=INFO
"@

Ensure-Content "requirements.txt" @"
fastapi
uvicorn[standard]
pydantic
pyyaml
paho-mqtt
"@

Ensure-Content "Makefile" @"
.PHONY: run dev api
dev:
\tuvicorn mona.web.api:create_app --factory --reload --host 0.0.0.0 --port 8000

run:
\tpython apps/main.py
"@

Ensure-Content "README.md" @"
# The Mona

Basisprojectstructuur met FastAPI, MQTT en game engine.
"@

Ensure-Content "deploy/systemd/mona.service" @"
[Unit]
Description=The Mona
After=network.target

[Service]
WorkingDirectory=%h/the-mona
ExecStart=/usr/bin/python3 apps/main.py
Restart=on-failure
User=%i

[Install]
WantedBy=multi-user.target
"@

Ensure-Content "docker/docker-compose.yml" @"
services:
  api:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - ..:/app
    command: bash -lc "pip install -r requirements.txt && uvicorn mona.web.api:create_app --factory --host 0.0.0.0 --port 8000"
    ports:
      - "8000:8000"
"@

Pop-Location

Write-Host "`n✅ Klaar! Structuur aangemaakt onder .\$root"
