from functools import partial
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QFormLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

if TYPE_CHECKING:
    from osmapy.ElementsLoader.Node import Node


class ElementViewer(QWidget):
    """Widget which contains a TextEdit with the information of a selected OSM element."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__()
        self.parent_widget: QWidget | None = parent
        self.node: "Node" | None = None
        self.id: int | str | None = None

        # Widgets
        self.id_label: QLabel = QLabel()
        self.uid_label: QLabel = QLabel()
        self.user_label: QLabel = QLabel()
        self.version_label: QLabel = QLabel()
        self.changeset_label: QLabel = QLabel()
        self.timestamp_label: QLabel = QLabel()

        self.lat_edit: QLineEdit = QLineEdit()
        self.lon_edit: QLineEdit = QLineEdit()

        self.search_bar: QLineEdit = QLineEdit()
        self.tag_container: QWidget = QWidget()
        self.tag_layout: QFormLayout = QFormLayout(self.tag_container)

        self.add_tag_btn: QPushButton = QPushButton("Add Tag")
        self.delete_node_btn: QPushButton = QPushButton("Delete Node")

        # Tag widgets map: key -> (button, value_edit)
        self.tag_widgets: dict[str, tuple[QPushButton, QLineEdit]] = {}

        self.default_label: QLabel = QLabel()
        self.tags_header: QLabel = QLabel()

        self._build_layout()
        self._connect_signals()
        self._show_empty()

    def _build_layout(self) -> None:
        layout = QFormLayout()

        # Default text
        self.default_label = QLabel("Right Click to Select Node")
        self.default_label.setStyleSheet("font-weight: bold")
        layout.addRow(self.default_label)

        # Static node info
        layout.addRow("Id", self.id_label)
        layout.addRow("Uid", self.uid_label)
        layout.addRow("User", self.user_label)
        layout.addRow("Version", self.version_label)
        layout.addRow("Changeset", self.changeset_label)
        layout.addRow("Timestamp", self.timestamp_label)

        # Lat/Lon
        layout.addRow("Latitude", self.lat_edit)
        layout.addRow("Longitude", self.lon_edit)

        # Tags header + filter
        self.tags_header = QLabel()
        self.tags_header.setStyleSheet("font-weight: bold")
        layout.addRow(self.tags_header)

        self.search_bar.setPlaceholderText("Search tags...")
        layout.addRow("Filter", self.search_bar)

        # Tag container
        layout.addRow(self.tag_container)

        # Buttons
        self.add_tag_btn.setShortcut("Ctrl+T")
        layout.addRow(self.add_tag_btn)

        self.delete_node_btn.setShortcut("Del")
        layout.addRow(self.delete_node_btn)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.lat_edit.textChanged.connect(
            partial(self.modify_property, "lat", self.lat_edit)
        )
        self.lon_edit.textChanged.connect(
            partial(self.modify_property, "lon", self.lon_edit)
        )

        self.search_bar.textChanged.connect(self.filter_tags)
        self.add_tag_btn.clicked.connect(self.new_tag)
        self.delete_node_btn.clicked.connect(self.delete_node)

    def _show_empty(self) -> None:
        self.default_label.setVisible(True)
        self._set_node_fields_visible(False)
        self._clear_tags()

    def _set_node_fields_visible(self, visible: bool) -> None:
        for w in (
            self.id_label,
            self.uid_label,
            self.user_label,
            self.version_label,
            self.changeset_label,
            self.timestamp_label,
            self.lat_edit,
            self.lon_edit,
            self.tags_header,
            self.search_bar,
            self.tag_container,
            self.add_tag_btn,
            self.delete_node_btn,
        ):
            w.setVisible(visible)

    def set_node(self, node: "Node") -> None:
        """Update the viewer to show the given node."""
        self.node = node
        self.id = node.id
        self.tag_widgets.clear()

        self.default_label.setVisible(False)
        self._set_node_fields_visible(True)

        # Node info
        self.id_label.setText(str(node.id))
        self.uid_label.setText(str(node.data["uid"]))
        self.user_label.setText(str(node.data["user"]))
        self.version_label.setText(str(node.data["version"]))
        self.changeset_label.setText(str(node.data["changeset"]))
        self.timestamp_label.setText(str(node.data["timestamp"]))

        # Lat/Lon
        self.lat_edit.setText(str(node.data["lat"]))
        self.lon_edit.setText(str(node.data["lon"]))

        # Tags
        tags = node.data["tags"]
        self._update_tags(tags)

    def _clear_tags(self) -> None:
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.tag_widgets.clear()
        self.tags_header.setText("Tags (0)")

    def _update_tags(self, tags: dict[str, str]) -> None:
        self._clear_tags()

        if not tags:
            return

        self.tags_header.setText(f"Tags ({len(tags)})")

        for key in sorted(tags.keys(), key=str.lower):
            self._add_tag_row(key, tags[key])

    def _add_tag_row(self, key: str, value: str) -> None:
        key_btn = QPushButton(key)
        val_edit = QLineEdit(value)

        self.tag_layout.addRow(key_btn, val_edit)

        key_btn.clicked.connect(partial(self.remove_tag, key))
        val_edit.textChanged.connect(partial(self.modify_tag, key))

        self.tag_widgets[key] = (key_btn, val_edit)

    def filter_tags(self, query: str) -> None:
        """Dynamically show/hide tags based on search input."""
        query = query.lower()
        for key, (key_btn, val_edit) in self.tag_widgets.items():
            match = query in key.lower() or query in val_edit.text().lower()
            key_btn.setVisible(match)
            val_edit.setVisible(match)
            key_btn.setStyleSheet("background: #d0ffd0" if match else "")

    def delete_node(self) -> None:
        """Delete the currently selected node."""
        if self.id is None or self.parent_widget is None:
            return

        del self.parent_widget.elements_loader.elements[self.id]
        self.parent_widget.elements_loader.selected_node = None
        self.parent_widget.viewer.update()
        self._show_empty()

    def modify_property(self, field: str, edit_widget: QLineEdit, value: str) -> None:
        """Callback to change a node's property with typechecking."""
        if self.id is None or self.parent_widget is None:
            return

        try:
            parsed_value = float(value)
            if field == "lat" and not (-90.0 <= parsed_value <= 90.0):
                raise ValueError("Latitude must be between -90 and 90")
            if field == "lon" and not (-180.0 <= parsed_value <= 180.0):
                raise ValueError("Longitude must be between -180 and 180")

            edit_widget.setStyleSheet("")
            self.parent_widget.elements_loader.elements[self.id].data[
                field
            ] = parsed_value
            self.parent_widget.viewer.update()

        except ValueError:
            edit_widget.setStyleSheet("border: 2px solid red;")

    def modify_tag(self, key: str, value: str) -> None:
        """Callback to modify a tag."""
        if self.id is None or self.parent_widget is None:
            return

        self.parent_widget.elements_loader.elements[self.id].data["tags"][key] = value
        self.parent_widget.viewer.update()

    def remove_tag(self, key: str) -> None:
        """Remove a tag from an object."""
        if self.id is None or self.parent_widget is None:
            return

        tags = self.parent_widget.elements_loader.elements[self.id].data["tags"]
        if key in tags:
            del tags[key]
            self._update_tags(tags)

    def new_tag(self) -> None:
        """Ask user for key and value of the new tag and create it."""
        if self.id is None or self.parent_widget is None:
            return

        key, ok = QInputDialog.getText(self, "New Tag", "Key")
        if not (ok and key):
            return

        # Validate key
        if " " in key:
            QMessageBox.warning(self, "Invalid key", "Tag keys cannot contain spaces")
            return

        tags = self.parent_widget.elements_loader.elements[self.id].data["tags"]
        if key in tags:
            QMessageBox.warning(self, "Duplicate", "Tag already exists")
            return

        value, ok = QInputDialog.getText(self, "New Tag", "Value")
        if ok and value:
            tags[key] = value
            self._update_tags(tags)
