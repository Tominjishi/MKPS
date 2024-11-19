from PySide6.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget, QToolBar, QLineEdit, QLabel, QStatusBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize
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
        
        self.albumLayout = QGridLayout()
        self.albumSize = QSize(200,200)

        mainWidget = QWidget()
        mainWidget.setLayout(self.albumLayout)
        self.setCentralWidget(mainWidget)

        toolbar = QToolBar()
        artistSearchLabel = QLabel(f"Search artist's discography:  ")
        self.artistSearchBox = QLineEdit()
        artistSearchButton = QPushButton('Enter')
        self.artistSearchBox.returnPressed.connect(self.populateGrid)
        artistSearchButton.clicked.connect(self.populateGrid)
        toolbar.addWidget(artistSearchLabel)
        toolbar.addWidget(self.artistSearchBox)
        toolbar.addWidget(artistSearchButton)
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())

    
    def populateGrid(self):
        startTime = time.time()

        while self.albumLayout.count():
            child = self.albumLayout.takeAt(0)
            child.widget().deleteLater()
        
        albumPixmap = QPixmap()

        results = d.search(artist=self.artistSearchBox.text(),type='master',format='album',sort='year')
        albumCount = len(results)
        albumButtons = []
        for i, master in enumerate(results):
            print(master)
            try:
                albumPixmap.loadFromData(getImgDataFromLink(master.images[0]['uri']))
                # pixmap = pixmap.scaled(albumSize,aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio,mode=Qt.TransformationMode.FastTransformation)

                albumButton = QPushButton(icon=albumPixmap)
                albumButton.setIconSize(self.albumSize)
                albumButton.setFixedSize(self.albumSize)
                albumButton.clicked.connect(lambda checked, a=master.url: webbrowser.open(a))

                albumButtons.append(albumButton)

            except HTTPError as e:
                if e.status_code == 404:
                    print(f"Skipping non-existent master release: {master}")
                else:
                    raise

            self.statusBar().showMessage(f"Processed {i+1} of {albumCount}")
            self.app.processEvents()

        rowCount = 0
        columnCount = 0
        for album in albumButtons:
            self.albumLayout.addWidget(album,rowCount,columnCount)
            columnCount += 1
            if columnCount == 6:
                rowCount += 1
                columnCount = 0
        self.statusBar().showMessage(f"Found {len(albumButtons)} albums by {self.artistSearchBox.text()} in {round(time.time() - startTime,2)}s")

