import yaml
import os

def load_config(path: str = "config.yaml"):
    if not os.path.exists(path):
        raise FileNotFoundError("Config file not found: " + path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
