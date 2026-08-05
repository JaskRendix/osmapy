from typing import Any

import lxml.etree as ET

from osmapy.utils import calc


class Node:
    """Class to represent an OSM node."""

    def __init__(self, raw: dict[str, Any]) -> None:
        """The constructor uses the raw dictionary of the OSM server answer.

        Args:
            raw (dict): OSM server result for this object.
        """
        self.raw: dict[str, Any] = raw.copy()
        self.id: int | str = self.raw["id"]

        self.data: dict[str, Any] = dict(
            id=str(self.raw["id"]),
            uid=str(self.raw.get("uid", "")),
            user=str(self.raw.get("user", "")),
            version=str(self.raw.get("version", "1")),
            changeset=str(self.raw.get("changeset", "0")),
            timestamp=str(self.raw.get("timestamp", "")),
            type="node",
            lat=str(self.raw["lat"]),
            lon=str(self.raw["lon"]),
        )

        if "tags" in self.raw:
            self.data["tags"] = self.raw["tags"].copy()
        else:
            self.data["tags"] = dict()

        self.x: float
        self.y: float
        self.x, self.y = calc.deg2xy(float(self.raw["lat"]), float(self.raw["lon"]))
        self.trigger: bool = False

    @classmethod
    def create_new_node(cls, id: int | str, lat: float, lon: float) -> "Node":
        """Create a new node and add it to the elements list

        Args:
            id (int|str): id of the new element
            lat (float): latitude of the new node
            lon (float): longitude of the new node

        Returns:
            Node: new node object
        """
        new_raw = dict(
            id=id,
            uid="-1",
            user="-1",
            version="0",
            changeset="-1",
            timestamp="-1",
            type="node",
            lat=lat,
            lon=lon,
            tags=dict(),
        )
        return cls(new_raw)

    def create_xml(
        self,
        id: int | str,
        changeset: int | str | None = None,
        tags: bool = True,
    ) -> ET.Element:
        """Create XML representation of the node. Can be used to create a osmChange file.

        Args:
            id (int|str): id which should be shown in the XML
            changeset (int|str, ): changeset ID
            tags (bool): the tags should be omitted when deleting a node
        """
        if not changeset:
            changeset = self.data["changeset"]

        xml_node = ET.Element(
            "node",
            id=str(id),
            changeset=str(changeset),
            version=str(self.data["version"]),
            lat=str(self.data["lat"]),
            lon=str(self.data["lon"]),
        )

        if tags:
            for key, value in self.data["tags"].items():
                ET.SubElement(xml_node, "tag", k=key, v=value)

        return xml_node

    def set_position(self, x: float, y: float) -> None:
        """Set new position of node

        Args:
            x (float): mercator x
            y (float): mercator y
        """
        self.x = x
        self.y = y
        lat, lon = calc.xy2deg(x, y)
        self.data["lat"], self.data["lon"] = str(lat), str(lon)

    def __str__(self) -> str:
        """XML representation of the node.

        Returns:
            str: XML representation as a string
        """
        return ET.tostring(self.create_xml(self.id)).decode()

    def __eq__(self, other: Any) -> bool:
        """Compare two node objects, by their string XML representation.

        Args:
            other (Node): node to compare

        Returns:
            bool
        """
        if not isinstance(other, Node):
            return False
        return (
            ET.tostring(self.create_xml(1)).decode()
            == ET.tostring(other.create_xml(1)).decode()
        )

    def __ne__(self, other: Any) -> bool:
        """Compare two node objects, by their string XML representation.

        Args:
            other (Node): node to compare

        Returns:
            bool
        """
        return not self.__eq__(other)
