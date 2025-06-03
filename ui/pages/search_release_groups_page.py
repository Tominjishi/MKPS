# mb api
from services.musicbrainz_api import search_release_groups
# ui components
from ui.components.search_page import SearchPage
# qt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QPushButton, QLabel, QMessageBox


# Subclass of SearchPage that handles searching for releases
class SearchReleaseGroupsPage(SearchPage):
    def __init__(self, main_window):
        super().__init__(main_window, 'releases', ['Title', 'Artist', 'Type', 'Release Year', ''])

    def get_data(self):
        result = search_release_groups(
            query=self.user_input,
            limit=self.PAGE_SIZE,
            offset=(self.curr_page - 1) * self.PAGE_SIZE
        )
        return result.get('release-group-count', 0), result.get('release-group-list', [])

    def fill_table(self, result):
        self.result_table.setRowCount(len(result))
        for i, release_group in enumerate(result):
            row_number = (self.curr_page - 1) * self.PAGE_SIZE + i + 1
            self.result_table.setVerticalHeaderItem(i, QTableWidgetItem(str(row_number)))

            title_item = QTableWidgetItem(release_group.get('title'))
            title_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 0, title_item)

            artist_item = QTableWidgetItem(release_group.get('artist-credit-phrase', 'Unknown'))
            artist_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 1, artist_item)

            type_item = QTableWidgetItem(release_group.get('type', 'Other'))
            type_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 2, type_item)

            year_item = QTableWidgetItem(release_group.get('first-release-date', 'Unknown')[:4])
            year_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.result_table.setItem(i, 3, year_item)

            mbid = release_group.get('id')
            if mbid:
                select_button = QPushButton('Select', self.result_table)
                select_button.clicked.connect(
                    lambda checked, a=mbid: self.navigate_to_release_group_card_page(a)
                )
            else:
                select_button = QLabel('-', self.result_table)
            self.result_table.setItem(i, 4, QTableWidgetItem())
            self.result_table.setCellWidget(i, 4, select_button)

    def navigate_to_release_group_card_page(self, release_group_mbid):
        success, error = self.main_window.release_group_card_page.populate_from_api(release_group_mbid)
        if success:
            self.main_window.navigate_to_page(self.main_window.release_group_card_page)
        else:
            QMessageBox.critical(self.main_window, 'Error', error)
