"""
Configuration loader for The Mona system.

Loads configuration from environment variables and YAML files,
with validation using Pydantic models.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class MQTTConfig(BaseModel):
    """MQTT broker connection configuration."""
    host: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    keepalive: int = 60
    topic_prefix: str = "the-mona"
    qos_default: int = 1
    reconnect_delay_min: float = 1.0
    reconnect_delay_max: float = 60.0


class GameConfig(BaseModel):
    """Game engine configuration."""
    tick_interval: float = 0.1
    button_timeout: float = 5.0
    discovery_timeout: float = 30.0
    max_players: int = 6
    
    # Game mode defaults
    reaction_race_timeout: float = 5.0
    simon_sequence_length: int = 8
    simon_show_duration: float = 1.0
    simon_input_timeout: float = 10.0


class AudioConfig(BaseModel):
    """Audio system configuration."""
    device_name: str = "JBL"  # Partial name to match
    default_volume: int = 80
    test_tone_freq: int = 440
    test_tone_duration: float = 0.5
    reconnect_interval: float = 10.0
    
    # Audio file paths
    sfx_directory: str = "mona/audio/sfx"
    success_sound: str = "success.wav"
    fail_sound: str = "fail.wav"
    button_sound: str = "button.wav"


class WebConfig(BaseModel):
    """Web interface configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    log_level: str = "info"
    cors_origins: List[str] = ["*"]
    
    # Static files
    static_dir: str = "mona/web/static"
    template_dir: str = "mona/web/templates"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "/var/log/the-mona/app.log"
    file_max_size: int = 10 * 1024 * 1024  # 10MB
    file_backup_count: int = 5
    console_enabled: bool = True


class MonaConfig(BaseModel):
    """Main configuration container."""
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    game: GameConfig = Field(default_factory=GameConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Known buttons (optional - can be discovered)
    buttons: List[str] = Field(default_factory=list)
    
    @validator('buttons')
    def validate_buttons(cls, v):
        """Validate button IDs format."""
        for button_id in v:
            if not button_id.replace('-', '').replace('_', '').isalnum():
                raise ValueError(f"Invalid button ID format: {button_id}")
        return v


class EnvSettings(BaseSettings):
    """Environment variable settings with .env support."""
    
    # Core settings
    MONA_DEBUG: bool = False
    MONA_LOG_LEVEL: str = "INFO"
    
    # MQTT settings
    MONA_MQTT_HOST: str = "localhost"
    MONA_MQTT_PORT: int = 1883
    MONA_MQTT_USERNAME: Optional[str] = None
    MONA_MQTT_PASSWORD: Optional[str] = None
    
    # Web settings
    MONA_WEB_HOST: str = "0.0.0.0"
    MONA_WEB_PORT: int = 8000
    MONA_WEB_DEBUG: bool = False
    
    # Audio settings
    MONA_AUDIO_DEVICE: str = "JBL"
    MONA_AUDIO_VOLUME: int = 80
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_path}: {e}")
    except Exception as e:
        raise ValueError(f"Could not read {config_path}: {e}")


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge configuration dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config(config_path: Optional[Path] = None) -> MonaConfig:
    """
    Load complete configuration from multiple sources.
    
    Priority order (highest to lowest):
    1. Environment variables
    2. config.yaml file
    3. Default values
    """
    if config_path is None:
        config_path = Path("config.yaml")
    
    # Load environment settings
    env_settings = EnvSettings()
    
    # Load YAML configuration
    yaml_config = load_yaml_config(config_path)
    
    # Create base configuration with environment overrides
    config_dict = {}
    
    # Map environment variables to config structure
    if env_settings.MONA_MQTT_HOST:
        config_dict.setdefault('mqtt', {})['host'] = env_settings.MONA_MQTT_HOST
    if env_settings.MONA_MQTT_PORT:
        config_dict.setdefault('mqtt', {})['port'] = env_settings.MONA_MQTT_PORT
    if env_settings.MONA_MQTT_USERNAME:
        config_dict.setdefault('mqtt', {})['username'] = env_settings.MONA_MQTT_USERNAME
    if env_settings.MONA_MQTT_PASSWORD:
        config_dict.setdefault('mqtt', {})['password'] = env_settings.MONA_MQTT_PASSWORD
    
    if env_settings.MONA_WEB_HOST:
        config_dict.setdefault('web', {})['host'] = env_settings.MONA_WEB_HOST
    if env_settings.MONA_WEB_PORT:
        config_dict.setdefault('web', {})['port'] = env_settings.MONA_WEB_PORT
    if env_settings.MONA_WEB_DEBUG:
        config_dict.setdefault('web', {})['debug'] = env_settings.MONA_WEB_DEBUG
    
    if env_settings.MONA_AUDIO_DEVICE:
        config_dict.setdefault('audio', {})['device_name'] = env_settings.MONA_AUDIO_DEVICE
    if env_settings.MONA_AUDIO_VOLUME:
        config_dict.setdefault('audio', {})['default_volume'] = env_settings.MONA_AUDIO_VOLUME
    
    if env_settings.MONA_LOG_LEVEL:
        config_dict.setdefault('logging', {})['level'] = env_settings.MONA_LOG_LEVEL
    
    if env_settings.MONA_DEBUG:
        config_dict.setdefault('web', {})['debug'] = True
        config_dict.setdefault('logging', {})['level'] = "DEBUG"
    
    # Merge YAML config (overrides defaults, but not env vars)
    final_config = merge_configs(yaml_config, config_dict)
    
    # Create and validate final configuration
    try:
        return MonaConfig(**final_config)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def create_example_config() -> str:
    """Generate example configuration YAML."""
    return """
# The Mona Configuration File
# Copy this to config.yaml and adjust as needed

# MQTT Broker Settings
mqtt:
  host: localhost
  port: 1883
  # username: mona_user
  # password: secret_password
  topic_prefix: the-mona
  qos_default: 1
  keepalive: 60
  reconnect_delay_min: 1.0
  reconnect_delay_max: 60.0

# Game Engine Settings
game:
  tick_interval: 0.1
  button_timeout: 5.0
  discovery_timeout: 30.0
  max_players: 6
  
  # Game mode specific settings
  reaction_race_timeout: 5.0
  simon_sequence_length: 8
  simon_show_duration: 1.0
  simon_input_timeout: 10.0

# Audio System Settings  
audio:
  device_name: JBL  # Partial name to match Bluetooth device
  default_volume: 80
  test_tone_freq: 440
  test_tone_duration: 0.5
  reconnect_interval: 10.0
  
  # Sound effects
  sfx_directory: mona/audio/sfx
  success_sound: success.wav
  fail_sound: fail.wav
  button_sound: button.wav

# Web Interface Settings
web:
  host: 0.0.0.0
  port: 8000
  debug: false
  reload: false
  log_level: info
  cors_origins: ["*"]
  
  static_dir: mona/web/static
  template_dir: mona/web/templates

# Logging Settings
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_enabled: true
  file_path: /var/log/the-mona/app.log
  file_max_size: 10485760  # 10MB
  file_backup_count: 5
  console_enabled: true

# Known Buttons (optional - will be auto-discovered if empty)
buttons:
  # - button-01
  # - button-02
  # - button-03
  # - button-04
  # - button-05
  # - button-06
"""


if __name__ == "__main__":
    # Generate example configuration
    print("Example config.yaml:")
    print(create_example_config())