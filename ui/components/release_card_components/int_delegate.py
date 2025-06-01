# qt
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtGui import QIntValidator


# Class for creating integer delegator to limit track list length inputs to integers
class IntDelegate(QStyledItemDelegate):
    def __init__(self, minimum=0, maximum=999, parent=None):
        super().__init__(parent)
        self.min = minimum
        self.max = maximum

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(self.min, self.max, parent))
        return editor