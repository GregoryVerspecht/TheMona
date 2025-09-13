from pathlib import Path
import yaml

def load_config(path: str = "config.yaml") -> dict:
    p = Path(path)
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
