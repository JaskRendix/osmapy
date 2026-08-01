from unittest.mock import patch

import pytest

from osmapy.TileLoader.Tile import Tile


@pytest.fixture
def mock_config():
    with patch("osmapy.TileLoader.Tile.config") as cfg:
        cfg.image_size = 256
        yield cfg


def test_tile_initialization(mock_config):
    lat, lon, zoom = 47.3769, 8.5417, 10
    tile = Tile(lat, lon, zoom)

    assert tile.lat == lat
    assert tile.lon == lon
    assert tile.zoom == zoom
    assert isinstance(tile.int_xtile, int)
    assert isinstance(tile.int_ytile, int)
    assert tile.name == f"{tile.int_xtile}_{tile.int_ytile}_{zoom}"
    assert tile.width_x > 0
    assert tile.width_y > 0
    assert tile.scale_x > 0
    assert tile.scale_y > 0


def test_tile_from_num(mock_config):
    xtile, ytile, zoom = 536.0, 355.0, 10
    tile = Tile.from_num(xtile, ytile, zoom)

    assert tile.zoom == zoom
    assert tile.int_xtile == int(xtile)
    assert tile.int_ytile == int(ytile)
    assert tile.name == f"{tile.int_xtile}_{tile.int_ytile}_{zoom}"


@pytest.mark.parametrize(
    "xtile, ytile, zoom, expected",
    [
        (10, 10, 4, True),  # Valid bounds
        (1, 1, 2, True),  # Valid inner bounds for zoom 2
        (3, 3, 2, True),  # Valid upper bounds for zoom 2
        (-1, 5, 3, False),  # Invalid xtile (negative)
        (9, 5, 3, False),  # Invalid xtile (exceeds 2**zoom)
        (5, -1, 3, False),  # Invalid ytile (negative)
        (5, 9, 3, False),  # Invalid ytile (exceeds 2**zoom)
    ],
)
def test_check_existance(mock_config, xtile, ytile, zoom, expected):
    tile = Tile.from_num(xtile, ytile, zoom)
    assert tile.check_existance() == expected


def test_tile_scaling_and_dimensions(mock_config):
    tile = Tile(0.0, 0.0, 5)

    expected_scale_x = tile.width_x / mock_config.image_size
    assert tile.scale_x == expected_scale_x

    assert isinstance(tile.center_x, float)
    assert isinstance(tile.center_y, float)
