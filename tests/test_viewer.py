import pytest
from PySide6 import QtCore, QtWidgets

from osmapy.Viewer.Viewer import Viewer


class MockStatusBar:
    def showMessage(self, message, timeout=0):
        pass


class MockParent(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._status = MockStatusBar()

        # minimal mocks required by Viewer
        self.element_viewer = type(
            "EV",
            (),
            {
                "clear": lambda self: None,
                "set_node": lambda self, node: None,
            },
        )()

        self.elements_loader = type(
            "EL",
            (),
            {
                "elements": {},
                "selected_node": None,
                "clear": lambda self: None,
                "load": lambda self, *args: None,
                "new_node": lambda self, lat, lon: None,
            },
        )()

        self.layer_manager = type(
            "LM",
            (),
            {
                "add_layer": lambda self, *args, **kwargs: None,
                "get_layers": lambda self: [],
            },
        )()

    def statusBar(self):
        return self._status

    def setToolTip(self, text):
        pass


@pytest.fixture
def viewer(qtbot):
    parent = MockParent()
    v = Viewer(parent=parent)
    qtbot.addWidget(v)
    v.resize(800, 600)
    return v


def test_viewer_initialization(viewer):
    assert viewer.mode == "normal"
    assert viewer.undo_stack is not None


def test_viewer_zoom_limits(viewer):
    viewer.set_zoom(10)
    assert viewer.zoom == 10

    viewer.zoom = 19

    class MockWheelEvent:
        def __init__(self, delta):
            self._delta = delta

        def angleDelta(self):
            return QtCore.QPoint(0, self._delta)

    viewer.wheelEvent(MockWheelEvent(120))
    assert viewer.zoom == 19  # capped


def test_coordinate_conversion_roundtrip(viewer):
    sx, sy = 400.0, 300.0
    mx, my = viewer.screen2xy(sx, sy)
    sx2, sy2 = viewer.xy2screen(mx, my)

    assert pytest.approx(sx2, abs=1e-2) == sx
    assert pytest.approx(sy2, abs=1e-2) == sy


def test_mode_switching(viewer):
    viewer.change_mode("new_node")
    assert viewer.mode == "new_node"
    viewer.change_mode("normal")
    assert viewer.mode == "normal"


def test_pan_basic(viewer):
    viewer.set_xy(10.0, 20.0)
    assert viewer.x == 10.0
    assert viewer.y == 20.0
