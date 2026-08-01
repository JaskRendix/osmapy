from PySide6.QtGui import QUndoCommand


class MoveNodeCommand(QUndoCommand):
    def __init__(self, node, old_pos, new_pos, viewer):
        super().__init__()
        self.node = node
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.viewer = viewer
        self.setText(f"Move Node {node.data.get('id')}")

    def undo(self):
        self.node.data["lat"] = self.old_pos[0]
        self.node.data["lon"] = self.old_pos[1]
        self.viewer.update()

    def redo(self):
        self.node.data["lat"] = self.new_pos[0]
        self.node.data["lon"] = self.new_pos[1]
        self.viewer.update()
