import pytest

from osmapy.ElementsLoader.Way import Way


@pytest.fixture
def raw_way():
    return {
        "id": 500,
        "uid": "123",
        "user": "mapper",
        "version": "2",
        "changeset": "999",
        "timestamp": "2026-01-01T00:00:00Z",
        "nodes": [10, 20, 30],
        "tags": {"natural": "water"},
    }


def test_way_initialization(raw_way):
    way = Way(raw_way)

    assert way.id == 500
    assert way.data["id"] == "500"
    assert way.data["uid"] == "123"
    assert way.data["user"] == "mapper"
    assert way.data["version"] == "2"
    assert way.data["changeset"] == "999"
    assert way.data["timestamp"] == "2026-01-01T00:00:00Z"
    assert way.data["type"] == "way"
    assert way.data["nodes"] == [10, 20, 30]
    assert way.data["tags"] == {"natural": "water"}


def test_way_initialization_defaults():
    raw = {
        "id": 501,
        "uid": "1",
        "user": "u",
        "version": "1",
        "changeset": "1",
        "timestamp": "2026-01-01T00:00:00Z",
    }
    way = Way(raw)

    assert way.data["nodes"] == []
    assert way.data["tags"] == {}


def test_create_xml(raw_way):
    way = Way(raw_way)
    xml_elem = way.create_xml(id=500, changeset=888)

    assert xml_elem.tag == "way"
    assert xml_elem.get("id") == "500"
    assert xml_elem.get("changeset") == "888"
    assert xml_elem.get("version") == "2"

    # Check child subelements (nd elements and tag elements)
    children = list(xml_elem)
    # 3 nodes + 1 tag = 4 children total
    assert len(children) == 4

    # Verify node reference subelements
    nd_elements = [c for c in children if c.tag == "nd"]
    assert len(nd_elements) == 3
    assert nd_elements[0].get("ref") == "10"
    assert nd_elements[1].get("ref") == "20"
    assert nd_elements[2].get("ref") == "30"

    # Verify tag subelement
    tag_elements = [c for c in children if c.tag == "tag"]
    assert len(tag_elements) == 1
    assert tag_elements[0].get("k") == "natural"
    assert tag_elements[0].get("v") == "water"


def test_create_xml_omit_tags(raw_way):
    way = Way(raw_way)
    xml_elem = way.create_xml(id=500, tags=False)

    children = list(xml_elem)
    # Only the 3 nd elements should be present
    assert len(children) == 3
    assert all(c.tag == "nd" for c in children)


def test_str_representation(raw_way):
    way = Way(raw_way)
    s = str(way)

    assert "<way" in s
    assert 'id="500"' in s
    assert 'ref="10"' in s
    assert "natural" in s
