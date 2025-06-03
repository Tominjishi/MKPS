from random import randint
from collections import Counter
# ui components
from ui.components.filtering.artist_filter_layout import ArtistFilterLayout
from ui.components.filtering.genre_filter_layout import GenreFilterLayout
from ui.components.filtering.rel_type_filter_layout import RelTypeFilterLayout
from ui.components.filtering.format_filter_layout import FormatFilterLayout
from ui.components.selectable_label import SelectableLabel
# db queries
from data.release import Release
from data.queries import get_artists, get_genres, get_release_types, get_formats
# qt
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QTableWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QGridLayout,
)

TABLE_ICON_SIZE = 50


# Page for showing user's collection
class CollectionPage(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.time_stamp_descending = True
        self.releases = []
        # sets of active filters
        self.active_filters = {
            'artists': set(),
            'genres': set(),
            'type': set(),
            'format': set(),
        }

        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()

        # layout for showing collection statistics
        statistics_layout = QGridLayout()
        statistics_layout.setVerticalSpacing(10)
        self.s_release_count = SelectableLabel()
        self.s_format_releases = SelectableLabel()
        self.s_format_releases.setWordWrap(True)
        self.s_type_releases = SelectableLabel()
        self.s_type_releases.setWordWrap(True)
        self.s_most_common_genres = SelectableLabel()
        self.s_most_common_genres.setWordWrap(True)
        self.s_unique_genre_count = SelectableLabel()
        self.s_most_common_artists = SelectableLabel()
        self.s_most_common_artists.setWordWrap(True)
        self.s_unique_artist_count = SelectableLabel()
        self.s_average_tracks = SelectableLabel()
        self.s_oldest_release = SelectableLabel()
        self.s_newest_release = SelectableLabel()
        statistics_layout.addWidget(self.s_release_count, 0, 0, 1, 6, Qt.AlignmentFlag.AlignCenter)
        statistics_layout.addWidget(self.s_format_releases, 1, 0, 1, 6)
        statistics_layout.addWidget(self.s_type_releases, 2, 0, 1, 6)
        statistics_layout.addWidget(self.s_most_common_genres, 3, 0, 1, 4)
        statistics_layout.addWidget(self.s_unique_genre_count, 3, 4, 1, 2, Qt.AlignmentFlag.AlignRight)
        statistics_layout.addWidget(self.s_most_common_artists, 4, 0, 1, 4)
        statistics_layout.addWidget(self.s_unique_artist_count, 4, 4, 1, 2, Qt.AlignmentFlag.AlignRight)
        statistics_layout.addWidget(self.s_average_tracks, 5, 0, 1, 2)
        statistics_layout.addWidget(self.s_oldest_release, 5, 2, 1, 2, Qt.AlignmentFlag.AlignCenter)
        statistics_layout.addWidget(self.s_newest_release, 5, 4, 1, 2, Qt.AlignmentFlag.AlignRight)
        left_layout.addLayout(statistics_layout)

        # Top bar layout for search bar, "Insert" button and "Random" button
        top_bar = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText('Search releases by title')
        self.search_bar.textChanged.connect(self.search_title)
        top_bar.addWidget(self.search_bar)
        # Button to create new release
        insert_button = QPushButton('Insert')
        insert_button.clicked.connect(self.open_edit_card)
        top_bar.addWidget(insert_button)
        # Button to open random release in collection
        random_button = QPushButton('Random')
        random_button.clicked.connect(self.open_random)
        top_bar.addWidget(random_button)
        left_layout.addLayout(top_bar)

        self.collection_table = QTableWidget(self)
        self.collection_table.setColumnCount(10)
        self.collection_table.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Format', 'Release Date', 'Added at', '']
        )

        header = self.collection_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # cover column
        self.collection_table.setIconSize(QSize(TABLE_ICON_SIZE, TABLE_ICON_SIZE))
        self.collection_table.verticalHeader().setDefaultSectionSize(TABLE_ICON_SIZE)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # button column
        self.collection_table.setColumnWidth(7, 150)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.collection_table.setSortingEnabled(True)
        # Hidden "added_at" column to sort by time while only showing date
        self.collection_table.setColumnHidden(8, True)
        # Hidden "row" column to keep track of the original order
        self.collection_table.setColumnHidden(9, True)
        self.collection_table.horizontalHeader().sectionClicked.connect(self.sort_by_timestamp)
        left_layout.addWidget(self.collection_table)

        # initialize filters
        filter_layout = QVBoxLayout()
        clear_filters_button = QPushButton('Clear filters', self)
        clear_filters_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filters_button)
        # individual filter layouts
        artist_filter_layout = ArtistFilterLayout(get_artists(), self)
        genre_filter_layout = GenreFilterLayout(get_genres(), self)
        rel_type_filter_layout = RelTypeFilterLayout(get_release_types(), self)
        format_filter_layout = FormatFilterLayout(get_formats(), self)

        # checkbox group connection to filtering function
        artist_filter_layout.check_box_group.buttonToggled.connect(
            lambda checkbox, checked, filter_by='artists': self.filter(checkbox, checked, filter_by)
        )
        genre_filter_layout.check_box_group.buttonToggled.connect(
            lambda checkbox, checked, filter_by='genres': self.filter(checkbox, checked, filter_by)
        )
        rel_type_filter_layout.check_box_group.buttonToggled.connect(
            lambda checkbox, checked, filter_by='type': self.filter(checkbox, checked, filter_by)
        )
        format_filter_layout.check_box_group.buttonToggled.connect(
            lambda checkbox, checked, filter_by='format': self.filter(checkbox, checked, filter_by)
        )

        # add individual filter layouts to list and general filter layout
        self.filter_boxes = {
            'artists': artist_filter_layout,
            'genres': genre_filter_layout,
            'type': rel_type_filter_layout,
            'format': format_filter_layout
        }
        filter_layout.addLayout(artist_filter_layout, 1)
        filter_layout.addLayout(genre_filter_layout, 1)
        filter_layout.addLayout(rel_type_filter_layout, 1)
        filter_layout.addLayout(format_filter_layout, 1)
        filter_layout.addStretch()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(filter_layout)
        main_layout.setStretchFactor(left_layout, 3)
        main_layout.setStretchFactor(filter_layout, 1)
        self.fill_table()

    def fill_table(self):
        self.releases = Release.get_all()
        self.collection_table.setRowCount(len(self.releases))
        if self.releases:
            # Counters to keep track of stats
            artist_counter = Counter()
            genre_counter = Counter()
            type_counter = Counter()
            format_counter = Counter()
            for row, release in enumerate(self.releases):
                self.add_row(row, release)  # Add row to table
                # Stats
                type_counter[release.type] += 1
                format_counter[release.format] += 1
                for artist in release.artists:
                    artist_counter[artist['name']] += 1
                for genre in release.genres:
                    genre_counter[genre['name']] += 1

            # Calculate and show statistics
            self.s_release_count.setText(f'<b>Total releases:</b> {len(self.releases)}')
            self.s_format_releases.setText(
                '<b>Most releases by format:</b> '
                + ', '.join(f'{form} - {count}' for form, count in format_counter.most_common(5))
            )
            self.s_type_releases.setText(
                '<b>Most releases by type:</b> '
                + ', '.join(f'{typ} - {count}' for typ, count in type_counter.most_common(5))
            )
            self.s_most_common_genres.setText(
                '<b>Most releases by genre:</b> '
                + ', '.join(f'{genre} - {count}' for genre, count in genre_counter.most_common(5))
            )
            self.s_unique_genre_count.setText(f'<b>Unique genres:</b> {len(genre_counter.keys())}')
            self.s_most_common_artists.setText(
                '<b>Most releases by artist:</b> '
                + ', '.join(f'{artist} - {count}' for artist, count in artist_counter.most_common(5))
            )
            self.s_unique_artist_count.setText(f'<b>Unique artists:</b> {len(artist_counter.keys())}')
            oldest_date, oldest_name = Release.get_oldest_release()
            self.s_oldest_release.setText(f'<b>Oldest release:</b> {oldest_date} - {oldest_name}')
            newest_date, newest_name = Release.get_newest_release()
            self.s_newest_release.setText(f'<b>Newest release:</b> {newest_date} - {newest_name}')
            self.s_average_tracks.setText(f'<b>Average tracks per release:</b> {Release.get_average_tracks()}')

    # Add row to table using release instance
    def add_row(self, row, release):
        cover_item = QTableWidgetItem()
        if release.cover:
            cover_pixmap = QPixmap()
            cover_pixmap.loadFromData(release.cover)
            cover_item.setIcon(cover_pixmap)
        else:
            cover_item.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.AudioVolumeHigh))
        cover_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        artist_item = QTableWidgetItem(release.artist_credit_phrase)
        artist_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        title_item = QTableWidgetItem(release.title)
        title_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        type_item = QTableWidgetItem(release.type)
        type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        format_item = QTableWidgetItem(release.format)
        format_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        release_date_item = QTableWidgetItem(release.release_date)
        release_date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        added_at_date = release.added_at[:4] + release.added_at[4:8] + release.added_at[8:10]
        added_at_item = QTableWidgetItem(added_at_date)
        added_at_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        added_at_item.setToolTip(release.added_at)

        select_button = QPushButton('Select')
        select_button.clicked.connect(lambda checked, a=release: self.open_card(a))

        self.collection_table.setItem(row, 0, cover_item)
        self.collection_table.setItem(row, 1, artist_item)
        self.collection_table.setItem(row, 2, title_item)
        self.collection_table.setItem(row, 3, type_item)
        self.collection_table.setItem(row, 4, format_item)
        self.collection_table.setItem(row, 5, release_date_item)
        self.collection_table.setItem(row, 6, added_at_item)
        self.collection_table.setCellWidget(row, 7, select_button)
        self.collection_table.setItem(row, 8, QTableWidgetItem(release.added_at))
        self.collection_table.setItem(row, 9, QTableWidgetItem(str(row)))

    # Sort by hidden timestamp column when user sorts by visible column
    def sort_by_timestamp(self, column):
        if column == 6:
            if self.time_stamp_descending:
                self.time_stamp_descending = False
                self.collection_table.sortItems(8, Qt.SortOrder.AscendingOrder)
            else:
                self.time_stamp_descending = True
                self.collection_table.sortItems(8, Qt.SortOrder.DescendingOrder)
        else:
            self.time_stamp_descending = None

    # Clear all checked filters
    def clear_filters(self):
        for filter_set in self.active_filters.values():
            filter_set.clear()
        for filter_box in self.filter_boxes.values():
            filter_box.uncheck_all()
        self.show_all_rows()
        self.search_bar.clear()

    # Un-hide all rows
    def show_all_rows(self):
        for row in range(self.collection_table.rowCount()):
            self.collection_table.setRowHidden(row, False)

    def filter(self, button, checked, filter_by):
        # add/remove from appropriate set
        if checked:
            self.active_filters[filter_by].add(button.text())
        else:
            self.active_filters[filter_by].remove(button.text())

        for row in range(self.collection_table.rowCount()):
            entry = self.releases[int(self.collection_table.item(row, 9).text())]
            visible = True  # Default to visible
            for col_name, filter_set in self.active_filters.items():
                if filter_set:  # Skip if not filtered by that field
                    entry_values = get_filterable_list(getattr(entry, col_name))
                    # if entry doesn't match any of the filters, hide the row
                    if not any(item in filter_set for item in entry_values):
                        visible = False
                        break
            self.collection_table.setRowHidden(row, not visible)

    def open_card(self, collection_entry):
        self.main_window.release_group_card_page.populate_from_database(collection_entry)
        self.main_window.navigate_to_page(self.main_window.release_group_card_page)

    def open_edit_card(self):
        self.main_window.release_group_card_page.release = None
        self.main_window.release_group_card_page.switch_online_mode(False)
        self.main_window.release_group_card_page.edit_mode = False
        self.main_window.release_group_card_page.switch_edit_mode()
        self.main_window.navigate_to_page(self.main_window.release_group_card_page)

    def search_title(self, query):
        for row in range(self.collection_table.rowCount()):
            title = self.collection_table.item(row, 2).text()
            if query.lower() in title.lower():
                self.collection_table.setRowHidden(row, False)
            else:
                self.collection_table.setRowHidden(row, True)

    def open_random(self):
        row_count = self.collection_table.rowCount()
        if row_count:
            random_row = randint(0, row_count - 1)
            select_button = self.collection_table.cellWidget(random_row, 7)
            select_button.click()
        else:
            QMessageBox.information(self, 'Empty collection', 'Your collection is empty!')


# create list of single item for strings (type, format) and list of name values (artists, genres) to filter by
def get_filterable_list(value):
    if isinstance(value, str) or not hasattr(value, '__iter__'):
        return [value]
    else:
        return [item['name'] for item in value]
