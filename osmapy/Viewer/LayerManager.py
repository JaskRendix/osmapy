from typing import TYPE_CHECKING, Any

from PySide6 import QtCore
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QGridLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QWidget,
)

if TYPE_CHECKING:
    from osmapy.Viewer.Viewer import Viewer


class Layers(QListWidget):
    """Class for layer widget to allow update of viewer when order of layers is changed."""

    def __init__(self, viewer: "Viewer") -> None:
        super(Layers, self).__init__()
        self.viewer: "Viewer" = viewer

        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def dropEvent(self, event: QEvent) -> None:
        """Override to update viewer when order changes."""
        super().dropEvent(event)
        self.viewer.update()


class LayerManager(QWidget):
    """Class to manage the layers of a viewer. Allow to change the order of layers by drag and drop."""

    def __init__(self, viewer: "Viewer") -> None:
        super(LayerManager, self).__init__()

        self.selected_layer: str | None = None

        self.viewer: "Viewer" = viewer
        self.layers: dict[str, dict[str, Any]] = dict()

        self.layer_widget: Layers = Layers(self.viewer)
        self.alpha_slider: QSlider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.checkbox_enable: QCheckBox = QCheckBox()
        self.alpha_label: QLabel = QLabel("Select Layer to change Opacity")
        self.enable_label: QLabel = QLabel("Select Layer to enable/disable")

        layout = QGridLayout()
        layout.addWidget(self.layer_widget, 0, 0, 1, 1)
        layout.addWidget(self.alpha_label, 1, 0, 1, 1)
        layout.addWidget(self.alpha_slider, 2, 0, 1, 1)
        layout.addWidget(self.enable_label, 3, 0, 1, 1)
        layout.addWidget(self.checkbox_enable, 4, 0, 1, 1)
        self.setLayout(layout)

        self.layer_widget.itemClicked.connect(self.select_layer)
        self.checkbox_enable.checkStateChanged.connect(self.checkbox_changed)
        self.alpha_slider.valueChanged.connect(self.slider_changed)
        self.alpha_slider.setValue(99)

    def add_layer(self, layer: Any, name: str, state: bool = True) -> None:
        """Add new layer to be managed.

        Args:
            layer (Object): object that implements a draw function.
            name (str): String which is the name of the layer.
            state (bool): initial visibility state of the layer.
        """
        self.layers[name] = {"layer": layer, "alpha": 1.0, "state": state}
        self.layer_widget.addItem(name)

    def get_layers(self) -> list[tuple[Any, float]]:
        """Get list of layers representing the order of the LayerManager in the UI.

        Returns:
            [Objects]: objects which implement a draw function with their opacity
        """
        names = [
            self.layer_widget.item(i).data(0) for i in range(self.layer_widget.count())
        ]
        result = [
            (self.layers[name]["layer"], self.layers[name]["alpha"])
            for name in names
            if name in self.layers and self.layers[name]["state"]
        ]
        return result

    def select_layer(self, item: QListWidgetItem) -> None:
        """Select a layer to change opacity.

        Args:
            item (QListWidgetItem): item of the list
        """
        name = item.data(0)
        self.selected_layer = name
        self.alpha_label.setText(f"Opacity ({self.selected_layer}):")
        self.enable_label.setText(f"Enable/Disable ({self.selected_layer}):")

        # set slider to current value
        value = self.layers[name]["alpha"]
        value_int = int(value * 100 - 1)
        self.alpha_slider.setValue(value_int)

        # set checkbox
        state = self.layers[name]["state"]
        if state:
            self.checkbox_enable.setCheckState(Qt.CheckState.Checked)
        else:
            self.checkbox_enable.setCheckState(Qt.CheckState.Unchecked)

    def slider_changed(self, value: int) -> None:
        """Callback when the opacity slider was moved.

        Args:
            value (int): slider value 0-99
        """
        computed_value = (value + 1) / 100.0
        if self.selected_layer and self.selected_layer in self.layers:
            self.layers[self.selected_layer]["alpha"] = computed_value
        self.viewer.update()

    def checkbox_changed(self) -> None:
        """Callback when the Checkbox is changed. The layer is (not) drawn anymore."""
        if self.selected_layer and self.selected_layer in self.layers:
            if self.checkbox_enable.isChecked():
                self.layers[self.selected_layer]["state"] = True
            else:
                self.layers[self.selected_layer]["state"] = False
            self.viewer.update()
