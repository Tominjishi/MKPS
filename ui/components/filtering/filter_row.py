from PySide6.QtWidgets import QHBoxLayout, QWidget, QCheckBox, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon

BUTTON_SIZE = 25

# Individual row in filter list
class FilterRow(QWidget):
    def __init__(self, name):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox(name)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        self.delete_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)

        self.layout.addWidget(self.checkbox)
        self.layout.addStretch()
        self.layout.addWidget(self.delete_button)
