__all__ = ["settings", "Settings", "Environment", "settings_path"]

import os
from pathlib import Path

from src.config_schema import Environment, Settings

settings_path = os.getenv("SETTINGS_PATH", "settings.yaml")
settings: Settings = Settings.from_yaml(Path(settings_path))
