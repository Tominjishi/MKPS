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
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.timeStampOrder = None
        self.tableIconSize = 50
        self.artists = set()
        self.entries = []

        mainLayout = QHBoxLayout(self)

        self.collectionTable = QTableWidget(self)
        self.collectionTable.setColumnCount(8)
        self.collectionTable.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Release Date', 'Added at', '']
        )
        self.collectionTable.setIconSize(QSize(self.tableIconSize, self.tableIconSize))
        self.collectionTable.verticalHeader().setDefaultSectionSize(self.tableIconSize)
        self.collectionTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.collectionTable.setSortingEnabled(True)
        self.collectionTable.setColumnHidden(7, True)
        self.collectionTable.horizontalHeader().sectionClicked.connect(self.sortByTimestamp)

        # filters
        # artist filters
        self.artistFilters = FilterLayout('Artists')
        self.artistFilters.filterButtons.buttonToggled.connect(self.filterArtists)

        filtersLayout = QVBoxLayout()
        filtersLayout.addLayout(self.artistFilters)
        filtersLayout.addStretch()

        mainLayout.addWidget(self.collectionTable)
        mainLayout.addLayout(filtersLayout)
        mainLayout.setStretchFactor(self.collectionTable, 3)
        mainLayout.setStretchFactor(filtersLayout, 1)

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
                        GROUP_CONCAT(DISTINCT artist.name) as artist_names
                    FROM collection_entry
                    JOIN artist_entry_link ON collection_entry_id = collection_entry.id
                    JOIN artist on artist_entry_link.artist_mbid = artist.mbid
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
                for row in range(rowCount):
                    addedAtDateTime = query.value('added_at')
                    collectionEntry = {
                        'id': query.value('collection_entry.id'),
                        'cover': query.value('cover'),
                        'artist_credit_phrase': query.value('artist_credit_phrase'),
                        'title': query.value('title'),
                        'type': query.value('type'),
                        'release_date': query.value('release_date'),
                        'added_at': (
                            addedAtDateTime[8:10]   # Day
                            + addedAtDateTime[4:8]  # -Month-
                            + addedAtDateTime[:4]   # Year
                        ),
                        'release_group_mbid': query.value('release_group_mbid'),
                        'artists': query.value('artist_names').split(',')
                    }
                    for artist in collectionEntry['artists']:
                        self.artists.add(artist)

                    self.entries.append(collectionEntry)

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
                    row += 1
                    query.previous()
            except Exception as e:
                print('Error:', e)
        else:
            print("Failed to open database: ", self.db.lastError().text())

        # fill artist filters
        for artist in self.artists:
            artistCheckbox = QCheckBox(artist)
            artistCheckbox.setChecked(True)
            self.artistFilters.filterLayout.addWidget(artistCheckbox)
            self.artistFilters.filterButtons.addButton(artistCheckbox)
            self.artistFilters.filterLayout.parentWidget().adjustSize()

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

    def filterArtists(self, button, checked):
        for i in range(self.collectionTable.rowCount()):
            if button.text() in self.entries[i]['artists']:
                self.collectionTable.setRowHidden(i, not checked)

    def openCard(self, release_group_mbid):
        return    
