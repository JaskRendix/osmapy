import webbrowser
from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np
from PySide6 import QtCore
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QUndoStack,
    QWheelEvent,
)
from PySide6.QtWidgets import QApplication, QDialog, QUndoView

from osmapy.GPXLoader.GPXLoader import GPXLoader
from osmapy.TileLoader import Tile, TileLoader
from osmapy.utils import calc
from osmapy.utils.config import load_config
from osmapy.Viewer.OSMCopyright import OSMCopyright

config = load_config()


class Viewer(QDialog):
    """Viewer widget where the map is shown with the slippy tiles in the background and OSM objects."""

    def __init__(self, parent: Any | None = None) -> None:
        super(Viewer, self).__init__()

        self.tile_loaders: list[Any] = []
        for config_id in range(len(config.slippy_tiles)):
            self.tile_loaders.append(TileLoader.TileLoader(self, config_id))
        self.parent: Any | None = parent
        self.element_viewer: Any = self.parent.element_viewer

        self.lat: float = config.start_latitude
        self.lon: float = config.start_longitude
        self.zoom: int = config.start_zoom
        self.x, self.y = calc.deg2xy(self.lat, self.lon)

        # scale
        tile = Tile.Tile(self.lat, self.lon, self.zoom)
        self.scale_x: float = config.image_size / tile.width_x
        self.scale_y: float = config.image_size / tile.width_y

        self.click: bool = False

        self.elements_loader: Any = self.parent.elements_loader

        for tile_loader in self.tile_loaders:
            self.destroyed.connect(tile_loader.close)

        error_path = resources.files("osmapy.assets") / "error.png"
        self.asset_error_image: str = str(error_path)

        self.osm_copyright: OSMCopyright = OSMCopyright()

        self.setAcceptDrops(True)  # allow file dropping

        self.layers: Any = self.parent.layer_manager
        for config_id, tile_loader in enumerate(self.tile_loaders):
            self.layers.add_layer(
                tile_loader,
                config.slippy_tiles[config_id].name,
                config.slippy_tiles[config_id].enabled,
            )
        self.layers.add_layer(self.elements_loader, "OSM Nodes")

        self.mode: str = "normal"  # mode for clicking events

        self.undo_stack: QUndoStack = QUndoStack(self)
        self.undo_view = QUndoView(self.undo_stack)
        self.undo_view.setWindowTitle("Command History")

    def set_deg(self, lat: float, lon: float) -> None:
        """Set center of the view.

        Args:
            lat (float): latitude of the center
            lon (float): longitude of the center
        """
        self.lat = lat
        self.lon = lon
        self.x, self.y = calc.deg2xy(self.lat, self.lon)
        self.set_zoom(self.zoom)

    def set_xy(self, x: float, y: float) -> None:
        """Set center of the view.

        Args:
            x (float): mercator x of the center
            y (float): mercator y of the center
        """
        self.x = x
        self.y = y
        self.lat, self.lon = calc.xy2deg(self.x, self.y)
        self.set_zoom(self.zoom)

    def set_zoom(self, zoom: int) -> None:
        """Set zoom level of the view.

        Args:
            zoom (int): zoom level
        """
        self.zoom = zoom
        self.parent.statusBar().showMessage(
            f"Lat: {self.lat:.7f} Lon: {self.lon:.7f} Zoom: {zoom}"
        )
        tile = Tile.Tile(self.lat, self.lon, self.zoom)
        self.scale_x = config.image_size / tile.width_x
        self.scale_y = config.image_size / tile.width_y

    def screen2xy(self, xscreen: float, yscreen: float) -> tuple[float, float]:
        """Convert from screen coordinates to mercator coordinates.

        Args:
            xscreen (float): x coordinate on view
            yscreen (float): y coordinate on view

        Returns:
            (float, float): mercator x and y
        """
        xscreen -= self.frameGeometry().width() / 2
        yscreen -= self.frameGeometry().height() / 2
        yscreen *= -1
        xscreen /= self.scale_x
        yscreen /= self.scale_y

        xscreen += self.x
        yscreen += self.y

        return xscreen, yscreen

    def xy2screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert mercator x and y to screen coordinates.

        Args:
            x (float): mercator x
            y (float): mercator y

        Returns:
            (float, float): coordinates on the view
        """
        xscreen = (x - self.x) * self.scale_x + self.frameGeometry().width() / 2
        yscreen = -(y - self.y) * self.scale_y + self.frameGeometry().height() / 2
        return xscreen, yscreen

    def paintEvent(self, event: Any) -> None:
        """This is triggered on every update. All the connected layers are drawn here. Also the copyright information
        is added here.

        Args:
            event (Event): not yet used
        """
        qpainter = QPainter(self)
        qpainter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for layer, alpha in self.layers.get_layers():
            layer.draw(self, qpainter, alpha)

        qpainter.setBrush(QColor(0, 0, 0, 0))
        qpainter.setPen(QPen(QColor(QtCore.Qt.GlobalColor.black), 1))
        size = 4
        qpainter.drawRect(
            -size / 2 + self.frameGeometry().width() * 0.5,
            -size / 2 + self.frameGeometry().height() * 0.5,
            size,
            size,
        )

        # draw OSM information
        self.osm_copyright.draw(self, qpainter)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Callback when the mouse wheel is used. Here the zooming is realized.

        Args:
            event (Event): scrolling event includes the amount of scrolling
        """
        angle_delta = event.angleDelta().y()
        if angle_delta != 0:
            delta = angle_delta // abs(angle_delta)
            if delta > 0 and self.zoom < 19:
                self.set_zoom(self.zoom + 1)
                self.update()
            elif delta < 0 and self.zoom > 0:
                self.set_zoom(self.zoom - 1)
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Callback when the mouse is moved. Here the dragging of the map is realized.

        Args:
            event (Event): contains the position of the mouse
        """
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            if not self.click:
                self.start = event.globalPosition().toPoint()
                self.click = True
                self.start_x = self.x
                self.start_y = self.y
            else:
                moved = event.globalPosition().toPoint() - self.start
                set_x = self.start_x - moved.x() / self.scale_x
                set_y = self.start_y + moved.y() / self.scale_y

                set_x = float(np.clip(set_x, -179.999999, 179.999999))
                set_y = float(np.clip(set_y, -179.999999, 179.999999))

                self.set_xy(set_x, set_y)
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Callback when the mouse is released. This is needed to realize the dragging.

        Args:
            event (Event): not yet used
        """
        self.click = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Callback when the mouse is clicked. This is use to react on a click on the OSM copyright, select a node
        or create a new node.

        Args:
            event (Event): contains the click information
        """
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            # click on copyright
            if (
                event.position().x()
                > self.frameGeometry().width()
                - self.osm_copyright.width
                - self.osm_copyright.margin
                and event.position().y()
                > self.frameGeometry().height()
                - self.osm_copyright.height
                - self.osm_copyright.margin
            ):
                webbrowser.open(self.osm_copyright.url)
                return

        if self.mode == "normal":
            if event.buttons() == QtCore.Qt.MouseButton.RightButton:
                posx = event.position().x()
                posy = event.position().y()
                smallest = 9999999
                elem_id = None

                for key, elem in self.elements_loader.elements.items():
                    # Nodes have x/y, ways do not
                    if hasattr(elem, "x") and hasattr(elem, "y"):
                        xscreen, yscreen = self.xy2screen(elem.x, elem.y)
                    else:
                        # Compute centroid for ways/relations
                        xs = []
                        ys = []
                        if hasattr(elem, "nodes"):
                            for nid in elem.nodes:
                                n = self.elements_loader.elements.get(nid)
                                if n:
                                    xs.append(n.x)
                                    ys.append(n.y)
                        if xs and ys:
                            xscreen, yscreen = self.xy2screen(
                                sum(xs) / len(xs), sum(ys) / len(ys)
                            )
                        else:
                            continue

                    dist = np.sqrt((xscreen - posx) ** 2 + (yscreen - posy) ** 2)
                    if dist < smallest:
                        elem_id = key
                        smallest = dist

                if elem_id:
                    self.elements_loader.selected_node = elem_id
                    self.update()
                    self.element_viewer.set_node(self.elements_loader.elements[elem_id])

        elif self.mode == "new_node":
            if event.buttons() == QtCore.Qt.MouseButton.RightButton:
                x, y = self.screen2xy(event.position().x(), event.position().y())
                lat, lon = calc.xy2deg(x, y)
                self.elements_loader.new_node(lat, lon)
                self.update()
                self.change_mode("normal")

    def dragEnterEvent(self, event: Any) -> None:
        """This callback is fired when something is dragged above the view. It is shown to the user that this is
        accepted to allow dropping GPX files.

        Args:
            event (Event): information of the dragged object
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: Any) -> None:
        """Event when something is dropped into the view. This is used to read GPX files.

        Args:
            event (Event): includes the dropping metadata
        """
        path = Path(event.mimeData().urls()[0].toLocalFile())
        self.layers.add_layer(GPXLoader(path), event.mimeData().urls()[0].toLocalFile())

        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Callback for keypress events. This is used to move the selected object around. this scales with the zoom
        level.

        Args:
            event (Event): contains the information of the pressed key
        """
        if self.parent.elements_loader.selected_node:
            node_id = self.parent.elements_loader.selected_node
            node = self.parent.elements_loader.elements[node_id]
            if event.key() == QtCore.Qt.Key.Key_Right:
                node.set_position(node.x + 1 / self.scale_x, node.y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key.Key_Left:
                node.set_position(node.x - 1 / self.scale_x, node.y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key.Key_Up:
                node.set_position(node.x, node.y + 1 / self.scale_y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()
            if event.key() == QtCore.Qt.Key.Key_Down:
                node.set_position(node.x, node.y - 1 / self.scale_y)
                self.element_viewer.set_node(self.elements_loader.elements[node_id])
                self.update()

        # Zooming
        if event.key() == QtCore.Qt.Key.Key_Plus:
            if self.zoom < 19:
                self.set_zoom(self.zoom + 1)
                self.update()
        if event.key() == QtCore.Qt.Key.Key_Minus:
            if self.zoom > 0:
                self.set_zoom(self.zoom - 1)
                self.update()
        # Reload Tiles shortcut
        if event.key() == QtCore.Qt.Key.Key_F5:
            self.reload_tiles()

    def load_elements(self) -> None:
        """Start loading OSM elements from the api which belong in the current map view."""
        left, top = self.screen2xy(0, 0)
        right, bottom = self.screen2xy(
            self.frameGeometry().width(), self.frameGeometry().height()
        )
        north, west = calc.xy2deg(left, bottom)
        south, east = calc.xy2deg(right, top)
        self.elements_loader.load(west, north, east, south)

        self.update()

    def undo_changes(self) -> None:
        """Undo the changes of the nodes."""
        self.parent.element_viewer.clear()
        self.parent.elements_loader.clear()
        self.update()
        self.load_elements()

    def change_mode(self, mode: str) -> None:
        """Changes what happens when the mouse is clicked in the view. Also changes the cursor style.

        Args:
            mode (str): humanreadable mode code
        """
        self.parent.setToolTip("")
        if mode == "new_node":
            self.parent.setToolTip("Right Click to create Node")
            QApplication.setOverrideCursor(QtCore.Qt.CursorShape.CrossCursor)
        if mode == "normal":
            QApplication.restoreOverrideCursor()
        self.mode = mode

    def reload_tiles(self) -> None:
        """Force a reload/refresh of all active slippy tile loaders and update the viewer."""
        for tile_loader in self.tile_loaders:
            if hasattr(tile_loader, "clear"):
                tile_loader.clear()
        self.load_elements()
        self.update()
