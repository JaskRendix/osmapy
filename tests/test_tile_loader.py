from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from osmapy.TileLoader.TileLoader import TileLoader


class MockViewer:
    def __init__(self, width=800, height=600):
        self._width = width
        self._height = height
        self.lat = 46.0
        self.lon = 8.9
        self.zoom = 10
        self.x = 100.0
        self.y = 100.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.asset_error_image = ""

    class MockFrameGeometry:
        def __init__(self, w, h):
            self.w = w
            self.h = h

        def width(self):
            return self.w

        def height(self):
            return self.h

    def frameGeometry(self):
        return self.MockFrameGeometry(self._width, self._height)

    def update(self):
        pass


@pytest.fixture
def mock_config():
    with patch("osmapy.TileLoader.TileLoader.config") as cfg:
        cfg.slippy_tiles = [
            MagicMock(
                name="Standard",
                urls=[
                    "https://tile.openstreetmap.org/${zoom}/${int_xtile}/${int_ytile}.png"
                ],
            )
        ]
        cfg.user_agent = "OsmapyTestAgent"
        cfg.retry_time_tile = 60
        cfg.image_size = 256
        yield cfg


@pytest.fixture
def tile_loader(tmp_path, mock_config):
    viewer = MockViewer()

    # Instantiate TileLoader normally without breaking pathlib internals
    loader = TileLoader.__new__(TileLoader)
    loader.name = "Standard"
    loader.urls = mock_config.slippy_tiles[0].urls
    loader.path_cache = tmp_path / "cache" / "Standard"
    loader.viewer = viewer
    loader.path_cache.mkdir(parents=True, exist_ok=True)

    # Ensure database.json exists with valid empty JSON content
    db_file = loader.path_cache / "database.json"
    db_file.write_text("{}", encoding="utf-8")

    loader.cache_json = loader.load_cache_json()
    loader.queue = __import__("queue").LifoQueue()
    loader.lock = __import__("multiprocessing").Lock()
    return loader


def test_tile_loader_initialization(tile_loader):
    assert tile_loader.name is not None
    assert tile_loader.queue is not None
    assert isinstance(tile_loader.cache_json, dict)


def test_load_cache_json_creates_file(tile_loader):
    db_path = tile_loader.path_cache / "database.json"
    assert db_path.is_file()


def test_save_cache_json(tile_loader):
    tile_loader.cache_json["test_tile"] = {"state": "loaded", "time": 123456789}
    tile_loader.save_cache_json()

    reloaded = tile_loader.load_cache_json()
    assert "test_tile" in reloaded
    assert reloaded["test_tile"]["state"] == "loaded"


@patch("requests.get")
def test_worker_success(mock_get, tile_loader):
    img = Image.new("RGB", (256, 256), color="red")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")

    mock_response = MagicMock()
    mock_response.content = img_byte_arr.getvalue()
    mock_get.return_value = mock_response

    mock_tile = MagicMock()
    mock_tile.zoom = 10
    mock_tile.int_xtile = 500
    mock_tile.int_ytile = 300
    mock_tile.name = "10_500_300"

    tile_loader.cache_json["10_500_300"] = {"state": "loading", "time": 0}
    tile_loader.queue.put(mock_tile)

    try:
        tile = tile_loader.queue.get_nowait()
        osm_tile_url = tile_loader.urls[0]
        headers = {"User-Agent": "OsmapyTestAgent"}
        import requests

        response = requests.get(osm_tile_url, headers=headers)
        image = Image.open(BytesIO(response.content))

        with tile_loader.lock:
            tile_loader.path_cache.mkdir(parents=True, exist_ok=True)
            image.save(tile_loader.path_cache / f"{tile.name}.png")
            tile_loader.cache_json[tile.name]["state"] = "loaded"

        assert (tile_loader.path_cache / "10_500_300.png").is_file()
        assert tile_loader.cache_json["10_500_300"]["state"] == "loaded"
    finally:
        tile_loader.queue.task_done()


def test_close_saves_database(tile_loader):
    tile_loader.cache_json["dummy"] = {"state": "loaded", "time": 999}
    tile_loader.close()

    db_path = tile_loader.path_cache / "database.json"
    assert db_path.is_file()
