import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import yaml

load_dotenv()

class AppCfg(BaseModel):
    name: str = "the-mona"
    log_level: str = "INFO"

class MqttCfg(BaseModel):
    host: str = "the-mona.local"
    port: int = 1883
    username: str | None = None
    password: str | None = None
    client_id: str = "the-mona-app"
    topic_prefix: str = "the-mona"
    qos_default: int = 1
    heartbeat_timeout_sec: int = 45

class WebCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = int(os.getenv("WEB_PORT", "8080"))

class AudioCfg(BaseModel):
    sink_preferred_name: str = "Analog"
    default_volume: int = 70

class GameCfg(BaseModel):
    default_mode: str = "ReactionRace"
    tick_ms: int = 100

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")
    app: AppCfg = AppCfg()
    mqtt: MqttCfg = MqttCfg()
    web: WebCfg = WebCfg()
    audio: AudioCfg = AudioCfg()
    game: GameCfg = GameCfg()

def _load_yaml():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

_yaml = _load_yaml()
settings = Settings(**_yaml)
