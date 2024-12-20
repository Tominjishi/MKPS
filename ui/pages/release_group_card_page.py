from PySide6.QtWidgets import(
    QWidget,
    QLabel,
    QGridLayout,
    QListWidget,
    QListWidgetItem
)
from PySide6.QtGui import QPixmap

from services.musicbrainz_api import getReleaseGroupByID, browseReleases
from services.cover_art_archive import getReleaseGroupFrontCoverData

class ReleaseGroupCardPage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.layout = QGridLayout(self)

        self.imgLabel = QLabel()

        self.layout.addWidget(self.imgLabel, 0, 2, 2, 2)
        
    def populateWidget(self, releaseGroupMBID):
        result = getReleaseGroupByID(
            id=releaseGroupMBID,
            includes=['artists', 'releases', 'media']
        )
        releaseGroup = result.get('release-group')
        
        # Fill data
        self.releaseGroupMBID = releaseGroupMBID
        self.type = releaseGroup.get('type')
        self.title = releaseGroup.get('title')
        self.releaseDate = releaseGroup.get('first-release-date','Unknown')
        self.artistCreditPhrase = releaseGroup.get('artist-credit-phrase')
        self.artists = []
        credit = releaseGroup.get('artist-credit', [])
        for artist in credit:
            if not isinstance(artist, str):
                self.artists.append(artist)

        # Get formats
        releaseCount = releaseGroup.get('release-count',0)
        releaseList = releaseGroup.get('release-list',[])
        self.formats = self.getFormats(releaseGroupMBID, releaseCount, releaseList)

        # Get front cover
        coverResponse = getReleaseGroupFrontCoverData(releaseGroupMBID,'s')
        requestStatusCode = coverResponse[0]
        requestContent = coverResponse[1]
        if requestStatusCode == 200:
            self.imgData = requestContent
            pixmap = QPixmap()
            pixmap.loadFromData(requestContent)
            self.imgLabel.setPixmap(pixmap)
        else:
            self.imgLabel.setText(requestContent)

        self.tempFillPage()

    def getFormats(self, releaseGroupMBID, totalReleaseCount, firstReleaseList):
        formats = set()
        releaseList = firstReleaseList

        if totalReleaseCount > 25:
            for offset in range(25, totalReleaseCount, 25):
                result = browseReleases(
                    release_group=releaseGroupMBID,
                    offset=offset,
                    includes='media'
                )
                releaseList.extend(result.get('release-list',[]))

        for release in releaseList:
            for medium in release.get('medium-list', []):
                mediaformat = medium.get('format')
                if mediaformat:
                    formats.add(mediaformat)

        return formats

    def tempFillPage(self):
        dataList = QListWidget()

        dataList.addItem(QListWidgetItem(f"id: {self.releaseGroupMBID}"))
        dataList.addItem(QListWidgetItem(f"type: {self.type}"))
        dataList.addItem(QListWidgetItem(f"title: {self.title}"))
        dataList.addItem(QListWidgetItem(f"release date: {self.releaseDate}"))
        dataList.addItem(QListWidgetItem(f"format list: {self.formats}"))
        dataList.addItem(QListWidgetItem(f"artist credit: {self.artistCreditPhrase}"))
        dataList.addItem(QListWidgetItem("artists:"))
        for artist in self.artists:
            dataList.addItem(QListWidgetItem(str(artist)))

        self.layout.addWidget(dataList, 0, 0, 2, 2)