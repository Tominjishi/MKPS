# qt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QComboBox, QDialogButtonBox


# Basic dialog for inserting new table row with name input and type choice for artist
class SimpleInsertDialog(QDialog):
    def __init__(self, parent, title, is_artist=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.inserted_id = None
        # self.setBaseSize(QSize(300, 100))
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        name_label = QLabel('Name: ')
        self.name_input = QLineEdit()
        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        self.is_artist = is_artist
        if self.is_artist:
            type_label = QLabel('Type: ')
            self.type_dropdown = QComboBox()
            self.type_dropdown.addItem('')
            self.type_dropdown.addItem('Person')
            self.type_dropdown.addItem('Group')
            type_layout = QHBoxLayout()
            type_layout.addWidget(type_label)
            type_layout.addWidget(self.type_dropdown)
            layout.addLayout(type_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.adjustSize()

    def clear(self):
        self.name_input.clear()
        if self.is_artist:
            self.type_dropdown.setCurrentIndex(0)
