from dataclasses import dataclass

import numpy as np


@dataclass
class Bbox_deg:
    left: float
    top: float
    right: float
    bottom: float


@dataclass
class Bbox_xy:
    left: float
    top: float
    right: float
    bottom: float


def xy2deg(x, y):
    """Convert Web Mercator x/y to lat/lon in degrees."""
    lon = x
    y_rad = y * np.pi / 180.0
    lat = np.degrees(np.arctan(np.sinh(y_rad)))
    return lat, lon


def deg2xy(lat, lon):
    """Convert lat/lon in degrees to Web Mercator x/y."""
    x = lon
    lat_rad = np.radians(lat)
    y = np.degrees(np.log(np.tan(np.pi / 4.0 + lat_rad / 2.0)))
    return x, y


def deg2num(lat, lon, zoom):
    """Convert lat/lon to slippy tile numbers."""
    lat_rad = np.radians(lat)
    n = 2.0**zoom
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n
    return xtile, ytile


def num2deg(xtile, ytile, zoom):
    """Convert slippy tile numbers to lat/lon."""
    n = 2.0**zoom
    lon = xtile / n * 360.0 - 180.0
    lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * ytile / n)))
    lat = np.degrees(lat_rad)
    return lat, lon


def get_bbox_deg(xtile, ytile, zoom):
    """Bounding box in degrees."""
    top, left = num2deg(xtile, ytile, zoom)
    bottom, right = num2deg(xtile + 1, ytile + 1, zoom)
    return Bbox_deg(left=left, top=top, right=right, bottom=bottom)


def get_bbox_xy(xtile, ytile, zoom):
    """Bounding box in Web Mercator x/y."""
    top_lat, left_lon = num2deg(xtile, ytile, zoom)
    bottom_lat, right_lon = num2deg(xtile + 1, ytile + 1, zoom)

    left, top = deg2xy(top_lat, left_lon)
    right, bottom = deg2xy(bottom_lat, right_lon)

    return Bbox_xy(left=left, top=top, right=right, bottom=bottom)
