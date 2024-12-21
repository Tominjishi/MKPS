from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidgetItem,
    QPushButton
)
from PySide6.QtCore import Qt
import math

from ui.components.release_group_browser import ReleaseGroupBrowser
from services.musicbrainz_api import browseReleaseGroups


class ReleaseGroupListPage(QWidget):
    # Constants
    PAGE_SIZE = 25

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        layout = QVBoxLayout(self)

        self.artistNameLabel = QLabel(self)
        self.artistNameLabel.setStyleSheet('font-size: 21px;')

        # Album Table
        # Title
        self.albumTableTitle = QLabel('Albums', self)
        self.albumTableTitle.setStyleSheet('font-size: 16px;')
        # Table Browser
        self.albumTableBrowser = ReleaseGroupBrowser(self)
        # Page navigation
        self.albumTableBrowser.prevButton.clicked.connect(
            lambda checked, browser=self.albumTableBrowser, releaseType='album':self.previousPage(browser, releaseType)
        )
        self.albumTableBrowser.nextButton.clicked.connect(
            lambda checked, browser=self.albumTableBrowser, releaseType='album':self.nextPage(browser, releaseType)
        )

        # EP Table
        # Title
        self.epTableTitle = QLabel("EP's", self)
        self.epTableTitle.setStyleSheet('font-size: 16px;')
        # Table Browser
        self.epTableBrowser = ReleaseGroupBrowser(self)
        #Page Navigation
        self.epTableBrowser.prevButton.clicked.connect(
            lambda checked, browser=self.epTableBrowser, releaseType='ep':self.previousPage(browser, releaseType)
        )
        self.epTableBrowser.nextButton.clicked.connect(
            lambda checked, browser=self.epTableBrowser, releaseType='ep':self.nextPage(browser, releaseType)
        )

        layout.addWidget(self.artistNameLabel)
        layout.addWidget(self.albumTableTitle)
        layout.addWidget(self.albumTableBrowser)
        layout.addWidget(self.epTableTitle)
        layout.addWidget(self.epTableBrowser)

    def populateWidget(self, artistMBID, artistName = ''):
        self.artistMBID = artistMBID
        self.artistNameLabel.setText(artistName)

        # Init Album
        albumResult = browseReleaseGroups(
            artist=self.artistMBID,
            release_type='album',
            limit=self.PAGE_SIZE
        )
        albumCount = albumResult.get('release-group-count', 0)
        albumList = albumResult.get('release-group-list', [])
        self.albumTableTitle.setText(f"Albums ({albumCount})")
        self.initTableBrowser(self.albumTableBrowser, albumCount, albumList)

        # Init EP
        epResult = browseReleaseGroups(
            artist=self.artistMBID,
            release_type='ep',
            limit=self.PAGE_SIZE
        )
        epCount = epResult.get('release-group-count', 0)
        epList = epResult.get('release-group-list', [])
        self.epTableTitle.setText(f"EP's ({epCount})")
        self.initTableBrowser(self.epTableBrowser, epCount, epList)

    def initTableBrowser(self, tableBrowser, releaseCount, releaseList):
        if releaseCount == 0 or not releaseList:
            tableBrowser.table.hide()
            tableBrowser.paginationButtons.hide()
            tableBrowser.emptyLabel.show()
        else:
            tableBrowser.table.show()
            tableBrowser.emptyLabel.hide()
            tableBrowser.currPage = 1
    
            if releaseCount > self.PAGE_SIZE:
                tableBrowser.paginationButtons.show()
                tableBrowser.pageCount = math.ceil(releaseCount / self.PAGE_SIZE)
                tableBrowser.pageLabel.setText(f"Page 1/{tableBrowser.pageCount}")
                tableBrowser.prevButton.setDisabled(True)
                tableBrowser.nextButton.setDisabled(False)
            else:
                tableBrowser.paginationButtons.hide()

            self.populateTable(tableBrowser, releaseList)

    def populateTable(self, tableBrowser, releaseList):
        rowCount = len(releaseList)
        tableBrowser.table.setRowCount(rowCount)

        for i, releaseGroup in enumerate(releaseList):
            rowNumber = (tableBrowser.currPage - 1) * self.PAGE_SIZE + i + 1
            tableBrowser.table.setVerticalHeaderItem(i, QTableWidgetItem(str(rowNumber)))

            titleItem = QTableWidgetItem(releaseGroup.get('title'))
            titleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            typeItem = QTableWidgetItem(releaseGroup.get('type'))
            typeItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            yearItem = QTableWidgetItem(releaseGroup.get('first-release-date')[:4])
            yearItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            selectButton = QPushButton('Select', tableBrowser.table)
            selectButton.clicked.connect(
                lambda checked, a=releaseGroup['id']:self.navigateToReleaseGroupCardPage(a)
            )

            # coverResponseTuple = getReleaseGroupFrontCoverData(releaseGroup['id'],'s')
            # if coverResponseTuple[0] == 200:
            #     pixmap = QPixmap()
            #     pixmap.loadFromData(coverResponseTuple[1])
            #     icon = QIcon(pixmap)
            #     coverItem = QTableWidgetItem(icon,'')
            # else:
            #     coverItem = QTableWidgetItem(coverResponseTuple[1])
            #     print(f"Error {coverResponseTuple[0]} for release group {releaseGroup['id']}")

            tableBrowser.table.setItem(i, 0, titleItem)
            tableBrowser.table.setItem(i, 1, typeItem)
            tableBrowser.table.setItem(i, 2, yearItem)
            tableBrowser.table.setItem(i, 3, QTableWidgetItem())
            tableBrowser.table.setCellWidget(i, 3, selectButton)

    def previousPage(self, tableBrowser, releaseType):
        tableBrowser.currPage -= 1
        self.switchPage(tableBrowser, releaseType)

    def nextPage(self, tableBrowser, releaseType):
        tableBrowser.currPage += 1
        self.switchPage(tableBrowser, releaseType)

    def switchPage(self, tableBrowser, releaseType):
        tableBrowser.prevButton.setDisabled(tableBrowser.currPage == 1)
        tableBrowser.nextButton.setDisabled(tableBrowser.currPage == tableBrowser.pageCount)

        tableBrowser.table.clearContents()
        tableBrowser.pageLabel.setText(f"Page {tableBrowser.currPage}/{tableBrowser.pageCount}")

        result = browseReleaseGroups(
            artist=self.artistMBID,
            release_type=releaseType,
            limit=self.PAGE_SIZE,
            offset=(tableBrowser.currPage - 1) * self.PAGE_SIZE
        )
        releaseList = result.get('release-group-list',[])
        self.populateTable(tableBrowser, releaseList)

    def navigateToReleaseGroupCardPage(self, releaseGroupMBID):
        self.mainWindow.releaseGroupCardPage.populateFromAPI(releaseGroupMBID)
        self.mainWindow.navigateToPage(self.mainWindow.releaseGroupCardPage)