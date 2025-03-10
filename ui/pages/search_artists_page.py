from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem
)
from PySide6.QtCore import Qt

from services.musicbrainz_api import search_artists

class SearchArtistsPage(QWidget):
    # Constants
    COLUMN_COUNT = 3
    COLUMN_HEADERS = ['Name', 'Description', '']

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        layout = QVBoxLayout(self)

        search_bar = QHBoxLayout()
        search_label = QLabel('Search artists:', self)
        self.search_box = QLineEdit(self)
        search_button = QPushButton('Search', self)
        self.search_box.returnPressed.connect(self.search_artists)
        search_button.clicked.connect(self.search_artists)
        search_bar.addWidget(search_label)
        search_bar.addWidget(self.search_box)
        search_bar.addWidget(search_button)
        layout.addLayout(search_bar)

        self.result_table = QTableWidget(self)
        self.result_table.hide()
        self.result_table.setColumnCount(self.COLUMN_COUNT)
        self.result_table.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
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


    def search_artists(self):
        user_input = self.search_box.text()
        if user_input == '':
            QMessageBox.information(self.main_window, 'Empty Search', 'Search box is empty!')
            return
        
        self.main_window.statusBar().showMessage('Searching...')
        self.main_window.app.processEvents()

        result = search_artists(user_input)
        artist_count = result.get('artist-count', 0)
        artist_list = result.get('artist-list', [])

        if artist_count == 0 or not artist_list:
            self.result_table.hide()
            self.no_results_label.show()
            self.main_window.statusBar().showMessage('Found 0 artists')
            return
        else:
            self.result_table.show()
            self.no_results_label.hide()

        self.result_table.setRowCount(artist_count)
        for i, artist in enumerate(artist_list):
            artist_name = artist.get('name')
            name_item = QTableWidgetItem(artist_name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 0, name_item)

            disambiguation_item = QTableWidgetItem(artist.get('disambiguation', 'None'))
            disambiguation_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 1, disambiguation_item)

            artist_mbid = artist.get('id', None)
            if artist_mbid:
                select_button = QPushButton('Select', self.result_table)
                select_button.clicked.connect(
                    lambda checked, a=artist_mbid, b=artist_name:self.navigate_to_release_group_list_page(a, b)
                )
            else:
                select_button = QLabel('-', self)
            self.result_table.setItem(i, 2, QTableWidgetItem())
            self.result_table.setCellWidget(i, 2, select_button)


        self.main_window.statusBar().showMessage(f"Found {artist_count} artists")

    def navigate_to_release_group_list_page(self, artist_mbid, artist_name):
        self.main_window.release_group_list_page.populate_widget(artist_mbid, artist_name)
        self.main_window.navigate_to_page(self.main_window.release_group_list_page)