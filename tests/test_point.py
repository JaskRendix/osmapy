import numpy as np
import pytest

from osmapy.utils.Point import Point


def test_point_initialization():
    p = Point(46.0, 8.9)
    assert p.lat == 46.0
    assert p.lon == 8.9
    assert isinstance(p.x, (int, float, np.number))
    assert isinstance(p.y, (int, float, np.number))


def test_point_from_deg():
    p = Point.from_deg(51.5, -0.1)
    assert p.lat == 51.5
    assert p.lon == -0.1


def test_point_from_xy():
    # Using known coordinates near Zurich / Central Europe
    original = Point(47.37, 8.54)
    p_xy = Point.from_xy(original.x, original.y)

    # Allow a tiny margin for coordinate conversion precision rounding
    assert pytest.approx(p_xy.lat, rel=1e-5) == original.lat
    assert pytest.approx(p_xy.lon, rel=1e-5) == original.lon


def test_point_repr():
    p = Point(46.0, 8.9)
    assert repr(p) == "Lat: 46.0 Lon: 8.9"


def test_point_addition_and_subtraction():
    p1 = Point(46.0, 8.9)
    p2 = Point(45.0, 8.0)

    # Subtraction
    sub_point = p1 - p2
    assert isinstance(sub_point, Point)
    assert sub_point.x == pytest.approx(p1.x - p2.x)
    assert sub_point.y == pytest.approx(p1.y - p2.y)

    # Addition
    add_point = p1 + p2
    assert isinstance(add_point, Point)
    assert add_point.x == pytest.approx(p1.x + p2.x)
    assert add_point.y == pytest.approx(p1.y + p2.y)


def test_point_abs():
    p = Point(3.0, 4.0)
    expected_magnitude = np.sqrt(p.x**2 + p.y**2)
    assert abs(p) == pytest.approx(expected_magnitude)
