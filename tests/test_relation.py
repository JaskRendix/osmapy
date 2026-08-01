import pytest

from osmapy.ElementsLoader.Relation import Relation


@pytest.fixture
def sample_relation_data():
    return {
        "type": "relation",
        "id": 100,
        "uid": "123",
        "user": "mapper",
        "version": "1",
        "changeset": "10",
        "timestamp": "2026-01-01T00:00:00Z",
        "members": [{"type": "node", "ref": 1, "role": "stop"}],
        "tags": {"type": "multipolygon"},
    }


def test_relation_initialization(sample_relation_data):
    relation = Relation(sample_relation_data)

    assert relation.data == sample_relation_data
    assert relation.data["id"] == 100
    assert relation.data["type"] == "relation"
    assert len(relation.data["members"]) == 1
    assert relation.data["tags"]["type"] == "multipolygon"


def test_create_new_relation_defaults():
    relation = Relation.create_new_relation(200)

    assert relation.data["id"] == 200
    assert relation.data["type"] == "relation"
    assert relation.data["members"] == []
    assert relation.data["tags"] == {}


def test_create_new_relation_custom():
    members = [{"type": "way", "ref": 5, "role": "outer"}]
    tags = {"route": "bus"}

    relation = Relation.create_new_relation(300, members=members, tags=tags)

    assert relation.data["id"] == 300
    assert relation.data["members"] == members
    assert relation.data["tags"] == tags
