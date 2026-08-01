import lxml.etree as ET


class Way:
    """Class to represent an OSM way."""

    def __init__(self, raw):
        """The constructor uses the raw dictionary of the OSM server answer.

        Args:
            raw (dict): OSM server result for this object.
        """
        self.raw = raw.copy()
        self.id = self.raw["id"]

        self.data = dict(
            id=str(self.raw["id"]),
            uid=str(self.raw["uid"]),
            user=str(self.raw["user"]),
            version=str(self.raw["version"]),
            changeset=str(self.raw["changeset"]),
            timestamp=str(self.raw["timestamp"]),
            type="way",
            nodes=self.raw.get("nodes", []),
        )

        if "tags" in self.raw:
            self.data["tags"] = self.raw["tags"].copy()
        else:
            self.data["tags"] = dict()

    def create_xml(self, id, changeset=None, tags=True):
        """Create XML representation of the way."""
        if not changeset:
            changeset = self.data["changeset"]

        xml_way = ET.Element(
            "way",
            id=str(id),
            changeset=str(changeset),
            version=str(self.data["version"]),
        )

        for node_id in self.data["nodes"]:
            ET.SubElement(xml_way, "nd", ref=str(node_id))

        if tags:
            for key, value in self.data["tags"].items():
                ET.SubElement(xml_way, "tag", k=key, v=value)

        return xml_way

    def __str__(self):
        return ET.tostring(self.create_xml(self.id)).decode()
