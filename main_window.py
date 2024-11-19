from PySide6.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize, Qt
import discogs_client as discogs
from urllib.request import Request, urlopen
import webbrowser

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

        results = d.search(artist='Weezer',type='master',format='album')
        
        albumLayout = QGridLayout()
        albumPixmap = QPixmap()
        albumSize = QSize(200,200)
     
        rowCount = 0
        columnCount = 0
        for master in results:
            albumPixmap.loadFromData(getImgDataFromLink(master.images[0]['uri']))
            # pixmap = pixmap.scaled(albumSize,aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio,mode=Qt.TransformationMode.FastTransformation)

            albumButton = QPushButton(icon=albumPixmap)
            albumButton.setIconSize(albumSize)
            albumButton.setFixedSize(albumSize)
            albumButton.clicked.connect(lambda checked, a=master.url: webbrowser.open(a))

            albumLayout.addWidget(albumButton,rowCount,columnCount)

            columnCount += 1
            if columnCount == 6:
                rowCount += 1
                columnCount = 0
        

        widget = QWidget()
        widget.setLayout(albumLayout)
        self.setCentralWidget(widget)

        
