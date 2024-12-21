from PySide6.QtWidgets import(
    QWidget,
    QLabel,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QComboBox,
    
)
from PySide6.QtGui import QPixmap

from services.musicbrainz_api import getReleaseGroupByID, browseReleases, lookupReleaseGroupDict
from services.cover_art_archive import getReleaseGroupFrontCoverData

class ReleaseGroupCardPage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.tempCollectionEntry = {
            "release_group_mbid": '',
            "type": '',
            "title": '',
            "release_date": '',
            "format": '',
            "artist_credit_phrase": '',
            "cover": None,
        }

        layout = QHBoxLayout(self)

        # Layout for left side (img and button/combobox under)
        leftSideLayout = QVBoxLayout()
        self.imgLabel = QLabel(self)
        self.addButton = QPushButton('Add to collection', self)
        self.formatOption = QComboBox(self)
        leftSideLayout.addWidget(self.imgLabel)
        leftSideLayout.addWidget(self.addButton)
        leftSideLayout.addWidget(self.formatOption)
        # Hide button (API) and combobox (local)
        self.addButton.hide()
        self.formatOption.hide()

        # Right side
        self.collectionEntryGroupBox = QGroupBox()
        self.collectionEntryGroupBox.setStyleSheet("""
            QGroupBox::title {
                font-size: 41px;                                    
                font-weight: bold;
            }
            QGroupBox {
                font-size: 21px;
            }
        """)

        self.typeLabel = QLabel(self.collectionEntryGroupBox)
        self.releaseDateLabel = QLabel(self.collectionEntryGroupBox)
        self.genreLabel = QLabel("Genres", self.collectionEntryGroupBox)
        self.genresListLabel = QLabel('', self.genreLabel)

        collectionEntryLayout = QVBoxLayout(self.collectionEntryGroupBox)
        collectionEntryLayout.addWidget(self.typeLabel)
        collectionEntryLayout.addWidget(self.releaseDateLabel)
        collectionEntryLayout.addWidget(self.genreLabel)
        collectionEntryLayout.addWidget(self.genresListLabel)     
    
        layout.addLayout(leftSideLayout)
        layout.addWidget(self.collectionEntryGroupBox)

        
    def populateFromAPI(self, releaseGroupMBID):
        self.addButton.show()

        result = getReleaseGroupByID(
            id=releaseGroupMBID,
            includes=['artists', 'releases', 'media']
        )
        releaseGroup = result.get('release-group')

        self.artistCredit = releaseGroup.get('artist-credit-phrase', '')
        self.title = releaseGroup.get('title', '')
        groupBoxTitle = self.artistCredit
        if self.artistCredit and self.title:
            groupBoxTitle += ' - '
        groupBoxTitle += self.title
        self.collectionEntryGroupBox.setTitle(groupBoxTitle)

        self.typeLabel.setText(releaseGroup.get('type', ''))
        self.releaseDateLabel.setText(releaseGroup.get('first-release-date', ''))

        # Get genres
        genreRelGroup = lookupReleaseGroupDict(releaseGroupMBID, 'genres')
        if genreRelGroup[0] == 200:
            genres = genreRelGroup[1].get('genres',[])
            self.sortedGenres = sorted(genres, key=lambda a: a['count'], reverse=True)
        else:
            self.sortedGenres = []

        if self.sortedGenres:
            genreList = ''
            self.genreLabel.show()
            iterTimes = min(len(self.sortedGenres), 5)
            for i in range(iterTimes):
                genreList += self.sortedGenres[i]['name'].capitalize()
                if i < iterTimes - 1:
                    genreList += ', '
            self.genresListLabel.setText(genreList)
        else:
            self.genreLabel.hide()
            
        # Get artists
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

        # self.tempFillPage()

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
