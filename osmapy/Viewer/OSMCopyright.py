from typing import TYPE_CHECKING

from PySide6.QtCore import QRect
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QStaticText

if TYPE_CHECKING:
    from osmapy.Viewer.Viewer import Viewer


class OSMCopyright:
    """Class for the OSM copyright in the right bottom corner of the map."""

    def __init__(self) -> None:
        self.margin: int = 2
        self.url: str = "https://www.openstreetmap.org/copyright"

        self.copyright_text: QStaticText = QStaticText("© OpenStreetMap contributors")
        self.font: QFont = QFont()
        self.font.setPointSize(8)
        self.copyright_text.prepare(font=self.font)

        size = self.copyright_text.size()
        # Normalize width/height to integers
        self.width: int = int(size.width()) + self.margin
        self.height: int = int(size.height()) + self.margin
        self.rect: QRect = QRect()

    def draw(self, viewer: "Viewer", qpainter: QPainter) -> None:
        qpainter.setFont(self.font)

        vw = viewer.frameGeometry().width()
        vh = viewer.frameGeometry().height()

        # Compute integer geometry
        x = int(vw - self.width - self.margin)
        y = int(vh - self.height - self.margin)
        w = int(self.width + self.margin)
        h = int(self.height + self.margin)

        self.rect = QRect(x, y, w, h)

        qpainter.fillRect(self.rect, QBrush(QColor(255, 255, 255)))

        qpainter.drawStaticText(
            int(vw - self.width),
            int(vh - self.height),
            self.copyright_text,
        )
