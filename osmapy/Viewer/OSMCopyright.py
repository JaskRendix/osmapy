from PySide6.QtCore import QRect
from PySide6.QtGui import QBrush, QColor, QFont, QStaticText


class OSMCopyright:
    """Class for the OSM copyright in the right bottom corner of the map."""

    def __init__(self):
        self.margin = 2
        self.url = "https://www.openstreetmap.org/copyright"

        self.copyright_text = QStaticText("© OpenStreetMap contributors")
        self.font = QFont()
        self.font.setPointSize(8)
        self.copyright_text.prepare(font=self.font)

        size = self.copyright_text.size()
        # Normalize width/height to integers
        self.width = int(size.width()) + self.margin
        self.height = int(size.height()) + self.margin

    def draw(self, viewer, qpainter):
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
