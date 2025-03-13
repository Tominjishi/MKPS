from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QPushButton, QLabel

from services.musicbrainz_api import search_artists
from ui.components.search_page import SearchPage

class SearchArtistsPage(SearchPage):
    def __init__(self, main_window):
        super().__init__(main_window, 'artists', ['Name', 'Description', ''])

    def get_data(self):
        result = search_artists(
            query=self.user_input,
            limit=self.PAGE_SIZE,
            offset=(self.curr_page - 1) * self.PAGE_SIZE
        )
        return result.get('artist-count', 0), result.get('artist-list', [])

    def fill_table(self, result):
        self.result_table.setRowCount(len(result))
        for i, artist in enumerate(result):
            row_number = (self.curr_page - 1) * self.PAGE_SIZE + i + 1
            self.result_table.setVerticalHeaderItem(i, QTableWidgetItem(str(row_number)))

            artist_name = artist.get('name')
            name_item = QTableWidgetItem(artist_name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 0, name_item)

            disambiguation_item = QTableWidgetItem(artist.get('disambiguation', 'None'))
            disambiguation_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 1, disambiguation_item)

            artist_mbid = artist.get('id')
            if artist_mbid:
                select_button = QPushButton('Select', self.result_table)
                select_button.clicked.connect(
                    lambda checked, a=artist_mbid, b=artist_name:self.navigate_to_release_group_list_page(a, b)
                )
            else:
                select_button = QLabel('-', self.result_table)
            self.result_table.setItem(i, 2, QTableWidgetItem())
            self.result_table.setCellWidget(i, 2, select_button)

    def navigate_to_release_group_list_page(self, artist_mbid, artist_name):
        self.main_window.release_group_list_page.populate_widget(artist_mbid, artist_name)
        self.main_window.navigate_to_page(self.main_window.release_group_list_page)