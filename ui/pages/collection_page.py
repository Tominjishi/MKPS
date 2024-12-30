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
        self.mainWindow = mainWindow

        self.timeStampOrder = None
        self.entries = []
        # sets of active filters
        self.activeFilters = {
            'artists': set(),
            'genres': set(),
            'type': set(),
            'formats': set(),
        }

        mainLayout = QHBoxLayout(self)

        self.collectionTable = QTableWidget(self)
        self.collectionTable.setColumnCount(9)
        self.collectionTable.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Release Date', 'Added at', '']
        )

        header = self.collectionTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # cover column
        self.collectionTable.setIconSize(QSize(self.TABLE_ICON_SIZE, self.TABLE_ICON_SIZE))
        self.collectionTable.verticalHeader().setDefaultSectionSize(self.TABLE_ICON_SIZE)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # button column
        self.collectionTable.setColumnWidth(6, 150)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)


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
        self.filterBoxes = {}
        for fieldName in self.activeFilters.keys():
            self.filterBoxes[fieldName] = FilterLayout(fieldName.capitalize())
            self.filterBoxes[fieldName].checkBoxGroup.buttonToggled.connect(
                lambda button, checked, col=fieldName: self.filterTable(button, checked, col)
            )
            self.filterBoxes[fieldName].searchBar.textChanged.connect(
                lambda text, col=fieldName: self.updateFilterBox(text, col)
            )
            filterLayout.addLayout(self.filterBoxes[fieldName])
        # self.artistFilters = FilterLayout('Artists')
        # self.artistFilters.checkBoxGroup.buttonToggled.connect(
        #     lambda button, checked, col='artists': self.filterTable(button, checked, col)
        # )
        # filterLayout.addLayout(self.artistFilters)
        # # genre filters
        # self.genreFilters = FilterLayout('Genres')
        # self.genreFilters.checkBoxGroup.buttonToggled.connect(
        #     lambda button, checked, col='genres': self.filterTable(button, checked, col)
        # )
        # filterLayout.addLayout(self.genreFilters)

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
                        collection_entry.id,
                        collection_entry.cover,
                        collection_entry.artist_credit_phrase,
                        collection_entry.title,
                        collection_entry.type,
                        collection_entry.release_date,
                        collection_entry.added_at,
                        collection_entry.release_group_mbid,
                        GROUP_CONCAT(DISTINCT collection_entry.format) AS formats,
                        GROUP_CONCAT(DISTINCT artist.name) AS artist_names,
                        COALESCE(GROUP_CONCAT(DISTINCT genre.name), 'Unknown') AS genre_names
                    FROM collection_entry
                    JOIN artist_entry_link ON artist_entry_link.collection_entry_id = collection_entry.id
                    JOIN artist ON artist_entry_link.artist_mbid = artist.mbid
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

                # unique sets for filters
                filters = {
                    'artists': set(),
                    'genres': set(),
                    'type': set(),
                    'formats': set(),
                }
                for row in range(rowCount):
                    addedAtDateTime = query.value('collection_entry.added_at')
                    collectionEntry = {
                        'id': query.value('collection_entry.id'),
                        'cover': query.value('collection_entry.cover'),
                        'artist_credit_phrase': query.value('collection_entry.artist_credit_phrase'),
                        'title': query.value('collection_entry.title'),
                        'type': [query.value('collection_entry.type')],
                        'release_date': query.value('collection_entry.release_date'),
                        'added_at': (
                            addedAtDateTime[8:10]   # Day
                            + addedAtDateTime[4:8]  # -Month-
                            + addedAtDateTime[:4]   # Year
                        ),
                        'release_group_mbid': query.value('collection_entry.release_group_mbid'),
                        'artists': query.value('artist_names').split(','),
                        'genres': query.value('genre_names').split(','),
                        'formats': query.value('formats').split(','),
                    }
                    self.entries.append(collectionEntry)

                    for artist in collectionEntry['artists']:
                        filters['artists'].add(artist)
                    for genre in collectionEntry['genres']:
                        filters['genres'].add(genre)
                    for format in collectionEntry['formats']:
                        filters['formats'].add(format)
                    filters['type'].add(collectionEntry['type'][0])

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

                    typeItem = QTableWidgetItem(collectionEntry['type'][0])
                    typeItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    releaseDateItem = QTableWidgetItem(collectionEntry['release_date'])
                    releaseDateItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    addedAtItem = QTableWidgetItem(collectionEntry['added_at'])
                    addedAtItem.setFlags(Qt.ItemFlag.ItemIsEnabled)

                    selectButton = QPushButton('Select')
                    selectButton.clicked.connect(
                        lambda checked, a=collectionEntry:self.openCard(a)
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
                for fieldName, filterSet in filters.items():
                    self.addCheckboxes(fieldName, filterSet)

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

    def addCheckboxes(self, fieldName, valueSet):
        for value in valueSet:
            checkBox = QCheckBox(value)
            self.filterBoxes[fieldName].checkBoxLayout.addWidget(checkBox)
            self.filterBoxes[fieldName].checkBoxGroup.addButton(checkBox)
        self.filterBoxes[fieldName].checkBoxLayout.parentWidget().adjustSize()
        self.filterBoxes[fieldName].checkBoxLayout.addStretch()

    def clearFilters(self):
        for filterSet in self.activeFilters.values():
            filterSet.clear()
        for filterBox in self.filterBoxes.values():
            filterBox.uncheckAll() 
        self.showAllRows()

    def showAllRows(self):
        for row in range(self.collectionTable.rowCount()):
            self.collectionTable.setRowHidden(row, False)

    def filterTable(self, button, checked, col):
        # add/remove from appropriate set
        if checked:
            self.activeFilters[col].add(button.text())
        else:
            self.activeFilters[col].remove(button.text())

        for row in range(self.collectionTable.rowCount()):
            entry = self.entries[int(self.collectionTable.item(row, 8).text())]
            visible = all(
                not filterSet or any(item in filterSet for item in entry[colName])
                for colName, filterSet in self.activeFilters.items()
            )
            self.collectionTable.setRowHidden(row, not visible)

    def updateFilterBox(self, text, col):
        for checkBox in self.filterBoxes[col].checkBoxGroup.buttons():
            if text.lower() in checkBox.text().lower():
                checkBox.show()
            else:
                checkBox.hide()
        self.filterBoxes[col].checkBoxLayout.parentWidget().adjustSize()

    def openCard(self, collectionEntry):
        self.mainWindow.releaseGroupCardPage.populateFromDatabase(collectionEntry)
        self.mainWindow.navigateToPage(self.mainWindow.releaseGroupCardPage)