from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QTableWidget, QVBoxLayout, QTableWidgetItem, QPushButton, QHeaderView
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery

class CollectionPage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.tableIconSize = 50
        mainLayout = QVBoxLayout(self)
        collectionTable = QTableWidget(self)
        collectionTable.setColumnCount(6)
        collectionTable.setHorizontalHeaderLabels(
            ['Cover', 'Artist', 'Title', 'Type', 'Release Date', '']
        )
        collectionTable.setIconSize(QSize(self.tableIconSize, self.tableIconSize))
        collectionTable.verticalHeader().setDefaultSectionSize(self.tableIconSize)
        collectionTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        mainLayout.addWidget(collectionTable)

        db = QSqlDatabase().database()
        if db.open():
            try:
                query = QSqlQuery("""SELECT
                                    cover,
                                    artist_credit_phrase,
                                    title,
                                    type,
                                    release_date,
                                    release_group_mbid
                                  FROM collection_entry
                                  GROUP BY release_group_mbid""")
                if not query.exec():
                    raise Exception('Collection entry fetch failed: ' + query.lastError().text())
                query.last()
                rowCount = query.at() + 1
                collectionTable.setRowCount(rowCount)
                for i in range(rowCount):
                    coverPixmap = QPixmap()
                    coverPixmap.loadFromData(query.value('cover'))
                    coverItem = QTableWidgetItem(QIcon(coverPixmap), '')
                    coverItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    artistItem = QTableWidgetItem(query.value('artist_credit_phrase'))
                    artistItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    titleItem = QTableWidgetItem(query.value('title'))
                    titleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    typeItem = QTableWidgetItem(query.value('type'))
                    typeItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    releaseDateItem = QTableWidgetItem(query.value('release_date'))
                    releaseDateItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    selectButton = QPushButton('Select')
                    selectButton.clicked.connect(
                        lambda checked, a=query.value('release_group_mbid'):self.openCard(a)
                    )

                    collectionTable.setItem(i, 0, coverItem)
                    collectionTable.setItem(i, 1, artistItem)
                    collectionTable.setItem(i, 2, titleItem)
                    collectionTable.setItem(i, 3, typeItem)
                    collectionTable.setItem(i, 4, releaseDateItem)
                    collectionTable.setItem(i, 5, QTableWidgetItem())
                    collectionTable.setCellWidget(i, 5, selectButton)
                    i += 1
                    query.previous()
            except Exception as e:
                print('Error:', e)
        else:
            print("Failed to open database: ", self.db.lastError().text())

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
