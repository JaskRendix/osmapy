import json
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from osmapy.utils.Export import Exporter


def test_export_to_osm(tmp_path):
    output_file = tmp_path / "output.osm"

    elements = {
        101: MagicMock(
            data={
                "type": "node",
                "id": 101,
                "lat": 46.0,
                "lon": 8.9,
                "version": 1,
                "tags": {"amenity": "cafe"},
            }
        ),
        201: MagicMock(
            data={
                "type": "way",
                "id": 201,
                "version": 2,
                "nodes": [101, 102],
                "tags": {"highway": "residential"},
            }
        ),
        301: MagicMock(
            data={
                "type": "relation",
                "id": 301,
                "version": 1,
                "members": [{"type": "way", "ref": 201, "role": "outer"}],
                "tags": {"type": "multipolygon"},
            }
        ),
    }

    Exporter.export_to_osm(output_file, elements)

    assert output_file.exists()
    tree = ET.parse(output_file)
    root = tree.getroot()

    assert root.tag == "osm"
    assert root.get("version") == "0.6"
    assert root.get("generator") == "osmapy"

    node = root.find("node")
    assert node is not None
    assert node.get("id") == "101"
    assert node.get("lat") == "46.0"
    assert node.get("lon") == "8.9"
    assert node.get("version") == "1"

    node_tag = node.find("tag")
    assert node_tag.get("k") == "amenity"
    assert node_tag.get("v") == "cafe"

    way = root.find("way")
    assert way.get("id") == "201"
    assert way.get("version") == "2"

    nd = way.find("nd")
    assert nd.get("ref") == "101"

    way_tag = way.find("tag")
    assert way_tag.get("k") == "highway"
    assert way_tag.get("v") == "residential"

    relation = root.find("relation")
    assert relation.get("id") == "301"
    assert relation.get("version") == "1"

    member = relation.find("member")
    assert member.get("type") == "way"
    assert member.get("ref") == "201"
    assert member.get("role") == "outer"

    rel_tag = relation.find("tag")
    assert rel_tag.get("k") == "type"
    assert rel_tag.get("v") == "multipolygon"


def test_export_to_gpx(tmp_path):
    output_file = tmp_path / "output.gpx"

    elements = {
        101: MagicMock(
            data={
                "type": "node",
                "id": 101,
                "lat": 46.0,
                "lon": 8.9,
                "tags": {"name": "Cafe"},
            }
        ),
        102: MagicMock(
            data={
                "type": "node",
                "id": 102,
                "lat": 46.1,
                "lon": 8.91,
                "tags": {},
            }
        ),
        201: MagicMock(
            data={
                "type": "way",
                "id": 201,
                "nodes": [101, 102],
                "tags": {"name": "Main Street"},
            }
        ),
    }

    Exporter.export_to_gpx(output_file, elements)

    assert output_file.exists()
    tree = ET.parse(output_file)
    root = tree.getroot()

    assert root.tag.endswith("gpx")
    assert root.get("version") == "1.1"
    assert root.get("creator") == "osmapy"

    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    wpt = root.find(".//g:wpt", ns)
    assert wpt is not None
    assert wpt.get("lat") == "46.0"
    assert wpt.get("lon") == "8.9"

    name = wpt.find("g:name", ns)
    assert name.text == "Cafe"

    trk = root.find(".//g:trk", ns)
    assert trk is not None

    trk_name = trk.find("g:name", ns)
    assert trk_name.text == "Main Street"

    trkseg = trk.find("g:trkseg", ns)
    trkpts = trkseg.findall("g:trkpt", ns)
    assert len(trkpts) == 2
    assert trkpts[0].get("lat") == "46.0"
    assert trkpts[0].get("lon") == "8.9"
    assert trkpts[1].get("lat") == "46.1"
    assert trkpts[1].get("lon") == "8.91"


def test_export_to_geojson(tmp_path):
    output_file = tmp_path / "output.geojson"

    elements = {
        101: MagicMock(
            data={
                "type": "node",
                "id": 101,
                "lat": 46.0,
                "lon": 8.9,
                "tags": {"amenity": "cafe"},
            }
        ),
        201: MagicMock(
            data={
                "type": "way",
                "id": 201,
                "nodes": [101],
                "tags": {"highway": "residential"},
            }
        ),
        301: MagicMock(
            data={
                "type": "relation",
                "id": 301,
                "members": [{"type": "node", "ref": 101}],
                "tags": {"type": "multipoint"},
            }
        ),
    }

    Exporter.export_to_geojson(output_file, elements)

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 3

    node_feature = next(f for f in data["features"] if f["geometry"]["type"] == "Point")
    assert node_feature["geometry"]["coordinates"] == [8.9, 46.0]
    assert node_feature["properties"]["amenity"] == "cafe"

    way_feature = next(
        f for f in data["features"] if f["geometry"]["type"] == "LineString"
    )
    assert way_feature["geometry"]["coordinates"] == [[8.9, 46.0]]
    assert way_feature["properties"]["highway"] == "residential"

    rel_feature = next(
        f for f in data["features"] if f["geometry"]["type"] == "MultiPoint"
    )
    assert rel_feature["geometry"]["coordinates"] == [[8.9, 46.0]]
    assert rel_feature["properties"]["type"] == "multipoint"


def test_export_empty_osm(tmp_path):
    output_file = tmp_path / "empty.osm"
    Exporter.export_to_osm(output_file, {})

    assert output_file.exists()
    tree = ET.parse(output_file)
    root = tree.getroot()

    assert root.tag == "osm"
    assert len(root) == 0


def test_export_empty_geojson(tmp_path):
    output_file = tmp_path / "empty.geojson"
    Exporter.export_to_geojson(output_file, {})

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["type"] == "FeatureCollection"
    assert data["features"] == []


def test_export_missing_tags_osm(tmp_path):
    output_file = tmp_path / "missing_tags.osm"

    elements = {
        1: MagicMock(data={"type": "node", "id": 1, "lat": 1.0, "lon": 2.0}),
        2: MagicMock(data={"type": "way", "id": 2, "nodes": []}),
    }

    Exporter.export_to_osm(output_file, elements)
    tree = ET.parse(output_file)
    root = tree.getroot()

    node = root.find("node")
    assert node.find("tag") is None

    way = root.find("way")
    assert way.find("tag") is None


def test_export_missing_tags_geojson(tmp_path):
    output_file = tmp_path / "missing_tags.geojson"

    elements = {
        1: MagicMock(data={"type": "node", "lat": 1.0, "lon": 2.0}),
    }

    Exporter.export_to_geojson(output_file, elements)

    with open(output_file, "r") as f:
        data = json.load(f)

    feature = data["features"][0]
    assert feature["properties"] == {}


def test_export_invalid_element_type(tmp_path):
    output_file = tmp_path / "invalid.osm"

    elements = {
        999: MagicMock(data={"type": "banana", "foo": "bar"}),
    }

    Exporter.export_to_osm(output_file, elements)

    tree = ET.parse(output_file)
    root = tree.getroot()

    assert len(root) == 0


def test_export_invalid_element_type_geojson(tmp_path):
    output_file = tmp_path / "invalid.geojson"

    elements = {
        999: MagicMock(data={"type": "banana"}),
    }

    Exporter.export_to_geojson(output_file, elements)

    with open(output_file) as f:
        data = json.load(f)

    assert data["features"] == []


def test_export_round_trip_osm(tmp_path):
    output_file = tmp_path / "roundtrip.osm"

    elements = {
        10: MagicMock(
            data={
                "type": "node",
                "id": 10,
                "lat": 46.0,
                "lon": 8.9,
                "tags": {"name": "TestNode"},
            }
        ),
        20: MagicMock(
            data={
                "type": "way",
                "id": 20,
                "nodes": [10],
                "tags": {"highway": "track"},
            }
        ),
    }

    Exporter.export_to_osm(output_file, elements)

    tree = ET.parse(output_file)
    root = tree.getroot()

    node = root.find("node")
    assert node.get("id") == "10"
    assert node.get("lat") == "46.0"
    assert node.get("lon") == "8.9"
    assert node.find("tag").get("v") == "TestNode"

    way = root.find("way")
    assert way.get("id") == "20"
    assert way.find("nd").get("ref") == "10"
    assert way.find("tag").get("v") == "track"
