import ctypes
import os
import sys
from functools import partial
from importlib import resources
from subprocess import call

from PySide6 import QtCore
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QToolBar,
    QUndoView,
)

from osmapy.Changeset.Changeset import Changeset
from osmapy.Changeset.ChangesetForm import ChangesetForm
from osmapy.ElementsLoader.ElementsLoader import ElementsLoader
from osmapy.utils.config import load_config
from osmapy.utils.Export import Exporter
from osmapy.Viewer.ElementViewer import ElementViewer
from osmapy.Viewer.LayerManager import LayerManager
from osmapy.Viewer.ShortcutDialog import ShortcutDialog
from osmapy.Viewer.Viewer import Viewer


class Main(QMainWindow):
    """MainWindow which contains all widgets of Osmapy."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super(Main, self).__init__(parent)
        self.config = load_config()
        self.setWindowTitle("Osmapy")
        icon_path = resources.files("osmapy.assets") / "appicon.png"
        self.setWindowIcon(QIcon(str(icon_path)))
        # All widgets should be destroyed when the main window is closed.
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.resize(self.config.window_size[0], self.config.window_size[1])

        self.elements_loader = ElementsLoader()

        # Element Viewer as DockWidget
        self.element_viewer = ElementViewer(self)
        self.dock_element_viewer = QDockWidget()
        self.dock_element_viewer.setWindowTitle("Element Viewer")
        self.dock_element_viewer.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.dock_element_viewer.setWidget(self.element_viewer)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock_element_viewer
        )

        # LayerManager as DockWidget
        self.layer_manager = LayerManager(self)
        self.dock_layer_manager = QDockWidget()
        self.dock_layer_manager.setWindowTitle("Layer Manager")
        self.dock_layer_manager.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetMovable
        )
        self.dock_layer_manager.setWidget(self.layer_manager)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock_layer_manager
        )

        self.viewer = Viewer(self)
        self.setCentralWidget(self.viewer)
        self.viewer.setFocus()
        self.viewer.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self.undo_view = QUndoView(self.viewer.undo_stack)
        self.dock_undo = QDockWidget("Undo History", self)
        self.dock_undo.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetMovable
        )
        self.dock_undo.setWidget(self.undo_view)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock_undo)

        self.changeset = Changeset(self)
        self.changeset_form = ChangesetForm(self)

        # Create actions first so they can be shared between Menu Bar and Tool Bar
        self.init_actions()
        self.init_menu_bar()
        self.init_tool_bar()

        self.statusBar().showMessage("Welcome to Osmapy!")

    def init_actions(self) -> None:
        """Initialize core application actions."""
        self.load_action = QAction("Load Elements", self)
        self.load_action.triggered.connect(self.viewer.load_elements)

        # Connect Undo/Redo directly to the viewer's QUndoStack if available
        if hasattr(self.viewer, "undo_stack"):
            self.undo_action = self.viewer.undo_stack.createUndoAction(
                self, "Undo Changes"
            )
            self.undo_action.setShortcut("Ctrl+Z")
            self.redo_action = self.viewer.undo_stack.createRedoAction(
                self, "Redo Changes"
            )
            self.redo_action.setShortcut("Ctrl+Y")
        else:
            self.undo_action = QAction("Undo Changes", self)
            self.undo_action.triggered.connect(self.viewer.undo_changes)
            self.redo_action = QAction("Redo Changes", self)

        self.reload_tiles_action = QAction("Reload Tiles", self)
        self.reload_tiles_action.triggered.connect(self.viewer.reload_tiles)

        self.create_node_action = QAction("Create Node", self)
        self.create_node_action.triggered.connect(
            partial(self.viewer.change_mode, "new_node")
        )

        self.export_action = QAction("Export to OSM...", self)
        self.export_action.triggered.connect(self.export_elements)

        self.shortcuts_action = QAction("Keyboard Shortcuts", self)
        self.shortcuts_action.triggered.connect(self.show_shortcuts)

        self.upload_action = QAction("Upload Changes", self)
        self.upload_action.triggered.connect(self.changeset_form.show)

        if os.name == "nt":
            config_func = partial(os.startfile, str(self.config.path_config))
        elif sys.platform == "darwin":
            config_func = partial(call, ["open", str(self.config.path_config)])
        else:
            config_func = partial(call, ["xdg-open", str(self.config.path_config)])

        self.config_action = QAction("Open Configuration", self)
        self.config_action.triggered.connect(config_func)

        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)

    def init_menu_bar(self) -> None:
        """Organize clean dropdown categories in the Menu Bar."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.config_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        if hasattr(self, "redo_action"):
            edit_menu.addAction(self.redo_action)

        # View Menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.load_action)
        view_menu.addAction(self.reload_tiles_action)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.create_node_action)
        tools_menu.addAction(self.upload_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.shortcuts_action)

    def init_tool_bar(self) -> None:
        """Keep the primary toolbar clean and focused."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.addAction(self.load_action)
        self.toolbar.addAction(self.reload_tiles_action)
        self.toolbar.addAction(self.undo_action)
        if hasattr(self, "redo_action"):
            self.toolbar.addAction(self.redo_action)
        self.toolbar.addAction(self.create_node_action)
        self.toolbar.addAction(self.upload_action)
        self.addToolBar(self.toolbar)

    def export_elements(self) -> None:
        """Open a file dialog to save currently loaded elements in various formats."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            "OSM Files (*.osm);;GPX Files (*.gpx);;GeoJSON Files (*.geojson);;All Files (*)",
        )

        if not filepath:
            return

        elements = self.elements_loader.elements

        # Determine format by extension
        if filepath.endswith(".osm"):
            Exporter.export_to_osm(filepath, elements)
            fmt = "OSM XML"

        elif filepath.endswith(".gpx"):
            Exporter.export_to_gpx(filepath, elements)
            fmt = "GPX"

        elif filepath.endswith(".geojson"):
            Exporter.export_to_geojson(filepath, elements)
            fmt = "GeoJSON"

        else:
            # Default fallback: export OSM
            Exporter.export_to_osm(filepath, elements)
            fmt = "OSM XML (default)"

        self.statusBar().showMessage(f"Successfully exported {fmt} to {filepath}", 5000)

    def show_shortcuts(self) -> None:
        """Open the keyboard shortcuts reference dialog."""
        dialog = ShortcutDialog(self)
        dialog.exec()


def main() -> None:
    # Starting point of Osmapy
    app = QApplication(sys.argv)
    app.setApplicationName("Osmapy")
    # Show the icon in the windows taskbar
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("osmapy")
    main_window = Main()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
