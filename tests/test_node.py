import pytest

from osmapy.ElementsLoader.Node import Node


@pytest.fixture
def raw_node():
    return {
        "id": 42,
        "uid": "100",
        "user": "mapping_user",
        "version": "3",
        "changeset": "555",
        "timestamp": "2026-01-01T12:00:00Z",
        "lat": 46.0,
        "lon": 8.9,
        "tags": {"highway": "residential"},
    }


def test_node_initialization(raw_node):
    node = Node(raw_node)

    assert node.id == 42
    assert node.data["id"] == "42"
    assert node.data["uid"] == "100"
    assert node.data["user"] == "mapping_user"
    assert node.data["version"] == "3"
    assert node.data["changeset"] == "555"
    assert node.data["timestamp"] == "2026-01-01T12:00:00Z"
    assert node.data["type"] == "node"
    assert node.data["lat"] == "46.0"
    assert node.data["lon"] == "8.9"
    assert node.data["tags"] == {"highway": "residential"}
    assert node.trigger is False


def test_node_initialization_without_tags():
    raw = {
        "id": 1,
        "uid": "1",
        "user": "u",
        "version": "1",
        "changeset": "1",
        "timestamp": "2026-01-01T00:00:00Z",
        "lat": 45.0,
        "lon": 7.0,
    }
    node = Node(raw)
    assert node.data["tags"] == {}


def test_create_new_node():
    node = Node.create_new_node(99, 46.5, 9.0)

    assert node.id == 99
    assert node.data["version"] == "0"
    assert node.data["uid"] == "-1"
    assert node.data["lat"] == "46.5"
    assert node.data["lon"] == "9.0"
    assert node.data["tags"] == {}


def test_create_xml(raw_node):
    node = Node(raw_node)
    xml_elem = node.create_xml(id=42, changeset=777)

    assert xml_elem.tag == "node"
    assert xml_elem.get("id") == "42"
    assert xml_elem.get("changeset") == "777"
    assert xml_elem.get("version") == "3"
    assert xml_elem.get("lat") == "46.0"
    assert xml_elem.get("lon") == "8.9"

    tags = list(xml_elem)
    assert len(tags) == 1
    assert tags[0].tag == "tag"
    assert tags[0].get("k") == "highway"
    assert tags[0].get("v") == "residential"


def test_create_xml_omit_tags(raw_node):
    node = Node(raw_node)
    xml_elem = node.create_xml(id=42, tags=False)

    assert len(list(xml_elem)) == 0


def test_set_position(raw_node):
    node = Node(raw_node)
    node.set_position(1000000.0, 5000000.0)

    assert node.x == 1000000.0
    assert node.y == 5000000.0
    assert isinstance(node.data["lat"], str)
    assert isinstance(node.data["lon"], str)


def test_str_representation(raw_node):
    node = Node(raw_node)
    s = str(node)

    assert "<node" in s
    assert 'id="42"' in s
    assert "highway" in s


def test_equality_and_inequality(raw_node):
    node1 = Node(raw_node)

    raw_node_copy = raw_node.copy()
    node2 = Node(raw_node_copy)

    different_node_raw = raw_node.copy()
    different_node_raw["lat"] = 47.0
    node3 = Node(different_node_raw)

    assert node1 == node2
    assert node1 != node3
    assert not (node1 == node3)
    assert not (node1 != node2)
