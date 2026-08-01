import numpy as np
import pytest

from osmapy.utils.calc import (
    Bbox_deg,
    Bbox_xy,
    deg2num,
    deg2xy,
    get_bbox_deg,
    get_bbox_xy,
    num2deg,
    xy2deg,
)


def test_bboxes_initialization():
    b_deg = Bbox_deg(left=8.0, top=47.0, right=9.0, bottom=46.0)
    assert b_deg.left == 8.0
    assert b_deg.top == 47.0
    assert b_deg.right == 9.0
    assert b_deg.bottom == 46.0

    b_xy = Bbox_xy(left=100.0, top=200.0, right=300.0, bottom=400.0)
    assert b_xy.left == 100.0
    assert b_xy.top == 200.0
    assert b_xy.right == 300.0
    assert b_xy.bottom == 400.0


def test_deg2xy_and_xy2deg_roundtrip():
    lat, lon = 46.0, 8.9
    x, y = deg2xy(lat, lon)

    assert x == lon

    calc_lat, calc_lon = xy2deg(x, y)
    assert np.isclose(calc_lat, lat)
    assert calc_lon == x


def test_deg2num_and_num2deg_roundtrip():
    lat, lon, zoom = 46.0, 8.9, 10
    xtile, ytile = deg2num(lat, lon, zoom)

    calc_lat, calc_lon = num2deg(xtile, ytile, zoom)
    assert np.isclose(calc_lat, lat, atol=1e-5)
    assert np.isclose(calc_lon, lon, atol=1e-5)


def test_get_bbox_deg():
    xtile, ytile, zoom = 33, 22, 6
    bbox = get_bbox_deg(xtile, ytile, zoom)

    assert isinstance(bbox, Bbox_deg)
    assert bbox.left < bbox.right
    assert bbox.bottom < bbox.top


def test_get_bbox_xy():
    xtile, ytile, zoom = 33, 22, 6
    bbox = get_bbox_xy(xtile, ytile, zoom)

    assert isinstance(bbox, Bbox_xy)
    assert isinstance(bbox.left, (float, np.floating))
    assert isinstance(bbox.right, (float, np.floating))


def test_xy2deg_no_overflow():
    # Extreme mercator values should not overflow
    lat, lon = xy2deg(0, 85 * np.pi)  # large y
    assert isinstance(lat, float)
    # lon is just x, which can be int or float
    assert isinstance(lon, (int, float, np.floating))


def test_get_bbox_xy_bounds():
    xtile, ytile, zoom = 33, 22, 6
    bbox = get_bbox_xy(xtile, ytile, zoom)

    assert isinstance(bbox, Bbox_xy)
    assert bbox.left < bbox.right
    # In Web Mercator, Y increases northward → top > bottom
    assert bbox.top > bbox.bottom
