import gpxpy
from PySide6 import QtCore
from PySide6.QtCore import QLineF
from PySide6.QtGui import QColor, QPen

from osmapy.utils.Point import Point


class GPXLoader:
    def __init__(self, path):
        """Class to manage GPX information.

        Args:
            path (pathlib.Path): path to the gpx file

        """
        self.points = []
        try:
            with open(path, "r", encoding="utf-8") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                self.points = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            pt = Point(point.latitude, point.longitude)
                            self.points.append(pt)
        except Exception as e:
            # TODO error handling
            print(e)

    def draw(self, viewer, qpainter, alpha):
        """Function to draw on a View.

        Args:
            viewer (Viewer): object which must is drawn on and which must be updated
            qpainter (QPainter): object which is used to draw
            alpha (float): opacity to draw
        """
        qpainter.setOpacity(alpha)
        qpainter.setBrush(QColor(QtCore.Qt.GlobalColor.red))
        qpainter.setPen(
            QPen(
                QColor(QtCore.Qt.GlobalColor.red),
                2,
                QtCore.Qt.PenStyle.SolidLine,
                QtCore.Qt.PenCapStyle.RoundCap,
                QtCore.Qt.PenJoinStyle.RoundJoin,
            )
        )

        points = [viewer.xy2screen(point.x, point.y) for point in self.points]
        if len(points) < 2:
            return

        pointsA = points[:-1]
        pointsB = points[1:]

        lines = [
            QLineF(pointA[0], pointA[1], pointB[0], pointB[1])
            for pointA, pointB in zip(pointsA, pointsB)
        ]
        qpainter.drawLines(lines)
