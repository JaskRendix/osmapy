import importlib
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest


@pytest.fixture(autouse=True)
def restore_config():
    yield
    import osmapy.utils.config as cfg_module

    importlib.reload(cfg_module)


def test_config_success(monkeypatch, tmp_path):
    valid_yaml = """
osm_api_url: "http://api"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tile"
    enabled: true
    urls: ["http://tile"]
"""

    # Create a real temporary file
    tmp_file = tmp_path / "config.yaml"
    tmp_file.write_text(valid_yaml)

    with patch("cerberus.Validator.validate", return_value=True):
        import osmapy.utils.config as cfg_module

        cfg = cfg_module.load_config(tmp_file)
        assert isinstance(cfg, cfg_module.Config)
        assert cfg.image_size == 256
        assert cfg.retry_time_tile == 4


def test_missing_config_file(tmp_path):
    missing = tmp_path / "does_not_exist.yaml"
    import osmapy.utils.config as cfg

    with pytest.raises(ValueError, match="Config file not found"):
        cfg.load_config(missing)


def test_invalid_yaml(tmp_path):
    bad_yaml = tmp_path / "config.yaml"
    bad_yaml.write_text("::: not yaml :::")

    import osmapy.utils.config as cfg

    with pytest.raises(ValueError, match="Failed to read config file"):
        cfg.load_config(bad_yaml)


def test_schema_validation_failure(tmp_path):
    invalid_yaml = tmp_path / "config.yaml"
    invalid_yaml.write_text("osm_api_url: 123")  # wrong type

    import osmapy.utils.config as cfg

    with patch("cerberus.Validator.validate", return_value=False):
        with pytest.raises(ValueError, match="Invalid configuration"):
            cfg.load_config(invalid_yaml)


def test_env_override(monkeypatch, tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        """
osm_api_url: "http://original"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tile"
    enabled: true
    urls: ["http://tile"]
"""
    )

    monkeypatch.setenv("OSMAPY_API_URL", "http://override")
    monkeypatch.setenv("OSMAPY_USER_AGENT", "OverrideUA")

    import osmapy.utils.config as cfg

    cfg_module = cfg.load_config(yaml_file)

    assert cfg_module.osm_api_url == "http://override"
    assert cfg_module.user_agent == "OverrideUA"


def test_slippy_tile_parsing(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        """
osm_api_url: "http://api"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tileA"
    enabled: true
    urls: ["http://a1", "http://a2"]
  - name: "tileB"
    enabled: false
    urls: ["http://b"]
"""
    )

    import osmapy.utils.config as cfg

    c = cfg.load_config(yaml_file)

    assert len(c.slippy_tiles) == 2
    assert c.slippy_tiles[0].name == "tileA"
    assert c.slippy_tiles[1].enabled is False


def test_default_values(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        """
osm_api_url: "http://api"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tile"
    enabled: true
    urls: ["http://tile"]
"""
    )

    import osmapy.utils.config as cfg

    c = cfg.load_config(yaml_file)

    assert c.image_size == 256
    assert c.retry_time_tile == 4


def test_reload_config(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        """
osm_api_url: "http://api"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tile"
    enabled: true
    urls: ["http://tile"]
"""
    )

    import osmapy.utils.config as cfg

    with patch("osmapy.utils.config.load_config") as mock_load:
        cfg.reload_config(yaml_file)
        mock_load.assert_called_once_with(yaml_file)


@pytest.mark.parametrize(
    "bad_yaml",
    [
        "osm_api_url: 123",  # wrong type
        "window_size: not_a_list",  # wrong type
        "slippy_tiles: 5",  # wrong type
        "start_zoom: -1",  # invalid value
    ],
)
def test_invalid_schema(monkeypatch, tmp_path, bad_yaml):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(bad_yaml)

    import osmapy.utils.config as cfg

    with patch("cerberus.Validator.validate", return_value=False):
        with pytest.raises(ValueError):
            cfg.load_config(yaml_file)


def test_path_config_is_set(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        """
osm_api_url: "http://api"
user_agent: "UA"
window_size: [800, 600]
start_latitude: 0
start_longitude: 0
start_zoom: 5
login_name: "user"
password: null
slippy_tiles:
  - name: "tile"
    enabled: true
    urls: ["http://tile"]
"""
    )

    import osmapy.utils.config as cfg

    c = cfg.load_config(yaml_file)

    assert c.path_config == yaml_file
