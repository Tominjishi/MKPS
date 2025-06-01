# qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class EditArtistGenreRow(QWidget):
    def __init__(self, row_dict):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(row_dict['name']))
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        layout.addWidget(self.remove_button)
        layout.addStretch()