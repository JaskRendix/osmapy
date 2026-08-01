class Relation:
    """Class representing an OSM Relation element."""

    def __init__(self, data):
        self.data = data

    @classmethod
    def create_new_relation(cls, rel_id, members=None, tags=None):
        """Create a new local relation object."""
        data = {
            "type": "relation",
            "id": rel_id,
            "members": members if members else [],
            "tags": tags if tags else {},
        }
        return cls(data)
