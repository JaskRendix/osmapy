import pytest
from PySide6.QtWidgets import QDockWidget

from osmapy.main import Main
from osmapy.Viewer.ShortcutDialog import ShortcutDialog


@pytest.fixture
def main_window(qtbot):
    window = Main()
    qtbot.addWidget(window)
    window.show()
    return window


def test_main_window_initialization(main_window):
    assert main_window.windowTitle() == "Osmapy"
    assert main_window.centralWidget() is not None
    assert main_window.statusBar().currentMessage() == "Welcome to Osmapy!"


def test_main_window_docks(main_window):
    docks = main_window.findChildren(QDockWidget)
    dock_titles = {dock.windowTitle() for dock in docks}

    assert "Element Viewer" in dock_titles
    assert "Layer Manager" in dock_titles


def test_main_window_actions_and_menus(main_window):
    menubar = main_window.menuBar()
    menu_titles = [action.text() for action in menubar.actions()]

    assert any("File" in title for title in menu_titles)
    assert any("Edit" in title for title in menu_titles)
    assert any("View" in title for title in menu_titles)
    assert any("Tools" in title for title in menu_titles)
    assert any("Help" in title for title in menu_titles)

    assert main_window.load_action is not None
    assert main_window.export_action is not None
    assert main_window.shortcuts_action is not None


def test_show_shortcuts_dialog(main_window, qtbot):
    # Use qtbot.keyClick or direct execution handling since ShortcutDialog.exec() is modal
    with qtbot.wait_exposed(main_window):
        pass

    # Use a helper callback to handle the modal dialog execution loop cleanly
    def handle_dialog():
        dialog = main_window.findChild(ShortcutDialog)
        if dialog is not None:
            dialog.accept()

    QtCore_timer = __import__("PySide6.QtCore", fromlist=["QTimer"]).QTimer
    QtCore_timer.singleShot(100, handle_dialog)

    # Triggering the action calls dialog.exec(), which blocks until closed
    main_window.shortcuts_action.trigger()
