import json
import xml.etree.ElementTree as ET


class Exporter:
    """Utility to export loaded elements to various formats."""

    @staticmethod
    def export_to_osm(filepath, elements):
        osm = ET.Element("osm", version="0.6", generator="osmapy")

        for elem in elements.values():
            data = elem.data
            elem_type = data.get("type")

            if elem_type == "node":
                node_elem = ET.SubElement(
                    osm,
                    "node",
                    {
                        "id": str(data.get("id")),
                        "lat": str(data.get("lat")),
                        "lon": str(data.get("lon")),
                        "version": str(data.get("version", 1)),
                    },
                )
                for k, v in data.get("tags", {}).items():
                    ET.SubElement(node_elem, "tag", {"k": k, "v": v})

            elif elem_type == "way":
                way_elem = ET.SubElement(
                    osm,
                    "way",
                    {
                        "id": str(data.get("id")),
                        "version": str(data.get("version", 1)),
                    },
                )
                for n_id in data.get("nodes", []):
                    ET.SubElement(way_elem, "nd", {"ref": str(n_id)})
                for k, v in data.get("tags", {}).items():
                    ET.SubElement(way_elem, "tag", {"k": k, "v": v})

            elif elem_type == "relation":
                rel_elem = ET.SubElement(
                    osm,
                    "relation",
                    {
                        "id": str(data.get("id")),
                        "version": str(data.get("version", 1)),
                    },
                )
                for member in data.get("members", []):
                    ET.SubElement(
                        rel_elem,
                        "member",
                        {
                            "type": str(member.get("type")),
                            "ref": str(member.get("ref")),
                            "role": str(member.get("role", "")),
                        },
                    )
                for k, v in data.get("tags", {}).items():
                    ET.SubElement(rel_elem, "tag", {"k": k, "v": v})

        tree = ET.ElementTree(osm)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def export_to_gpx(filepath, elements):
        """Export nodes and ways to GPX (tracks + waypoints)."""

        gpx = ET.Element(
            "gpx",
            version="1.1",
            creator="osmapy",
            xmlns="http://www.topografix.com/GPX/1/1",
        )

        # Waypoints for nodes
        for elem in elements.values():
            data = elem.data
            if data.get("type") == "node":
                wpt = ET.SubElement(
                    gpx,
                    "wpt",
                    lat=str(data.get("lat")),
                    lon=str(data.get("lon")),
                )
                name = data.get("tags", {}).get("name")
                if name:
                    ET.SubElement(wpt, "name").text = name

        # Tracks for ways
        for elem in elements.values():
            data = elem.data
            if data.get("type") == "way":
                trk = ET.SubElement(gpx, "trk")
                ET.SubElement(trk, "name").text = data.get("tags", {}).get(
                    "name", "Way"
                )

                trkseg = ET.SubElement(trk, "trkseg")
                for n_id in data.get("nodes", []):
                    node = elements.get(n_id)
                    if node:
                        nd = node.data
                        ET.SubElement(
                            trkseg,
                            "trkpt",
                            lat=str(nd.get("lat")),
                            lon=str(nd.get("lon")),
                        )

        tree = ET.ElementTree(gpx)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def export_to_geojson(filepath, elements):
        """Export nodes, ways, relations to GeoJSON FeatureCollection."""

        features = []

        for elem in elements.values():
            data = elem.data
            elem_type = data.get("type")

            # Node → Point
            if elem_type == "node":
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [data.get("lon"), data.get("lat")],
                        },
                        "properties": data.get("tags", {}),
                    }
                )

            # Way → LineString
            elif elem_type == "way":
                coords = []
                for n_id in data.get("nodes", []):
                    node = elements.get(n_id)
                    if node:
                        nd = node.data
                        coords.append([nd.get("lon"), nd.get("lat")])

                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": coords},
                        "properties": data.get("tags", {}),
                    }
                )

            # Relation → MultiLineString or MultiPoint (simple fallback)
            elif elem_type == "relation":
                members = []
                for member in data.get("members", []):
                    ref = member.get("ref")
                    node = elements.get(ref)
                    if node:
                        nd = node.data
                        members.append([nd.get("lon"), nd.get("lat")])

                features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "MultiPoint",
                            "coordinates": members,
                        },
                        "properties": data.get("tags", {}),
                    }
                )

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)
