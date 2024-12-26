from PySide6.QtWidgets import(
    QWidget,
    QTableWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery

class CollectionPage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.timeStampOrder = None
        self.tableIconSize = 50

        mainLayout = QVBoxLayout(self)
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
        mainLayout.addWidget(self.collectionTable)

        db = QSqlDatabase().database()
        if db.open():
            try:
                query = QSqlQuery("""SELECT
                                    cover,
                                    artist_credit_phrase,
                                    title,
                                    type,
                                    release_date,
                                    added_at,
                                    release_group_mbid
                                  FROM collection_entry
                                  GROUP BY release_group_mbid
                                  ORDER BY added_at""")
                if not query.exec():
                    raise Exception('Collection entry fetch failed: ' + query.lastError().text())
                query.last()
                rowCount = query.at() + 1
                self.collectionTable.setRowCount(rowCount)
                for row in range(rowCount):
                    dateTimeAddedAt = query.value('added_at')
                    collectionEntry = {
                        'cover': query.value('cover'),
                        'artist_credit_phrase': query.value('artist_credit_phrase'),
                        'title': query.value('title'),
                        'type': query.value('type'),
                        'release_date': query.value('release_date'),
                        'added_at': (
                            dateTimeAddedAt[8:10]   # Day
                            + dateTimeAddedAt[4:8]  # -Month-
                            + dateTimeAddedAt[:4]   # Year
                        ),
                        'release_group_mbid': query.value('release_group_mbid')
                    }

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
                    self.collectionTable.setItem(row, 7, QTableWidgetItem(dateTimeAddedAt))
                    row += 1
                    query.previous()
            except Exception as e:
                print('Error:', e)
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

    def openCard(self, release_group_mbid):
        return

        # layout = QGridLayout(self)
        # row = 0
        # col = 0

        # db = QSqlDatabase.addDatabase("QSQLITE")
        # db.setDatabaseName('data/data.db')

        # if db.open():
        #     query = QSqlQuery("SELECT title, cover FROM collection_entry")
        #     while query.next():
        #         label = QLabel(self)
        #         label.setFixedWidth(250)
        #         if query.value(1):
        #             pixmap = QPixmap()
        #             pixmap.loadFromData(query.value(1))
        #             label.setPixmap(pixmap)
        #         else:
        #             label.setText(query.value(0))
        #         layout.addWidget(label, row, col)
        #         col += 1
        #         if col == 5:
        #             row += 1
        #             col = 0
    
