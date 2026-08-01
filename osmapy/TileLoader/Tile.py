import numpy as np

from osmapy.utils import calc
from osmapy.utils.config import load_config

config = load_config()


class Tile:
    """Class to represent a slippy tile."""

    def __init__(self, lat, lon, zoom):
        """Constructer with the latitude and longitude which should lay inside of the slippy tile.

        Args:
            lat (float): latitude of a position which should lay inside of the tile
            lon (float): longitude of a position which should lay inside of the tile
            zoom (int): zoom level of the tile
        """
        self.lat = lat
        self.lon = lon
        self.zoom = zoom

        self.x, self.y = calc.deg2xy(self.lat, self.lon)

        self.xtile, self.ytile = calc.deg2num(self.lat, self.lon, self.zoom)
        self.int_xtile, self.int_ytile = int(self.xtile), int(self.ytile)

        self.bbox_deg = calc.get_bbox_deg(self.xtile, self.ytile, self.zoom)
        self.bbox_xy = calc.get_bbox_xy(self.xtile, self.ytile, self.zoom)

        # Correct width calculations
        self.width_x = np.abs(self.bbox_xy.right - self.bbox_xy.left)
        self.width_y = np.abs(self.bbox_xy.bottom - self.bbox_xy.top)

        # Correct scale calculations
        self.scale_x = self.width_x / config.image_size
        self.scale_y = self.width_y / config.image_size

        # Correct tile center
        self.center_x, self.center_y = calc.deg2xy(
            *calc.num2deg(self.int_xtile + 0.5, self.int_ytile + 0.5, self.zoom)
        )

        self.name = f"{self.int_xtile}_{self.int_ytile}_{self.zoom}"

    @classmethod
    def from_num(cls, xtile, ytile, zoom):
        """Alternative constructor using the slippy tile numbers.

        Args:
            xtile (float): x slippy tile number of the requested tile
            ytile (float): y slippy tile number of the requested tile
            zoom (int): zoom level of the tile
        """
        tile = cls(*calc.num2deg(xtile, ytile, zoom), zoom)
        tile.xtile = xtile
        tile.ytile = ytile
        tile.int_xtile = int(xtile)
        tile.int_ytile = int(ytile)
        return tile

    def check_existance(self):
        """Checks if the tilenumbers are valid and if the tile can exists on a slippy tile server.

        Returns:
            bool: True if tile can exists, False if not
        """
        max_tile = 2**self.zoom
        return 0 <= self.int_xtile < max_tile and 0 <= self.int_ytile < max_tile
