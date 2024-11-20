from PySide6.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget, QToolBar, QLineEdit, QLabel, QStatusBar, QButtonGroup, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize , Qt
import discogs_client as discogs
from discogs_client.exceptions import HTTPError
from urllib.request import Request, urlopen
import webbrowser
import time

d = discogs.Client('mkps', user_token='vnRSeBrormvwiawEirpmXqhlUnedHQWEKYCMDrzP')

# d = discogs_client.Client(
#     'mkps',
#     consumer_key='SRxPQVqksmdWkRaxLpZO',
#     consumer_secret='lnDYNGkWKoZYPttqedeaRWUtmdOyFCJF'
# )

def getImgDataFromMasterID(ID):
    release = d.master(ID)
    req = Request(release.images[0]['uri'], headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    return data

def getImgDataFromLink(imgLink):
    req = Request(imgLink, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    return data

class MainWindow(QMainWindow):
    def __init__ (self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle('MKPS')
        self.resize(self.width(),250)

        self.gridItemSize = QSize(200,200)
        self.tableIconSize = 50

        self.albums = []

        toolbar = QToolBar()

        artistSearchLabel = QLabel(f"Search artist's discography:  ")
        self.artistSearchBox = QLineEdit()
        self.artistSearchBox.returnPressed.connect(self.searchAlbums)
        artistSearchButton = QPushButton('Search')
        artistSearchButton.clicked.connect(self.searchAlbums)

        self.gridViewButton = QPushButton(icon=QIcon("./images/gridView.png"))
        self.gridViewButton.setCheckable(True)
        self.gridViewButton.setChecked(True)
        tableViewButton = QPushButton(icon=QIcon("./images/tableView.png"))
        tableViewButton.setCheckable(True)
        viewButtonGroup = QButtonGroup(self)
        viewButtonGroup.addButton(self.gridViewButton)
        viewButtonGroup.addButton(tableViewButton)
        self.gridViewButton.toggled.connect(self.setView)

        toolbar.addWidget(artistSearchLabel)
        toolbar.addWidget(self.artistSearchBox)
        toolbar.addWidget(artistSearchButton)
        toolbar.addSeparator()
        toolbar.addWidget(self.gridViewButton)
        toolbar.addWidget(tableViewButton)
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())

    
    def searchAlbums(self):
        if self.artistSearchBox.text() == '':
            self.statusBar().showMessage('Empty search string!')
            return
        
        startTime = time.time()
        self.albums.clear()

        results = d.search(artist=self.artistSearchBox.text(),type='master',format='album',sort='year')
        resultCount = len(results)
        self.statusBar().showMessage(f"Processed 0 of {resultCount}")
        self.app.processEvents()
        for i, master in enumerate(results):
            print(master)
            try:
                albumPixmap = QPixmap()
                albumPixmap.loadFromData(getImgDataFromLink(master.images[0]['uri']))
                styleList = master.styles
                styles = ''
                for style in styleList:
                    if style == styleList[-1]:
                        styles += style
                    else:
                        styles += f"{style}, "
                self.albums.append({
                    'cover': albumPixmap,
                    'url': master.url,
                    'title': master.title,
                    'styles': styles,
                    'year': master.main_release.year})

            except HTTPError as e:
                if e.status_code == 404:
                    print(f"Skipping non-existent master release: {master}")
                else:
                    raise
            self.statusBar().showMessage(f"Processed {i+1} of {resultCount}")
            self.app.processEvents()
        
        self.statusBar().showMessage(f"Found {len(self.albums)} albums by {self.artistSearchBox.text()} in {round(time.time() - startTime,2)}s")
        self.setView()
        

    def setView(self):
        #self.clearLayout()
        if self.gridViewButton.isChecked():
            self.fillGrid()
        else:
            self.fillTable()

    def fillGrid(self):
        gridWidget = QWidget()
        layout = QGridLayout()
        rowCount = 0
        columnCount = 0
        for album in self.albums:
            gridItem = QPushButton(icon=album['cover'])
            gridItem.setIconSize(self.gridItemSize)
            gridItem.setFixedSize(self.gridItemSize)
            gridItem.clicked.connect(lambda checked, a=album['url']:webbrowser.open(a))
            layout.addWidget(gridItem,rowCount,columnCount)
            columnCount += 1
            if columnCount == 6:
                rowCount += 1
                columnCount = 0

        gridWidget.setLayout(layout)
        self.setCentralWidget(gridWidget)

    def fillTable(self):
        table = QTableWidget()
        table.setRowCount(len(self.albums))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['Cover','Title','Genre','Release Year','Discogs Page'])
        table.setIconSize(QSize(self.tableIconSize,self.tableIconSize))
        table.verticalHeader().setDefaultSectionSize(self.tableIconSize)
        #table.setColumnWidth(0, self.tableIconSize)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        for i, album in enumerate(self.albums):
            coverItem = QTableWidgetItem(QIcon(album['cover']), '')
            coverItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            titleItem = QTableWidgetItem(album['title'])
            titleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            stylesItem = QTableWidgetItem(album['styles'])
            stylesItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            yearItem = QTableWidgetItem(str(album['year']))
            yearItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            linkButton = QPushButton('Link')
            linkButton.clicked.connect(lambda checked, a=album['url']:webbrowser.open(a))

            table.setItem(i, 0, coverItem)
            table.setItem(i, 1, titleItem)
            table.setItem(i, 2, stylesItem)
            table.setItem(i, 3, yearItem)
            table.setItem(i, 4, QTableWidgetItem())
            table.setCellWidget(i, 4, linkButton)

        self.setCentralWidget(table)

    # def clearLayout(self):
    #     if self.mainWidget.layout() is not None:
    #         while self.mainWidget.layout().count():
    #             child = self.mainWidget.layout().takeAt(0)
    #             child.widget().deleteLater()
    #         self.mainWidget.layout().deleteLater()


