from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ShortcutDialog(QDialog):
    """Dialog showing available keyboard shortcuts and controls."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super(ShortcutDialog, self).__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(450, 350)

        layout = QVBoxLayout(self)

        table = QTableWidget(self)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Action", "Shortcut / Control"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        shortcuts = [
            ("Pan Map", "Left Click + Drag"),
            ("Zoom In / Out", "Mouse Wheel / Plus (+) / Minus (-)"),
            ("Reload Tiles & Elements", "F5"),
            ("Select Element", "Right Click on Node"),
            ("Move Selected Node", "Arrow Keys (Up, Down, Left, Right)"),
            ("Create New Node", "Tools -> Create Node (then Right Click)"),
            ("Export OSM Data", "File -> Export to OSM..."),
        ]

        table.setRowCount(len(shortcuts))
        for row, (action, shortcut) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(shortcut))

        layout.addWidget(table)

        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
