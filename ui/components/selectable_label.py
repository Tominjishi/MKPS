from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

class SelectableLabel(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setCursor(Qt.CursorShape.IBeamCursor)