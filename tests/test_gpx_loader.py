import pytest
from PySide6.QtGui import QImage, QPainter

from osmapy.GPXLoader.GPXLoader import GPXLoader


class MockViewer:
    def __init__(self, width=800, height=600):
        self._width = width
        self._height = height

    def xy2screen(self, x, y):
        return (float(x * 10), float(y * 10))


@pytest.fixture
def sample_gpx_file(tmp_path):
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="test">
      <trk>
        <trkseg>
          <trkpt lat="10.0" lon="20.0"></trkpt>
          <trkpt lat="15.0" lon="25.0"></trkpt>
          <trkpt lat="20.0" lon="30.0"></trkpt>
        </trkseg>
      </trk>
    </gpx>
    """
    gpx_file = tmp_path / "sample.gpx"
    gpx_file.write_text(gpx_content, encoding="utf-8")
    return gpx_file


@pytest.fixture
def empty_gpx_file(tmp_path):
    gpx_file = tmp_path / "empty.gpx"
    gpx_file.write_text("<gpx></gpx>", encoding="utf-8")
    return gpx_file


def test_gpx_loader_initialization_success(sample_gpx_file):
    loader = GPXLoader(sample_gpx_file)
    assert len(loader.points) == 3
    # Check that points are parsed and populated as valid numeric coordinates
    assert loader.points[0].y is not None
    assert loader.points[0].x is not None
    assert loader.points[1].y is not None
    assert loader.points[1].x is not None


def test_gpx_loader_initialization_empty(empty_gpx_file):
    loader = GPXLoader(empty_gpx_file)
    assert len(loader.points) == 0


def test_gpx_loader_initialization_invalid_path(tmp_path):
    non_existent = tmp_path / "missing.gpx"
    loader = GPXLoader(non_existent)
    assert len(loader.points) == 0


def test_gpx_loader_draw_success(sample_gpx_file):
    loader = GPXLoader(sample_gpx_file)
    viewer = MockViewer(800, 600)

    image = QImage(800, 600, QImage.Format_ARGB32)
    image.fill(0)

    qpainter = QPainter(image)
    try:
        loader.draw(viewer, qpainter, alpha=0.8)
    finally:
        qpainter.end()


def test_gpx_loader_draw_insufficient_points(empty_gpx_file):
    loader = GPXLoader(empty_gpx_file)
    viewer = MockViewer(800, 600)

    image = QImage(800, 600, QImage.Format_ARGB32)
    image.fill(0)

    qpainter = QPainter(image)
    try:
        # Should return early before attempting to draw lines
        loader.draw(viewer, qpainter, alpha=1.0)
    finally:
        qpainter.end()
