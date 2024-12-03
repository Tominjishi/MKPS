from PySide6.QtWidgets import QMainWindow, QToolBar, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QStatusBar, QHeaderView, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt, QSize
import psycopg
import json

with open('db_config.json') as f:
    dbConfig = json.load(f)

connString = (f"hostaddr={dbConfig['hostaddr']} port={dbConfig['port']} dbname={dbConfig['dbname']} user={dbConfig['user']} password={dbConfig['password']}")

class MainWindow(QMainWindow):
    def __init__ (self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("MKPS")
        self.resize(QSize(1280, 720))
        self.setStatusBar(QStatusBar())
        self.toolbar = QToolBar()

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        artistSearchPage = ArtistSearchPage(self)
        self.pages.addWidget(artistSearchPage)
        self.pages.setCurrentWidget(artistSearchPage)

class ArtistSearchPage(QTableWidget):
    def __init__ (self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.initToolBar()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Name','Description',''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def initToolBar(self):
        self.mainWindow.removeToolBar(self.mainWindow.toolbar)
        self.mainWindow.toolbar = QToolBar()

        artistSearchLabel = QLabel("Search artists: ")
        self.artistSearchBox = QLineEdit(getattr(self, 'userInput', ''))
        self.artistSearchBox.returnPressed.connect(self.searchArtists)
        artistSearchButton = QPushButton('Search')
        artistSearchButton.clicked.connect(self.searchArtists)

        self.mainWindow.toolbar.addWidget(artistSearchLabel)
        self.mainWindow.toolbar.addWidget(self.artistSearchBox)
        self.mainWindow.toolbar.addWidget(artistSearchButton)

        self.mainWindow.addToolBar(self.mainWindow.toolbar)

    def searchArtists(self):
        self.userInput = self.artistSearchBox.text()
        if self.userInput == '':
            QMessageBox.information(None,'Empty Search','Search box is empty!')
            return

        self.mainWindow.statusBar().showMessage('Searching...')
        self.mainWindow.app.processEvents()

        with psycopg.connect(connString) as conn:
            with conn.cursor() as cur:
                query = """
                SELECT id, name, profile
                FROM artist
                WHERE name ILIKE %s
                """
                cur.execute(query, (f"%{self.userInput}%",))
                results = cur.fetchall()

        self.setRowCount(len(results))
        for i, artist in enumerate(results):
            nameItem = QTableWidgetItem(artist[1])
            nameItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            descriptionItem = QTableWidgetItem(artist[2])
            descriptionItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            selectButton = QPushButton('Select')
            selectButton.clicked.connect(lambda checked, a=artist[0]:self.showArtistMasters(a))

            self.setItem(i, 0, nameItem)
            self.setItem(i, 1, descriptionItem)
            self.setItem(i, 2, QTableWidgetItem())
            self.setCellWidget(i, 2, selectButton)
        
        self.mainWindow.statusBar().showMessage(f"Found {len(results)} artists")

    def showArtistMasters(self, artistID):
        artistMastersListPage = ArtistMastersListPage(self.mainWindow,artistID)
        self.mainWindow.pages.addWidget(artistMastersListPage)
        self.mainWindow.pages.setCurrentWidget(artistMastersListPage)
        
class ArtistMastersListPage(QTableWidget):
        def __init__(self, mainWindow, artistID):
            super().__init__(mainWindow)
            self.mainWindow = mainWindow

            with psycopg.connect(connString) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name FROM artist WHERE id = %s", (artistID,))
                    self.mainWindow.statusBar().showMessage(cur.fetchone()[0])

                    query = """
                    SELECT master.id, master.title, master.year
                    FROM master_artist
                    JOIN master ON master.id = master_id
                    JOIN artist ON artist.id = artist_id
                    WHERE artist.id = %s
                    ORDER BY master.year DESC
                    """
                    cur.execute(query, (artistID,))
                    results = cur.fetchall()

            self.setRowCount(len(results))
            self.setColumnCount(2)
            self.setHorizontalHeaderLabels(['Title','Release Year'])
            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            for i, master in enumerate(results):
                titleItem = QTableWidgetItem(master[1])
                titleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                yearItem = QTableWidgetItem(str(master[2]))
                yearItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

                self.setItem(i, 0, titleItem)
                self.setItem(i, 1, yearItem)

            self.mainWindow.removeToolBar(self.mainWindow.toolbar)
            self.mainWindow.toolbar = ReturnToolBar(self)
            self.mainWindow.addToolBar(self.mainWindow.toolbar)
            

class ReturnToolBar(QToolBar):
    def __init__(self, currPage):
        super().__init__()
        self.currPage = currPage

        returnButton = QPushButton('Return')
        returnButton.clicked.connect(self.setPreviousWindow)
        self.addWidget(returnButton)

    def setPreviousWindow(self):
        curr_index = self.currPage.mainWindow.pages.currentIndex()
        self.currPage.mainWindow.pages.removeWidget(self.currPage)
        self.currPage.mainWindow.pages.setCurrentIndex(curr_index - 1)
        self.currPage.mainWindow.statusBar().clearMessage()
        try:
            self.currPage.mainWindow.pages.currentWidget().initToolBar()
        except AttributeError:
            self.currPage.mainWindow.removeToolBar(self)