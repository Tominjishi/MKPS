from PySide6.QtWidgets import(
    QWidget,
    QTableWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
    QCheckBox,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt
from ui.components.collection_filter_layout import FilterLayout
from data.release import Release

class CollectionPage(QWidget):
    TABLE_ICON_SIZE = 50

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.time_stamp_descending = True
        self.entries = []
        # sets of active filters
        self.active_filters = {
            'artists': set(),
            'genres': set(),
            'type': set(),
            'format': set(),
        }

        main_layout = QHBoxLayout(self)

        self.collection_table = QTableWidget(self)
        self.collection_table.setColumnCount(9)
        self.collection_table.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Release Date', 'Added at', '']
        )

        header = self.collection_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # cover column
        self.collection_table.setIconSize(QSize(self.TABLE_ICON_SIZE, self.TABLE_ICON_SIZE))
        self.collection_table.verticalHeader().setDefaultSectionSize(self.TABLE_ICON_SIZE)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # button column
        self.collection_table.setColumnWidth(6, 150)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)


        self.collection_table.setSortingEnabled(True)
        self.collection_table.setColumnHidden(7, True)
        self.collection_table.setColumnHidden(8, True)
        self.collection_table.horizontalHeader().sectionClicked.connect(self.sort_by_timestamp)

        # filters
        filter_layout = QVBoxLayout()
        clear_filters_button = QPushButton('Clear filters', self)
        clear_filters_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filters_button)
        # artist filters
        self.filter_boxes = {}
        for field_name in self.active_filters.keys():
            self.filter_boxes[field_name] = FilterLayout(field_name.capitalize())
            self.filter_boxes[field_name].check_box_group.buttonToggled.connect(
                lambda button, checked, col=field_name: self.filter_table(button, checked, col)
            )
            self.filter_boxes[field_name].search_bar.textChanged.connect(
                lambda text, col=field_name: self.update_filter_box(text, col)
            )
            filter_layout.addLayout(self.filter_boxes[field_name])
        # self.artistFilters = FilterLayout('Artists')
        # self.artistFilters.checkBoxGroup.buttonToggled.connect(
        #     lambda button, checked, col='artists': self.filterTable(button, checked, col)
        # )
        # filter_layout.addLayout(self.artistFilters)
        # # genre filters
        # self.genreFilters = FilterLayout('Genres')
        # self.genreFilters.checkBoxGroup.buttonToggled.connect(
        #     lambda button, checked, col='genres': self.filterTable(button, checked, col)
        # )
        # filter_layout.addLayout(self.genreFilters)

        filter_layout.addStretch()

        main_layout.addWidget(self.collection_table)
        main_layout.addLayout(filter_layout)
        main_layout.setStretchFactor(self.collection_table, 3)
        main_layout.setStretchFactor(filter_layout, 1)

        self.fill_table()

    def fill_table(self):
        self.entries = Release.get_all()
        if self.entries:
            self.collection_table.setRowCount(len(self.entries))

            # unique sets for filters
            filters = {
                'artists': set(),
                'genres': set(),
                'type': set(),
                'format': set(),
            }

            for row, entry in enumerate(self.entries):
                for artist in entry.artists:
                    filters['artists'].add(artist)
                for genre in entry.genres:
                    filters['genres'].add(genre)
                filters['type'].add(entry.type)
                filters['format'].add(entry.format)

                # add row to table
                self.add_row(row, entry)

            # fill artist filter checkboxes
            for field_name, filter_set in filters.items():
                self.add_checkboxes(field_name, filter_set)


    def add_row(self, row, entry):
        cover_item = QTableWidgetItem()
        if entry.cover:
            cover_pixmap = QPixmap()
            cover_pixmap.loadFromData(entry.cover)
            cover_item.setIcon(cover_pixmap)
        else:
            cover_item.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.AudioVolumeHigh))
        cover_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        artist_item = QTableWidgetItem(entry.artist_credit_phrase)
        artist_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        title_item = QTableWidgetItem(entry.title)
        title_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        type_item = QTableWidgetItem(entry.type)
        type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        release_date_item = QTableWidgetItem(entry.release_date)
        release_date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        added_at_date = entry.added_at[:4] + entry.added_at[4:8] + entry.added_at[8:10]
        added_at_item = QTableWidgetItem(added_at_date)
        added_at_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        added_at_item.setToolTip(entry.added_at)

        select_button = QPushButton('Select')
        select_button.clicked.connect(
            lambda checked, a=entry: self.open_card(a)
        )

        self.collection_table.setItem(row, 0, cover_item)
        self.collection_table.setItem(row, 1, artist_item)
        self.collection_table.setItem(row, 2, title_item)
        self.collection_table.setItem(row, 3, type_item)
        self.collection_table.setItem(row, 4, release_date_item)
        self.collection_table.setItem(row, 5, added_at_item)
        self.collection_table.setItem(row, 6, QTableWidgetItem())
        self.collection_table.setCellWidget(row, 6, select_button)
        # Hidden "added_at" column to sort by time while only showing date
        self.collection_table.setItem(row, 7, QTableWidgetItem(entry.added_at))
        self.collection_table.setItem(row, 8, QTableWidgetItem(str(row)))

    def add_checkboxes(self, field_name, value_set):
        for value in value_set:
            check_box = QCheckBox(value)
            self.filter_boxes[field_name].check_box_layout.addWidget(check_box)
            self.filter_boxes[field_name].check_box_group.addButton(check_box)
        self.filter_boxes[field_name].check_box_layout.parentWidget().adjustSize()
        self.filter_boxes[field_name].check_box_layout.addStretch()

    def sort_by_timestamp(self, column):
        if column == 5:
            if self.time_stamp_descending:
                self.time_stamp_descending = False
                self.collection_table.sortItems(7, Qt.SortOrder.AscendingOrder)
            else:
                self.time_stamp_descending = True
                self.collection_table.sortItems(7, Qt.SortOrder.DescendingOrder)
        else:
            self.time_stamp_descending = None

    def clear_filters(self):
        for filter_set in self.active_filters.values():
            filter_set.clear()
        for filter_box in self.filter_boxes.values():
            filter_box.uncheck_all()
        self.show_all_rows()


    def show_all_rows(self):
        for row in range(self.collection_table.rowCount()):
            self.collection_table.setRowHidden(row, False)

    def filter_table(self, button, checked, col):
        # add/remove from appropriate set
        if checked:
            self.active_filters[col].add(button.text())
        else:
            self.active_filters[col].remove(button.text())

        for row in range(self.collection_table.rowCount()):
            entry = self.entries[int(self.collection_table.item(row, 8).text())]
            visible = True  # Default to visible
            for col_name, filter_set in self.active_filters.items():
                if filter_set:  # Skip if not filtered by that field
                    entry_values = ensure_iterable_filter(getattr(entry, col_name))
                    # if entry doesn't match any of the filters, hide the row
                    if not any(item in filter_set for item in entry_values):
                        visible = False
                        break
            self.collection_table.setRowHidden(row, not visible)

    def update_filter_box(self, text, col):
        for check_box in self.filter_boxes[col].check_box_group.buttons():
            if text.lower() in check_box.text().lower():
                check_box.show()
            else:
                check_box.hide()
        self.filter_boxes[col].check_box_layout.parentWidget().adjustSize()

    def open_card(self, collection_entry):
        self.main_window.release_group_card_page.populate_from_database(collection_entry)
        self.main_window.navigate_to_page(self.main_window.release_group_card_page)

def ensure_iterable_filter(value):
    if isinstance(value, str) or not hasattr(value, '__iter__'):
        return [value]
    else:
        return value
