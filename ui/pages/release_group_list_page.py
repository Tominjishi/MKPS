from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidgetItem,
    QPushButton
)
from PySide6.QtCore import Qt
import math

from ui.components.release_group_browser import ReleaseGroupBrowser
from services.musicbrainz_api import browse_release_groups


class ReleaseGroupListPage(QWidget):
    # Constants
    PAGE_SIZE = 25

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.artist_mbid = None
        layout = QVBoxLayout(self)

        self.artist_name_label = QLabel(self)
        self.artist_name_label.setStyleSheet('font-size: 21px;')

        # Album Table
        # Title
        self.album_table_title = QLabel('Albums', self)
        self.album_table_title.setStyleSheet('font-size: 16px;')
        # Table Browser
        self.album_table_browser = ReleaseGroupBrowser(self)
        # Page navigation
        self.album_table_browser.prev_button.clicked.connect(
            lambda checked, browser=self.album_table_browser, release_type='album':self.previous_page(browser, release_type)
        )
        self.album_table_browser.next_button.clicked.connect(
            lambda checked, browser=self.album_table_browser, release_type='album':self.next_page(browser, release_type)
        )

        # EP Table
        # Title
        self.ep_table_title = QLabel("EP's", self)
        self.ep_table_title.setStyleSheet('font-size: 16px;')
        # Table Browser
        self.ep_table_browser = ReleaseGroupBrowser(self)
        #Page Navigation
        self.ep_table_browser.prev_button.clicked.connect(
            lambda checked, browser=self.ep_table_browser, release_type='ep':self.previous_page(browser, release_type)
        )
        self.ep_table_browser.next_button.clicked.connect(
            lambda checked, browser=self.ep_table_browser, release_type='ep':self.next_page(browser, release_type)
        )

        layout.addWidget(self.artist_name_label)
        layout.addWidget(self.album_table_title)
        layout.addWidget(self.album_table_browser)
        layout.addWidget(self.ep_table_title)
        layout.addWidget(self.ep_table_browser)

    def populate_widget(self, artist_mbid, artist_name =''):
        self.artist_mbid = artist_mbid
        self.artist_name_label.setText(artist_name)

        # Init Album
        album_result = browse_release_groups(
            artist=self.artist_mbid,
            release_type='album',
            limit=self.PAGE_SIZE
        )
        album_count = album_result.get('release-group-count', 0)
        album_list = album_result.get('release-group-list', [])
        self.album_table_title.setText(f"Albums ({album_count})")
        self.init_table_browser(self.album_table_browser, album_count, album_list)

        # Init EP
        ep_result = browse_release_groups(
            artist=self.artist_mbid,
            release_type='ep',
            limit=self.PAGE_SIZE
        )
        ep_count = ep_result.get('release-group-count', 0)
        ep_list = ep_result.get('release-group-list', [])
        self.ep_table_title.setText(f"EP's ({ep_count})")
        self.init_table_browser(self.ep_table_browser, ep_count, ep_list)

    def init_table_browser(self, table_browser, release_count, release_list):
        if release_count == 0 or not release_list:
            table_browser.table.hide()
            table_browser.pagination_buttons.hide()
            table_browser.empty_label.show()
        else:
            table_browser.table.show()
            table_browser.empty_label.hide()
            table_browser.curr_page = 1
    
            if release_count > self.PAGE_SIZE:
                table_browser.pagination_buttons.show()
                table_browser.page_count = math.ceil(release_count / self.PAGE_SIZE)
                table_browser.page_count_label.setText(f"Page 1/{table_browser.page_count}")
                table_browser.prev_button.setDisabled(True)
                table_browser.next_button.setDisabled(False)
            else:
                table_browser.pagination_buttons.hide()

            self.populate_table(table_browser, release_list)

    def populate_table(self, table_browser, release_list):
        row_count = len(release_list)
        table_browser.table.setRowCount(row_count)

        for i, releaseGroup in enumerate(release_list):
            row_number = (table_browser.curr_page - 1) * self.PAGE_SIZE + i + 1
            table_browser.table.setVerticalHeaderItem(i, QTableWidgetItem(str(row_number)))

            title_item = QTableWidgetItem(releaseGroup.get('title'))
            title_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table_browser.table.setItem(i, 0, title_item)

            type_item = QTableWidgetItem(releaseGroup.get('type'))
            type_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table_browser.table.setItem(i, 1, type_item)

            year_item = QTableWidgetItem(releaseGroup.get('first-release-date')[:4])
            year_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table_browser.table.setItem(i, 2, year_item)

            select_button = QPushButton('Select', table_browser.table)
            select_button.clicked.connect(
                lambda checked, a=releaseGroup['id']:self.navigate_to_release_group_card_page(a)
            )
            table_browser.table.setItem(i, 3, QTableWidgetItem())
            table_browser.table.setCellWidget(i, 3, select_button)

            # coverResponseTuple = getReleaseGroupFrontCoverData(releaseGroup['id'],'s')
            # if coverResponseTuple[0] == 200:
            #     pixmap = QPixmap()
            #     pixmap.loadFromData(coverResponseTuple[1])
            #     icon = QIcon(pixmap)
            #     coverItem = QTableWidgetItem(icon,'')
            # else:
            #     coverItem = QTableWidgetItem(coverResponseTuple[1])
            #     print(f"Error {coverResponseTuple[0]} for release group {releaseGroup['id']}")


    def previous_page(self, table_browser, release_type):
        table_browser.curr_page -= 1
        self.switch_page(table_browser, release_type)

    def next_page(self, table_browser, release_type):
        table_browser.curr_page += 1
        self.switch_page(table_browser, release_type)

    def switch_page(self, table_browser, release_type):
        table_browser.prev_button.setDisabled(table_browser.curr_page == 1)
        table_browser.next_button.setDisabled(table_browser.curr_page == table_browser.page_count)

        table_browser.table.clearContents()
        table_browser.page_count_label.setText(f"Page {table_browser.curr_page}/{table_browser.page_count}")

        result = browse_release_groups(
            artist=self.artist_mbid,
            release_type=release_type,
            limit=self.PAGE_SIZE,
            offset=(table_browser.curr_page - 1) * self.PAGE_SIZE
        )
        release_list = result.get('release-group-list',[])
        self.populate_table(table_browser, release_list)

    def navigate_to_release_group_card_page(self, release_group_mbid):
        self.main_window.release_group_card_page.populate_from_api(release_group_mbid)
        self.main_window.navigate_to_page(self.main_window.release_group_card_page)