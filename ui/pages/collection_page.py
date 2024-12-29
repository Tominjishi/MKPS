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
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from ui.components.collection_filter_layout import FilterLayout

class CollectionPage(QWidget):
    TABLE_ICON_SIZE = 50

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.timeStampOrder = None
        self.tableFiltered = False
        self.entries = []
        self.filterSets = {
            'artists': set(),
            'genres': set()
        }

        mainLayout = QHBoxLayout(self)

        self.collectionTable = QTableWidget(self)
        self.collectionTable.setColumnCount(9)
        self.collectionTable.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Release Date', 'Added at', '']
        )
        self.collectionTable.setIconSize(QSize(self.TABLE_ICON_SIZE, self.TABLE_ICON_SIZE))
        self.collectionTable.verticalHeader().setDefaultSectionSize(self.TABLE_ICON_SIZE)
        self.collectionTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.collectionTable.setSortingEnabled(True)
        self.collectionTable.setColumnHidden(7, True)
        self.collectionTable.setColumnHidden(8, True)
        self.collectionTable.horizontalHeader().sectionClicked.connect(self.sortByTimestamp)

        # filters
        filterLayout = QVBoxLayout()
        clearFilters = QPushButton('Clear filters', self)
        clearFilters.clicked.connect(self.clearFilters)
        filterLayout.addWidget(clearFilters)
        # artist filters
        self.artistFilters = FilterLayout('Artists')
        self.artistFilters.checkBoxGroup.buttonToggled.connect(
            lambda button, checked, col='artists': self.filterTable(button, checked, col)
        )
        filterLayout.addLayout(self.artistFilters)
        # genre filters
        self.genreFilters = FilterLayout('Genres')
        self.genreFilters.checkBoxGroup.buttonToggled.connect(
            lambda button, checked, col='genres': self.filterTable(button, checked, col)
        )
        filterLayout.addLayout(self.genreFilters)

        filterLayout.addStretch()

        mainLayout.addWidget(self.collectionTable)
        mainLayout.addLayout(filterLayout)
        mainLayout.setStretchFactor(self.collectionTable, 3)
        mainLayout.setStretchFactor(filterLayout, 1)

        db = QSqlDatabase().database()
        if db.open():
            try:
                query = QSqlQuery(
                    """SELECT
                        collection_entry.cover,
                        collection_entry.artist_credit_phrase,
                        collection_entry.title,
                        collection_entry.type,
                        collection_entry.release_date,
                        collection_entry.added_at,
                        collection_entry.release_group_mbid,
                        GROUP_CONCAT(DISTINCT artist.name) as artist_names,
                        COALESCE(GROUP_CONCAT(DISTINCT genre.name), 'Unknown') as genre_names
                    FROM collection_entry
                    JOIN artist_entry_link ON artist_entry_link.collection_entry_id = collection_entry.id
                    JOIN artist on artist_entry_link.artist_mbid = artist.mbid
                    LEFT JOIN genre_link ON genre_link.collection_entry_id = collection_entry.id
                    LEFT JOIN genre ON genre_link.genre_mbid = genre.mbid
                    GROUP BY collection_entry.release_group_mbid
                    ORDER BY added_at"""
                )
                if not query.exec():
                    raise Exception(
                        'Collection entry fetch failed: ' + query.lastError().text()
                    )
                query.last()
                rowCount = query.at() + 1
                self.collectionTable.setRowCount(rowCount)

                artistSet = set()
                genreSet = set()
                for row in range(rowCount):
                    addedAtDateTime = query.value('collection_entry.added_at')
                    collectionEntry = {
                        # 'id': query.value('collection_entry.id'),
                        'cover': query.value('collection_entry.cover'),
                        'artist_credit_phrase': query.value('collection_entry.artist_credit_phrase'),
                        'title': query.value('collection_entry.title'),
                        'type': query.value('collection_entry.type'),
                        'release_date': query.value('collection_entry.release_date'),
                        'added_at': (
                            addedAtDateTime[8:10]   # Day
                            + addedAtDateTime[4:8]  # -Month-
                            + addedAtDateTime[:4]   # Year
                        ),
                        'release_group_mbid': query.value('collection_entry.release_group_mbid'),
                        'artists': query.value('artist_names').split(','),
                        'genres': query.value('genre_names').split(','),
                    }
                    self.entries.append(collectionEntry)
                    for artist in collectionEntry['artists']:
                        artistSet.add(artist)
                    for genre in collectionEntry['genres']:
                        genreSet.add(genre)

                    # ui add row
                    coverItem = QTableWidgetItem()
                    if collectionEntry['cover']:
                        coverPixmap = QPixmap()
                        coverPixmap.loadFromData(collectionEntry['cover'])
                        coverItem.setIcon(coverPixmap)
                    else:
                        coverItem.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.AudioCard))
                    coverItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    artistItem = QTableWidgetItem(collectionEntry['artist_credit_phrase'])
                    artistItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    titleItem = QTableWidgetItem(collectionEntry['title'])
                    titleItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    typeItem = QTableWidgetItem(collectionEntry['type'])
                    typeItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    releaseDateItem = QTableWidgetItem(collectionEntry['release_date'])
                    releaseDateItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    addedAtItem = QTableWidgetItem(collectionEntry['added_at'])
                    addedAtItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    selectButton = QPushButton('Select')
                    selectButton.clicked.connect(
                        lambda checked, a=collectionEntry['release_group_mbid']:self.openCard(
                            collectionEntry
                        )
                    )

                    self.collectionTable.setItem(row, 0, coverItem)
                    self.collectionTable.setItem(row, 1, artistItem)
                    self.collectionTable.setItem(row, 2, titleItem)
                    self.collectionTable.setItem(row, 3, typeItem)
                    self.collectionTable.setItem(row, 4, releaseDateItem)
                    self.collectionTable.setItem(row, 5, addedAtItem)
                    self.collectionTable.setItem(row, 6, QTableWidgetItem())
                    self.collectionTable.setCellWidget(row, 6, selectButton)
                    self.collectionTable.setItem(row, 7, QTableWidgetItem(addedAtDateTime))
                    self.collectionTable.setItem(row, 8, QTableWidgetItem(str(row)))
                    row += 1
                    query.previous()
                    
                # fill artist filter checkboxes
                self.addCheckboxes(artistSet, self.artistFilters)
                self.addCheckboxes(genreSet, self.genreFilters)
            except Exception as e:
                print('Error:', e)
                return
        else:
            print("Failed to open database: ", self.db.lastError().text())

    def sortByTimestamp(self, column):
        if column == 5:
            if self.timeStampOrder == 'asc':
                self.timeStampOrder = 'desc'
                self.collectionTable.sortItems(7, Qt.SortOrder.DescendingOrder)
            else:
                self.timeStampOrder = 'asc'
                self.collectionTable.sortItems(7, Qt.SortOrder.AscendingOrder)
        else:
            self.timeStampOrder = None

    def addCheckboxes(self, valueSet, filterLayout):
        for value in valueSet:
            checkBox = QCheckBox(value)
            filterLayout.checkBoxLayout.addWidget(checkBox)
            filterLayout.checkBoxGroup.addButton(checkBox)
        filterLayout.checkBoxLayout.parentWidget().adjustSize()

    def clearFilters(self):
        self.tableFiltered = False
        for filterSet in self.filterSets.values():
            filterSet.clear()
        self.artistFilters.uncheckAll()
        self.genreFilters.uncheckAll()
        self.showAllRows()

    def showAllRows(self):
        for row in range(self.collectionTable.rowCount()):
            self.collectionTable.setRowHidden(row, False)

    def filterTable(self, button, checked, col):
        # add/remove from appropriate set
        if checked:
            self.filterSets[col].add(button.text())
        else:
            self.filterSets[col].remove(button.text())

        for row in range(self.collectionTable.rowCount()):
            entry = self.entries[int(self.collectionTable.item(row, 8).text())]
            visible = all(
                not filterSet or any(item in filterSet for item in entry[colName])
                for colName, filterSet in self.filterSets.items()
            )
            self.collectionTable.setRowHidden(row, not visible)

    def openCard(self, release_group_mbid):
        return    
