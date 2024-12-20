from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QHeaderView,
    QLabel,
    QHBoxLayout,
    QPushButton
)
from PySide6.QtGui import Qt

class ReleaseGroupBrowser(QWidget):
    COLUMN_COUNT = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.currPage = 1
        self.pageCount = 1

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(self.COLUMN_COUNT)
        self.table.setHorizontalHeaderLabels(['Title', 'Type', 'Release Year',''])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Replaces table if empty
        self.emptyLabel = QLabel('No releases found.', self)
        self.emptyLabel.setStyleSheet('font-size: 14px; color: gray;')
        self.emptyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Page navigation
        paginationLayout = QHBoxLayout()
        self.prevButton = QPushButton('Previous', self)
        self.prevButton.setDisabled(True)
        self.pageLabel = QLabel(self)
        self.nextButton = QPushButton('Next', self)
        paginationLayout.addWidget(self.prevButton)
        paginationLayout.addWidget(self.pageLabel)
        paginationLayout.addWidget(self.nextButton)
        self.paginationButtons = QWidget(self)
        self.paginationButtons.setLayout(paginationLayout)

        layout.addWidget(self.table)
        layout.addWidget(self.emptyLabel)
        layout.addWidget(self.paginationButtons)