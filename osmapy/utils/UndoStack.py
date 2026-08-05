from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from osmapy.ElementsLoader.Node import Node
    from osmapy.Viewer.Viewer import Viewer


class MoveNodeCommand(QUndoCommand):
    """Undo command for moving a node to a new position."""

    node: Node
    old_pos: tuple[float, float]
    new_pos: tuple[float, float]
    viewer: Viewer

    def __init__(
        self,
        node: Node,
        old_pos: tuple[float, float],
        new_pos: tuple[float, float],
        viewer: Viewer,
    ) -> None:
        super().__init__()
        self.node = node
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.viewer = viewer
        self.setText(f"Move Node {node.data.get('id')}")

    def undo(self) -> None:
        self.node.data["lat"] = self.old_pos[0]
        self.node.data["lon"] = self.old_pos[1]
        self.viewer.update()

    def redo(self) -> None:
        self.node.data["lat"] = self.new_pos[0]
        self.node.data["lon"] = self.new_pos[1]
        self.viewer.update()
