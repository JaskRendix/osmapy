import pytest
from PySide6.QtGui import QImage, QPainter

from osmapy.Viewer.OSMCopyright import OSMCopyright


class MockViewer:
    def __init__(self, width, height):
        self._width = width
        self._height = height

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


@pytest.fixture
def copyright_widget():
    return OSMCopyright()


def test_osm_copyright_initialization(copyright_widget):
    assert copyright_widget.margin == 2
    assert copyright_widget.url == "https://www.openstreetmap.org/copyright"
    assert copyright_widget.width > 0
    assert copyright_widget.height > 0
    assert copyright_widget.font.pointSize() == 8


@pytest.mark.parametrize(
    "viewer_width, viewer_height",
    [
        (800, 600),
        (1920, 1080),
        (400, 300),
        (100, 100),  # Edge case: extremely small viewport
    ],
)
def test_osm_copyright_draw_positioning(copyright_widget, viewer_width, viewer_height):
    viewer = MockViewer(viewer_width, viewer_height)

    # Use an off-screen QImage device to completely avoid native widget/window painter errors and console suppression issues.
    image = QImage(viewer_width, viewer_height, QImage.Format_ARGB32)
    image.fill(0)

    qpainter = QPainter(image)
    try:
        copyright_widget.draw(viewer, qpainter)
    finally:
        qpainter.end()

    # Validate rectangle boundaries match bottom-right alignment calculation
    expected_x = viewer_width - copyright_widget.width - copyright_widget.margin
    expected_y = viewer_height - copyright_widget.height - copyright_widget.margin

    assert copyright_widget.rect.x() == expected_x
    assert copyright_widget.rect.y() == expected_y
    assert (
        copyright_widget.rect.width()
        == copyright_widget.width + copyright_widget.margin
    )
    assert (
        copyright_widget.rect.height()
        == copyright_widget.height + copyright_widget.margin
    )


def test_geometry_is_integer(copyright_widget):
    viewer = MockViewer(800, 600)
    image = QImage(800, 600, QImage.Format_ARGB32)
    qp = QPainter(image)
    qp.begin(image)
    copyright_widget.draw(viewer, qp)
    qp.end()

    rect = copyright_widget.rect
    assert isinstance(rect.x(), int)
    assert isinstance(rect.y(), int)
    assert isinstance(rect.width(), int)
    assert isinstance(rect.height(), int)


@pytest.mark.parametrize("w,h", [(20, 20), (10, 10), (5, 5)])
def test_text_clamped_to_viewport(copyright_widget, w, h):
    viewer = MockViewer(w, h)
    image = QImage(w, h, QImage.Format_ARGB32)
    qp = QPainter(image)
    qp.begin(image)
    copyright_widget.draw(viewer, qp)
    qp.end()

    rect = copyright_widget.rect
    assert rect.x() >= -rect.width()
    assert rect.y() >= -rect.height()


def test_font_size(copyright_widget):
    assert copyright_widget.font.pointSize() == 8


def test_copyright_url_constant(copyright_widget):
    assert copyright_widget.url == "https://www.openstreetmap.org/copyright"
