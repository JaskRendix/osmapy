from string import Template
from typing import Any

import numpy as np
import requests
from PySide6 import QtCore
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QMessageBox

from osmapy.ElementsLoader import Node, Relation, Way
from osmapy.utils import calc
from osmapy.utils.config import load_config

config = load_config()


class ElementsLoader:
    """This class provides a loader for OSM elements from the OSM server."""

    def __init__(self) -> None:
        self.elements_copy: dict[int | str, Any] = {}
        self.elements: dict[int | str, Any] = {}
        self.headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": config.user_agent,
        }
        self.x_coords: list[float] = []
        self.y_coords: list[float] = []
        self.lons: np.ndarray | None = None
        self.selected_node: int | str | None = None
        self.new_node_counter: int = -1
        self.new_elements_loaded: bool = False

    def clear(self) -> None:
        """Reset the elements dicts and the counter"""
        self.selected_node = None
        self.new_node_counter = -1
        self.elements_copy = {}
        self.elements = {}
        self.x_coords = []
        self.y_coords = []
        self.lons = None

    def load(self, west: float, north: float, east: float, south: float) -> None:
        """This function loads all node, way, and relation elements from a given bounding box."""
        url = config.osm_api_url + "/api/0.6/map?bbox=${west},${north},${east},${south}"
        request = Template(url)
        request = request.substitute(west=west, north=north, east=east, south=south)
        result = requests.get(request, headers=self.headers)

        if result.ok:
            result_json = result.json()

            # Parse Nodes, Ways, and Relations
            loaded_elements = {}
            for raw in result_json["elements"]:
                if raw["type"] == "node":
                    loaded_elements[raw["id"]] = Node.Node(raw)
                elif raw["type"] == "way":
                    loaded_elements[raw["id"]] = Way.Way(raw)
                elif raw["type"] == "relation":
                    loaded_elements[raw["id"]] = Relation.Relation(raw)

            self.elements_copy = {**self.elements_copy, **loaded_elements}
            self.elements = {**self.elements, **loaded_elements}

            for elem_key in self.elements:
                elem = self.elements[elem_key]
                if elem.data["type"] == "node":
                    elem.data["lat"] = float(elem.data["lat"])
                    elem.data["lon"] = float(elem.data["lon"])

            self.new_elements_loaded = True
        else:
            box = QMessageBox()
            box.setWindowTitle("Error")
            box.setText(
                "Maybe you have to zoom in because there are too many objects in this area"
            )
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()

    def new_node(self, lat: float, lon: float) -> None:
        """Add new node to the elements list."""
        self.elements[self.new_node_counter] = Node.Node.create_new_node(
            self.new_node_counter, lat, lon
        )
        self.new_node_counter -= 1

    def draw(self, viewer: Any, qpainter: QPainter, alpha: float) -> None:
        """Function to draw nodes and ways on a View."""
        qpainter.setOpacity(alpha)

        # 1. Draw Ways first (so nodes sit on top)
        qpainter.setPen(QPen(QColor(100, 100, 250), 3))
        for elem in self.elements.values():
            if elem.data["type"] == "way":
                node_ids = elem.data["nodes"]
                points = []
                for n_id in node_ids:
                    if (
                        n_id in self.elements
                        and self.elements[n_id].data["type"] == "node"
                    ):
                        n_elem = self.elements[n_id]
                        x_val, y_val = calc.deg2xy(
                            n_elem.data["lat"], n_elem.data["lon"]
                        )
                        xscreen, yscreen = viewer.xy2screen(x_val, y_val)
                        points.append(QtCore.QPointF(xscreen, yscreen))

                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        qpainter.drawLine(points[i], points[i + 1])

        # 2. Draw Nodes
        if self.new_elements_loaded:
            lats = np.array(
                [
                    x.data["lat"]
                    for x in self.elements.values()
                    if x.data["type"] == "node"
                ]
            )
            lons = np.array(
                [
                    x.data["lon"]
                    for x in self.elements.values()
                    if x.data["type"] == "node"
                ]
            )
            self.lons = lons
            x = lons
            y = (
                180.0
                / np.pi
                * np.log(np.tan(np.pi / 4.0 + lats * (np.pi / 180.0) / 2.0))
            )
            self.y_coords = y.tolist()
            self.x_coords = x.tolist()
        else:
            x = np.array(self.x_coords)
            y = np.array(self.y_coords)

        if len(x) == 0 or len(y) == 0:
            self.new_elements_loaded = False
            return

        xscreen = (
            (x - viewer.x) * viewer.scale_x + viewer.frameGeometry().width() / 2
        ) - 3
        yscreen = (
            -(y - viewer.y) * viewer.scale_y + viewer.frameGeometry().height() / 2
        ) - 3

        coords = np.column_stack((xscreen, yscreen))

        qpainter.setBrush(QColor(QtCore.Qt.GlobalColor.blue))
        qpainter.setPen(QPen(QColor(QtCore.Qt.GlobalColor.black), 1))

        for elem in coords:
            size = 6
            qpainter.drawEllipse(elem[0], elem[1], size, size)

        if self.selected_node and self.selected_node in self.elements:
            selected = self.elements[self.selected_node]
            if selected.data["type"] == "node":
                qpainter.setBrush(QColor(0, 0, 0, 0))
                qpainter.setPen(QPen(QColor(QtCore.Qt.GlobalColor.red), 2))
                size = 10
                x_val, y_val = calc.deg2xy(selected.data["lat"], selected.data["lon"])
                xscreen, yscreen = viewer.xy2screen(x_val, y_val)
                qpainter.drawRect(xscreen - size / 2, yscreen - size / 2, size, size)

        self.new_elements_loaded = False
