import math
from abc import abstractmethod

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt

class SearchPage(QWidget):
    PAGE_SIZE = 25
    curr_page = 1
    page_count = 1
    user_input = ''

    def __init__(self, main_window, target, column_headers):
        super().__init__(main_window)
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        search_bar = QHBoxLayout()
        search_label = QLabel(f'Search {target}:', self)
        self.search_box = QLineEdit(self)
        search_button = QPushButton('Search', self)
        self.search_box.returnPressed.connect(self.search)
        search_button.clicked.connect(self.search)

        self.pagination = QWidget()
        pagination_layout = QHBoxLayout(self.pagination)
        self.prev_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), '', self.pagination)
        self.prev_button.setDisabled(False)
        self.prev_button.clicked.connect(lambda:self.switch_page(-1))
        pagination_layout.addWidget(self.prev_button)
        self.page_count_label = QLabel()
        pagination_layout.addWidget(self.page_count_label)
        self.next_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoNext), '', self.pagination)
        self.next_button.clicked.connect(lambda:self.switch_page(1))
        pagination_layout.addWidget(self.next_button)
        self.pagination.setHidden(True)

        search_bar.addWidget(search_label)
        search_bar.addWidget(self.search_box)
        search_bar.addWidget(self.pagination)
        search_bar.addWidget(search_button)
        layout.addLayout(search_bar)

        self.result_table = QTableWidget(self)
        self.result_table.hide()
        self.result_table.setColumnCount(len(column_headers))
        self.result_table.setHorizontalHeaderLabels(column_headers)
        self.result_table.setColumnWidth(0, 200)
        self.result_table.setColumnWidth(1, 400)
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setStretchLastSection(False)
        layout.addWidget(self.result_table)

        self.no_results_label = QLabel('No results found.', self)
        self.no_results_label.hide()
        self.no_results_label.setStyleSheet('font-size: 14px; color: gray;')
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.no_results_label)


    def search(self):
        self.user_input = self.search_box.text()
        if self.user_input == '':
            QMessageBox.information(self.main_window, 'Empty Search', 'Search box is empty!')
            return

        self.main_window.statusBar().showMessage('Searching...')
        self.main_window.app.processEvents()

        self.curr_page = 1
        search_result_info = self.get_data()
        count = search_result_info[0]
        result = search_result_info[1]

        if count == 0 or not result:
            self.result_table.hide()
            self.no_results_label.show()
            self.main_window.statusBar().showMessage('Found nothing')
            return

        if count > self.PAGE_SIZE:
            self.page_count = math.ceil(count / self.PAGE_SIZE)
            self.update_page_count_label()
            self.pagination.setHidden(False)
        else:
            self.page_count = 1
            self.pagination.setHidden(True)

        self.result_table.show()
        self.no_results_label.hide()

        self.fill_table(result)
        self.main_window.statusBar().showMessage(f'Found {count} results')

    def switch_page(self, direction):
        self.curr_page += direction
        self.update_page_count_label()

        self.prev_button.setDisabled(self.curr_page == 1)
        self.next_button.setDisabled(self.curr_page == self.page_count)

        self.result_table.clearContents()
        page_data = self.get_data()[1]
        self.fill_table(page_data)

    def update_page_count_label(self):
        self.page_count_label.setText(f'Page {self.curr_page}/{self.page_count}')

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def fill_table(self, result):
        pass
