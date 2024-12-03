from PySide6.QtWidgets import QMainWindow, QToolBar, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QStatusBar, QHeaderView
from PySide6.QtCore import Qt
import psycopg

class MainWindow(QMainWindow):
    def __init__ (self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("MKPS")

        self.toolbar = QToolBar()

        artistSearchLabel = QLabel("Search artists: ")
        self.artistSearchBox = QLineEdit()
        self.artistSearchBox.returnPressed.connect(self.searchArtists)
        artistSearchButton = QPushButton('Search')
        artistSearchButton.clicked.connect(self.searchArtists)

        self.toolbar.addWidget(artistSearchLabel)
        self.toolbar.addWidget(self.artistSearchBox)
        self.toolbar.addWidget(artistSearchButton)
        self.addToolBar(self.toolbar)

        self.setStatusBar(QStatusBar())

    def searchArtists(self):
        self.statusBar().showMessage('Searching...')
        self.app.processEvents()

        userInput = self.artistSearchBox.text()
        with psycopg.connect("hostaddr=192.168.1.100 port=5432 dbname=discogs user=psycopg password=kjkszpj") as conn:
            with conn.cursor() as cur:
                query = """
                SELECT id, name, profile
                FROM artist
                WHERE name ILIKE %s
                """
                cur.execute(query, (f"%{userInput}%",))
                results = cur.fetchall()

        self.table = QTableWidget()
        self.table.setRowCount(len(results))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Name','Description',''])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i, artist in enumerate(results):
            nameItem = QTableWidgetItem(artist[1])
            nameItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            descriptionItem = QTableWidgetItem(artist[2])
            descriptionItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            selectButton = QPushButton('Select')
            selectButton.clicked.connect(lambda checked, a=artist[0]:self.showArtistMasters(a))

            self.table.setItem(i, 0, nameItem)
            self.table.setItem(i, 1, descriptionItem)
            self.table.setItem(i, 2, QTableWidgetItem())
            self.table.setCellWidget(i, 2, selectButton)
        
        self.setCentralWidget(self.table)
        self.statusBar().showMessage(f"Found {len(results)} artists")

    def showArtistMasters(self, artistId):
        with psycopg.connect("hostaddr=192.168.1.100 port=5432 dbname=discogs user=psycopg password=kjkszpj") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM artist WHERE id = %s", (artistId,))
                self.statusBar().showMessage(cur.fetchone()[0])

                query = """
                SELECT master.id, master.title, master.year
                FROM master_artist
                JOIN master ON master.id = master_id
                JOIN artist ON artist.id = artist_id
                WHERE artist.id = %s
                ORDER BY master.year DESC
                """
                cur.execute(query, (artistId,))
                results = cur.fetchall()

                masterTable = QTableWidget()
                masterTable.setRowCount(len(results))
                masterTable.setColumnCount(2)
                masterTable.setHorizontalHeaderLabels(['Title','Release Year'])
                masterTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                for i, master in enumerate(results):
                    titleItem = QTableWidgetItem(master[1])
                    titleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    print(master[2])
                    yearItem = QTableWidgetItem(str(master[2]))
                    yearItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                    masterTable.setItem(i, 0, titleItem)
                    masterTable.setItem(i, 1, yearItem)

                self.setCentralWidget(masterTable)
                returnButton = QPushButton('Return')
                returnButton.clicked.connect(lambda checked, a=self.table:self.setCentralWidget(a))
                self.toolbar.addWidget(returnButton)
