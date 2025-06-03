# qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QHeaderView,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtGui import Qt


# Table with pagination to browse artist's releases
class ReleaseGroupBrowser(QWidget):
    COLUMN_COUNT = 4
    COLUMN_HEADERS = ['Title', 'Type', 'Release Year', '']

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.curr_page = 1
        self.page_count = 1

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(self.COLUMN_COUNT)
        self.table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Replaces table if empty
        self.empty_label = QLabel('No releases found.', self)
        self.empty_label.setStyleSheet('font-size: 14px; color: gray;')
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

        # Page navigation
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton('Previous', self)
        self.prev_button.setDisabled(True)
        self.page_count_label = QLabel(self)
        self.next_button = QPushButton('Next', self)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_count_label)
        pagination_layout.addWidget(self.next_button)
        self.pagination_buttons = QWidget(self)
        self.pagination_buttons.setLayout(pagination_layout)
        layout.addWidget(self.pagination_buttons)
