import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml
from cerberus import Validator

from osmapy.utils.config_schema import schema


@dataclass
class SlippyTile:
    name: str
    enabled: bool
    urls: list[str]


@dataclass
class Config:
    osm_api_url: str
    user_agent: str
    window_size: list[int]
    start_latitude: float
    start_longitude: float
    start_zoom: int
    login_name: str
    password: str | None
    slippy_tiles: list[SlippyTile]
    path_config: Path | None
    image_size: int = 256
    retry_time_tile: int = 4


def load_config(path: Path | None = None) -> Config:
    """
    Load and validate Osmapy configuration.
    """

    # Locate default config if no path is provided
    if path is None:
        try:
            path = resources.files("osmapy") / "config.yaml"
        except Exception as e:
            raise ValueError(f"Cannot locate default config.yaml: {e}")

    assert path is not None

    if not path.exists():
        raise ValueError(f"Config file not found: {path}")

    # Load YAML
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to read config file {path}: {e}")

    # Validate using Cerberus
    validator = Validator(schema)
    if not validator.validate(doc):
        errors = json.dumps(validator.errors, indent=2)
        raise ValueError(f"Invalid configuration:\n{errors}")

    # Environment variable overrides (optional)
    doc["osm_api_url"] = os.getenv("OSMAPY_API_URL", doc["osm_api_url"])
    doc["user_agent"] = os.getenv("OSMAPY_USER_AGENT", doc["user_agent"])

    # Convert slippy tiles
    slippy_tiles = [
        SlippyTile(
            name=t["name"],
            enabled=t["enabled"],
            urls=t["urls"],
        )
        for t in doc["slippy_tiles"]
    ]

    # Build dataclass
    return Config(
        osm_api_url=doc["osm_api_url"],
        user_agent=doc["user_agent"],
        window_size=doc["window_size"],
        start_latitude=doc["start_latitude"],
        start_longitude=doc["start_longitude"],
        start_zoom=doc["start_zoom"],
        login_name=doc["login_name"],
        password=doc.get("password"),
        slippy_tiles=slippy_tiles,
        path_config=path,
    )


def reload_config(path: Path | None = None) -> Config:
    """Reload configuration at runtime."""
    return load_config(path)
