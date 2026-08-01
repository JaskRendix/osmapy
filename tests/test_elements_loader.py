from unittest.mock import MagicMock, patch

import pytest

from osmapy.ElementsLoader.ElementsLoader import ElementsLoader


@pytest.fixture
def loader():
    return ElementsLoader()


def test_clear_resets_state(loader):
    loader.selected_node = 123
    loader.new_node_counter = -5
    loader.elements = {1: "test"}
    loader.elements_copy = {1: "test"}

    loader.clear()

    assert loader.selected_node is None
    assert loader.new_node_counter == -1
    assert loader.elements == {}
    assert loader.elements_copy == {}


@patch("requests.get")
def test_load_success(mock_get, loader):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 46.0,
                "lon": 8.9,
                "uid": "123",
                "user": "test_user",
                "version": "1",
                "changeset": "10",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "type": "way",
                "id": 2,
                "nodes": [1],
                "uid": "123",
                "user": "test_user",
                "version": "1",
                "changeset": "10",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "type": "relation",
                "id": 3,
                "members": [],
                "uid": "123",
                "user": "test_user",
                "version": "1",
                "changeset": "10",
                "timestamp": "2026-01-01T00:00:00Z",
            },
        ]
    }
    mock_get.return_value = mock_response

    loader.load(8.0, 47.0, 9.0, 46.0)

    assert 1 in loader.elements
    assert 2 in loader.elements
    assert 3 in loader.elements
    assert isinstance(loader.elements[1].data["lat"], float)
    assert loader.new_elements_loaded is True


@patch("requests.get")
def test_load_error_warning(mock_get, loader):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_get.return_value = mock_response

    with patch("PySide6.QtWidgets.QMessageBox.exec") as mock_exec:
        loader.load(8.0, 47.0, 9.0, 46.0)
        mock_exec.assert_called_once()


def test_new_node(loader):
    loader.new_node(46.0, 8.9)

    assert -1 in loader.elements
    assert loader.new_node_counter == -2
    assert loader.elements[-1].data["type"] == "node"


def test_draw_elements(loader):
    mock_node = MagicMock()
    mock_node.data = {"type": "node", "lat": 46.0, "lon": 8.9}

    mock_way = MagicMock()
    mock_way.data = {"type": "way", "nodes": [1]}

    loader.elements = {1: mock_node, 2: mock_way}
    loader.new_elements_loaded = True
    loader.selected_node = 1

    mock_viewer = MagicMock()
    mock_viewer.x = 8.9
    mock_viewer.y = 46.0
    mock_viewer.scale_x = 1.0
    mock_viewer.scale_y = 1.0
    mock_viewer.frameGeometry.return_value.width.return_value = 800
    mock_viewer.frameGeometry.return_value.height.return_value = 600
    mock_viewer.xy2screen.return_value = (100, 100)

    mock_painter = MagicMock()

    loader.draw(mock_viewer, mock_painter, 1.0)

    mock_painter.setOpacity.assert_called_once_with(1.0)
    assert mock_painter.drawEllipse.called
    assert mock_painter.drawRect.called
    assert loader.new_elements_loaded is False
