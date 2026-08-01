import pytest

from osmapy.Viewer.LayerManager import LayerManager


class MockViewer:
    def __init__(self):
        self.updated = False

    def update(self):
        self.updated = True


class MockLayer:
    def draw(self, viewer, painter, alpha):
        pass


@pytest.fixture
def viewer():
    return MockViewer()


@pytest.fixture
def layer_manager(qtbot, viewer):
    manager = LayerManager(viewer)
    qtbot.addWidget(manager)
    manager.show()
    return manager


def test_layer_manager_initialization(layer_manager):
    assert layer_manager.selected_layer is None
    assert layer_manager.layer_widget.count() == 0
    assert layer_manager.alpha_slider.value() == 99


def test_add_layer(layer_manager):
    layer_obj = MockLayer()
    layer_manager.add_layer(layer_obj, "Base Map", state=True)
    layer_manager.add_layer(layer_obj, "Overlay", state=False)

    assert "Base Map" in layer_manager.layers
    assert "Overlay" in layer_manager.layers
    assert layer_manager.layer_widget.count() == 2
    assert layer_manager.layer_widget.item(0).data(0) == "Base Map"


def test_get_layers_filtering(layer_manager):
    layer_obj = MockLayer()
    layer_manager.add_layer(layer_obj, "Layer A", state=True)
    layer_manager.add_layer(layer_obj, "Layer B", state=False)
    layer_manager.add_layer(layer_obj, "Layer C", state=True)

    active_layers = layer_manager.get_layers()
    # Only Layer A and Layer C should be active/returned
    assert len(active_layers) == 2


def test_select_layer_and_controls(layer_manager):
    layer_obj = MockLayer()
    layer_manager.add_layer(layer_obj, "Test Layer", state=True)

    # Manually configure an alpha value for testing retrieval
    layer_manager.layers["Test Layer"]["alpha"] = 0.55

    item = layer_manager.layer_widget.item(0)
    layer_manager.select_layer(item)

    assert layer_manager.selected_layer == "Test Layer"
    assert "Test Layer" in layer_manager.alpha_label.text()
    # Alpha 0.55 translates to slider value 54 (computed as int(0.55 * 100 - 1))
    assert layer_manager.alpha_slider.value() == 54
    assert layer_manager.checkbox_enable.isChecked() is True


def test_slider_changes_opacity(layer_manager, viewer):
    layer_obj = MockLayer()
    layer_manager.add_layer(layer_obj, "Test Layer", state=True)
    layer_manager.select_layer(layer_manager.layer_widget.item(0))

    layer_manager.alpha_slider.setValue(74)  # Sets alpha to (74 + 1) / 100 = 0.75

    assert layer_manager.layers["Test Layer"]["alpha"] == 0.75
    assert viewer.updated is True


def test_checkbox_toggles_state(layer_manager, viewer):
    layer_obj = MockLayer()
    layer_manager.add_layer(layer_obj, "Test Layer", state=True)
    layer_manager.select_layer(layer_manager.layer_widget.item(0))

    # Uncheck the box
    layer_manager.checkbox_enable.setChecked(False)
    assert layer_manager.layers["Test Layer"]["state"] is False
    assert viewer.updated is True

    # Check the box back
    layer_manager.checkbox_enable.setChecked(True)
    assert layer_manager.layers["Test Layer"]["state"] is True
