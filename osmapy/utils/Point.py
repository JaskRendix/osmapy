from __future__ import annotations

import numpy as np

from osmapy.utils import calc


class Point:
    """Class to manage a point on the earth. Uses latitude, longitude and the mercator coordinates."""

    lat: float
    lon: float
    x: float
    y: float

    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon
        self.x, self.y = calc.deg2xy(lat, lon)

    @classmethod
    def from_deg(cls, lat: float, lon: float) -> Point:
        return cls(lat, lon)

    @classmethod
    def from_xy(cls, x: float, y: float) -> Point:
        lat, lon = calc.xy2deg(x, y)
        return cls(lat, lon)

    def __repr__(self) -> str:
        return f"Lat: {self.lat} Lon: {self.lon}"

    def __sub__(self, other: Point) -> Point:
        x = self.x - other.x
        y = self.y - other.y
        return Point.from_xy(x, y)

    def __add__(self, other: Point) -> Point:
        x = self.x + other.x
        y = self.y + other.y
        return Point.from_xy(x, y)

    def __abs__(self) -> float:
        return float(np.sqrt(self.x**2 + self.y**2))
