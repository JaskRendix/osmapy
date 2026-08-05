from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QLineEdit, QPushButton

from osmapy.Viewer.ElementViewer import ElementViewer


class MockNode:
    def __init__(self, id_val=1, lat=46.0, lon=8.9, tags=None):
        self.id = id_val
        self.data = {
            "uid": 123,
            "user": "test_user",
            "version": 1,
            "changeset": 456,
            "timestamp": "2026-01-01T00:00:00Z",
            "lat": lat,
            "lon": lon,
            "tags": tags or {"amenity": "cafe", "name": "Central"},
        }


class MockViewer:
    def update(self):
        pass


class MockElementsLoader:
    def __init__(self, node):
        self.elements = {node.id: node}
        self.selected_node = node.id


class MockParent:
    def __init__(self, node):
        self.elements_loader = MockElementsLoader(node)
        self.viewer = MockViewer()


@pytest.fixture
def sample_node():
    return MockNode()


@pytest.fixture
def element_viewer(qtbot, sample_node):
    parent = MockParent(sample_node)
    ev = ElementViewer(parent)
    qtbot.addWidget(ev)
    ev.show()
    ev.set_node(sample_node)
    return ev


def test_element_viewer_initialization(qtbot):
    parent = MockParent(MockNode())
    ev = ElementViewer(parent)
    qtbot.addWidget(ev)

    # Should display the default prompt text
    assert ev.layout().itemAt(0).widget().text() == "Right Click to Select Node"


def test_element_viewer_set_node(element_viewer, sample_node):
    assert element_viewer.id == sample_node.id
    assert "amenity" in element_viewer.tag_widgets
    assert "name" in element_viewer.tag_widgets


def test_modify_property_valid(element_viewer, sample_node):
    lat_edit = [
        w for w in element_viewer.findChildren(QLineEdit) if w.text() == "46.0"
    ][0]

    # Change latitude to valid value
    lat_edit.setText("45.5")
    assert sample_node.data["lat"] == 45.5
    assert lat_edit.styleSheet() == ""


def test_modify_property_invalid_range(element_viewer, sample_node):
    lat_edit = [
        w for w in element_viewer.findChildren(QLineEdit) if w.text() == "46.0"
    ][0]

    # Invalid latitude > 90
    lat_edit.setText("95.0")
    assert "border: 2px solid red;" in lat_edit.styleSheet()


def test_filter_tags(element_viewer):
    element_viewer.search_bar.setText("cafe")

    cafe_btn, cafe_val = element_viewer.tag_widgets["amenity"]
    name_btn, name_val = element_viewer.tag_widgets["name"]

    # 'amenity' matches 'cafe', 'name' does not
    assert cafe_btn.isVisible() is True
    assert name_btn.isVisible() is False


def test_modify_tag(element_viewer, sample_node):
    _, val_edit = element_viewer.tag_widgets["amenity"]
    val_edit.setText("restaurant")

    assert sample_node.data["tags"]["amenity"] == "restaurant"


def test_remove_tag(element_viewer, sample_node):
    key_btn, _ = element_viewer.tag_widgets["amenity"]

    # Simulate clicking key button to trigger removal
    key_btn.click()
    assert "amenity" not in sample_node.data["tags"]


def test_delete_node(element_viewer, sample_node):
    delete_btn = [
        w for w in element_viewer.findChildren(QPushButton) if w.text() == "Delete Node"
    ][0]
    delete_btn.click()

    assert sample_node.id not in element_viewer.parent_widget.elements_loader.elements
    assert element_viewer.parent_widget.elements_loader.selected_node is None


def test_tags_are_sorted(element_viewer):
    keys = list(element_viewer.tag_widgets.keys())
    assert keys == sorted(keys, key=str.lower)


def test_filter_highlight(element_viewer):
    element_viewer.search_bar.setText("cen")  # matches "Central"
    key_btn, _ = element_viewer.tag_widgets["name"]
    assert "background" in key_btn.styleSheet()


def test_shortcuts_exist(element_viewer):
    buttons = element_viewer.findChildren(QPushButton)
    shortcuts = [b.shortcut().toString() for b in buttons]
    assert "Ctrl+T" in shortcuts
    assert "Del" in shortcuts
