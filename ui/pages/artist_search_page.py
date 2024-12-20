from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem
)
from PySide6.QtCore import Qt

from services.musicbrainz_api import searchArtists

class ArtistSearchPage(QWidget):
    # Constants
    COLUMN_COUNT = 3

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        layout = QVBoxLayout(self)

        searchBar = QHBoxLayout()
        searchLabel = QLabel('Search artists:', self)
        self.searchBox = QLineEdit(self)
        searchButton = QPushButton('Search', self)
        self.searchBox.returnPressed.connect(self.searchArtists)
        searchButton.clicked.connect(self.searchArtists)

        searchBar.addWidget(searchLabel)
        searchBar.addWidget(self.searchBox)
        searchBar.addWidget(searchButton)

        self.resultTable = QTableWidget(self)
        self.resultTable.setColumnCount(self.COLUMN_COUNT)
        self.resultTable.hide()

        self.resultTable.setHorizontalHeaderLabels(['Name','Description',''])
        self.resultTable.setColumnWidth(0, 200)
        self.resultTable.setColumnWidth(1, 400)
        header = self.resultTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setStretchLastSection(False)

        self.noResultsLabel = QLabel('No results found.', self)
        self.noResultsLabel.setStyleSheet('font-size: 14px; color: gray;')
        self.noResultsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.noResultsLabel.hide()
        
        layout.addLayout(searchBar)
        layout.addWidget(self.noResultsLabel)
        layout.addWidget(self.resultTable)

    def searchArtists(self):
        userInput = self.searchBox.text()
        if userInput == '':
            QMessageBox.information(None, 'Empty Search', 'Search box is empty!')
            return
        
        self.mainWindow.statusBar().showMessage('Searching...')
        self.mainWindow.app.processEvents()


        result = searchArtists(userInput)
        artistCount = result.get('artist-count', 0)
        artistList = result.get('artist-list', [])

        if artistCount == 0 or not artistList:
            self.resultTable.hide()
            self.noResultsLabel.show()
            self.mainWindow.statusBar().showMessage('Found 0 artists')
            return
        else:
            self.resultTable.show()
            self.noResultsLabel.hide()

        self.resultTable.setRowCount(artistCount)
        for i, artist in enumerate(artistList):
            artistName = artist.get('name')
            nameItem = QTableWidgetItem(artistName)
            nameItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            disambiguationItem = QTableWidgetItem(artist.get('disambiguation', 'None'))
            disambiguationItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            artistMBID = artist.get('id', None)
            if artistMBID:
                selectButton = QPushButton('Select', self.resultTable)
                selectButton.clicked.connect(
                    lambda checked, a=artistMBID, b=artistName:self.navigateToReleaseGroupListPage(a,b)
                )
            else:
                selectButton = QLabel('-', self)

            self.resultTable.setItem(i, 0, nameItem)
            self.resultTable.setItem(i, 1, disambiguationItem)
            self.resultTable.setItem(i, 2, QTableWidgetItem())
            self.resultTable.setCellWidget(i, 2, selectButton)
        
        self.mainWindow.statusBar().showMessage(f"Found {artistCount} artists")

    def navigateToReleaseGroupListPage(self, artistMBID, artistName):
        self.mainWindow.releaseGroupListPage.populateWidget(artistMBID,artistName)
        self.mainWindow.navigateToPage(self.mainWindow.releaseGroupListPage)