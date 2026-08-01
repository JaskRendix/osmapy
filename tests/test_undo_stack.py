from unittest.mock import MagicMock

from osmapy.utils.UndoStack import MoveNodeCommand


def test_move_node_command_initialization():
    node = MagicMock()
    node.data = {"id": 42}
    old_pos = (46.0, 8.9)
    new_pos = (46.1, 9.0)
    viewer = MagicMock()

    cmd = MoveNodeCommand(node, old_pos, new_pos, viewer)

    assert cmd.node == node
    assert cmd.old_pos == old_pos
    assert cmd.new_pos == new_pos
    assert cmd.viewer == viewer
    assert cmd.text() == "Move Node 42"


def test_move_node_command_redo():
    node = MagicMock()
    node.data = {"id": 42, "lat": 46.0, "lon": 8.9}
    old_pos = (46.0, 8.9)
    new_pos = (46.1, 9.0)
    viewer = MagicMock()

    cmd = MoveNodeCommand(node, old_pos, new_pos, viewer)
    cmd.redo()

    assert node.data["lat"] == 46.1
    assert node.data["lon"] == 9.0
    viewer.update.assert_called_once()


def test_move_node_command_undo():
    node = MagicMock()
    node.data = {"id": 42, "lat": 46.1, "lon": 9.0}
    old_pos = (46.0, 8.9)
    new_pos = (46.1, 9.0)
    viewer = MagicMock()

    cmd = MoveNodeCommand(node, old_pos, new_pos, viewer)
    cmd.undo()

    assert node.data["lat"] == 46.0
    assert node.data["lon"] == 8.9
    viewer.update.assert_called_once()
