from typing import Any

import lxml.etree as ET


class Relation:
    """Class representing an OSM Relation element."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw: dict[str, Any] = raw.copy()
        self.id: int | str = self.raw.get("id", 0)

        self.data: dict[str, Any] = dict(
            id=self.raw.get("id", 0),
            uid=str(self.raw.get("uid", "")),
            user=str(self.raw.get("user", "")),
            version=str(self.raw.get("version", "1")),
            changeset=str(self.raw.get("changeset", "0")),
            timestamp=str(self.raw.get("timestamp", "")),
            type="relation",
            members=self.raw.get("members", []),
        )

        if "tags" in self.raw:
            self.data["tags"] = self.raw["tags"].copy()
        else:
            self.data["tags"] = dict()

    @classmethod
    def create_new_relation(
        cls,
        rel_id: int | str,
        members: list[dict[str, Any]] | None = None,
        tags: dict[str, str] | None = None,
    ) -> "Relation":
        """Create a new local relation object."""
        data = {
            "type": "relation",
            "id": rel_id,
            "version": "1",
            "members": members if members else [],
            "tags": tags if tags else {},
        }
        return cls(data)

    def create_xml(
        self,
        id: int | str,
        changeset: int | str | None = None,
        tags: bool = True,
    ) -> ET.Element:
        """Create XML representation of the relation."""
        if not changeset:
            changeset = self.data.get("changeset", "0")

        xml_relation = ET.Element(
            "relation",
            id=str(id),
            changeset=str(changeset),
            version=str(self.data.get("version", "1")),
        )

        for member in self.data["members"]:
            ET.SubElement(
                xml_relation,
                "member",
                type=str(member.get("type", "")),
                ref=str(member.get("ref", "")),
                role=str(member.get("role", "")),
            )

        if tags:
            for key, value in self.data["tags"].items():
                ET.SubElement(xml_relation, "tag", k=key, v=value)

        return xml_relation

    def __str__(self) -> str:
        return ET.tostring(self.create_xml(self.id)).decode()

    def __eq__(self, other: Any) -> bool:
        """Compare two relation objects by their string XML representation using their actual IDs."""
        if not isinstance(other, Relation):
            return False
        return (
            ET.tostring(self.create_xml(self.id)).decode()
            == ET.tostring(other.create_xml(other.id)).decode()
        )

    def __ne__(self, other: Any) -> bool:
        """Compare two relation objects by their string XML representation."""
        return not self.__eq__(other)
