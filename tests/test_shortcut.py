import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QPushButton, QTableWidget

from osmapy.Viewer.ShortcutDialog import ShortcutDialog


def test_shortcut_dialog_initialization(qtbot):
    dialog = ShortcutDialog()
    qtbot.addWidget(dialog)

    # Verify window properties
    assert dialog.windowTitle() == "Keyboard Shortcuts"

    # Verify table existence and layout configuration
    table = dialog.findChild(QTableWidget)
    assert table is not None
    assert table.columnCount() == 2
    assert table.rowCount() > 0

    # Verify table headers are correctly set
    assert table.horizontalHeaderItem(0).text() == "Action"
    assert table.horizontalHeaderItem(1).text() == "Shortcut / Control"


def test_shortcut_dialog_content_items(qtbot):
    dialog = ShortcutDialog()
    qtbot.addWidget(dialog)

    table = dialog.findChild(QTableWidget)

    # Check sample expected rows
    assert table.item(0, 0).text() == "Pan Map"
    assert table.item(0, 1).text() == "Left Click + Drag"
    assert table.item(2, 0).text() == "Reload Tiles & Elements"
    assert table.item(2, 1).text() == "F5"


def test_shortcut_dialog_close_button(qtbot):
    dialog = ShortcutDialog()
    qtbot.addWidget(dialog)

    close_btn = dialog.findChild(QPushButton)
    assert close_btn is not None
    assert close_btn.text() == "Close"

    # Simulate clicking the close button and verify it accepts/closes the dialog
    with qtbot.waitSignal(dialog.finished, timeout=1000):
        qtbot.mouseClick(close_btn, QtCore.Qt.MouseButton.LeftButton)
