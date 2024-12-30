# ui
from PySide6.QtWidgets import(
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QSizePolicy,
    QListWidget,
    QDialog,
    QMessageBox,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtSql import QSqlDatabase, QSqlQuery
# api services
from services.musicbrainz_api import browseReleases, lookupReleaseGroupDict
from services.cover_art_archive import getReleaseGroupFrontCoverData

class ReleaseGroupCardPage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.db = QSqlDatabase().database()
        # self.tempCollectionEntry = {
        #     "release_group_mbid": '',
        #     "type": '',
        #     "title": '',
        #     "release_date": '',
        #     "format": '',
        #     "artist_credit_phrase": '',
        #     "cover": None,
        # }
        self.tempCollectionEntry = {}
        self.tracks = []
        self.formatOptionMapping = []

        mainLayout = QHBoxLayout(self)

        # Layout for left side (img and button/combobox under)
        leftLayout = QVBoxLayout()
        
        self.imgLabel = QLabel(self)
        self.imgLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.imgLabel.setAlignment(Qt.AlignCenter)

        self.addButton = QPushButton('Add to collection', self)
        self.addButton.clicked.connect(self.runAddDialog)
        # self.addButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.formatOption = QComboBox(self)
        self.formatOption.currentIndexChanged.connect(self.switchFormat)

        leftLayout.addWidget(self.imgLabel)
        leftLayout.addWidget(self.addButton)
        leftLayout.addWidget(self.formatOption)
        leftLayout.addStretch()
        # Hide button (API) and combobox (local)
        self.addButton.hide()
        self.formatOption.hide()

        # Right side
        rightLayout = QVBoxLayout()

        self.artistTitleLabel = QLabel(self)
        self.artistTitleLabel.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.artistTitleLabel.setAlignment(Qt.AlignLeft)

        self.typeLabel = QLabel(self)
        self.typeLabel.setStyleSheet("font-size: 15px;")
        self.typeLabel.setAlignment(Qt.AlignLeft)

        self.releaseDateLabel = QLabel(self)
        self.releaseDateLabel.setAlignment(Qt.AlignLeft)
        self.genreLabel = QLabel(self)
        self.genreLabel.setAlignment(Qt.AlignLeft)

        self.trackListWidget = QListWidget(self)
        # self.trackListWidget.setMaximumHeight(300)

        rightLayout.addWidget(self.artistTitleLabel)
        rightLayout.addWidget(self.typeLabel)
        rightLayout.addWidget(self.releaseDateLabel)
        rightLayout.addWidget(self.genreLabel)
        rightLayout.addWidget(self.trackListWidget)
        rightLayout.addStretch()     
    
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        mainLayout.setContentsMargins(20, 20, 20, 20)

        # Dialog for creating collection entry
        self.addDialog = QDialog(self)
        self.addDialog.setModal(True)
        self.addDialog.setWindowTitle('Add to collection')
        self.addDialog.setFixedWidth(200)
        addDialogLayout = QVBoxLayout(self.addDialog)
        # Format Choice
        formatLabel = QLabel('Choose a format')
        self.formatDropdown = QComboBox(self.addDialog)
        # Tracklist information
        tracklistChangeInfo = QLabel('You may change the tracklist later')
        # Buttons
        buttonLayout = QHBoxLayout()
        addDialogAddButton = QPushButton('Add')
        addDialogAddButton.setDefault(True)
        addDialogCancelButton = QPushButton('Cancel')
        addDialogAddButton.clicked.connect(self.checkFormat)
        addDialogCancelButton.clicked.connect(self.addDialog.reject)
        buttonLayout.addWidget(addDialogAddButton)
        buttonLayout.addWidget(addDialogCancelButton)

        addDialogLayout.addWidget(formatLabel)
        addDialogLayout.addWidget(self.formatDropdown)
        addDialogLayout.addWidget(tracklistChangeInfo)
        addDialogLayout.addLayout(buttonLayout)
       
    def populateFromAPI(self, releaseGroupMBID):
        self.addButton.show()
        self.formatOption.hide()
        self.tempCollectionEntry.clear()
        self.tracks.clear()

        releaseGroupResponse = lookupReleaseGroupDict(releaseGroupMBID, 'genres+artists') 
        if releaseGroupResponse[0] == 200:
            result = releaseGroupResponse[1]
            # Get artist credit phrase and individual artist list
            self.tempCollectionEntry['artist_credit_phrase'] = ''
            self.artists = []
            for artist in result.get('artist-credit',[]):
                name = artist.get('name')
                joinphrase = artist.get('joinphrase')
                self.tempCollectionEntry['artist_credit_phrase'] += name + joinphrase

                artistDict = artist.get('artist')
                self.artists.append(artistDict)

            self.tempCollectionEntry['release_group_mbid'] = result.get('id')
            self.tempCollectionEntry['title'] = result.get('title')
            self.tempCollectionEntry['type'] = result.get('primary-type')
            self.tempCollectionEntry['release_date'] = result.get('first-release-date')

            genres = result.get('genres', [])
            if genres:
                self.sortedGenres = sorted(genres, key=lambda a: a['count'], reverse=True)
            else:
                self.sortedGenres = []
        else:
            # handle error
            # self.collectionEntryGroupBox.setTitle(releaseGroupResponse[1])
            return
        
        # Get front cover
        coverResponse = getReleaseGroupFrontCoverData(releaseGroupMBID,'s')
        requestStatusCode = coverResponse[0]
        requestContent = coverResponse[1]
        if requestStatusCode == 200:
            self.tempCollectionEntry['cover'] = QByteArray(requestContent)
        else:
            self.tempCollectionEntry['cover'] = None

        # Get formats and tracks
        formatsTracksTuple = self.getFormatsAndTracks(releaseGroupMBID)
        self.formats = formatsTracksTuple[0]
        self.tracks = formatsTracksTuple[1]

        self.fillWidget()

    def getFormatsAndTracks(self, releaseGroupMBID):
        formats = set()
        tracks = []

        releasesPerRequest = 100
        
        result = browseReleases(
            release_group=releaseGroupMBID,
            limit=releasesPerRequest,
            includes = ['media', 'recordings']
        )

        releaseList = result.get('release-list',[])
        releaseCount = result.get('release-count')

        if releaseCount > releasesPerRequest:
            for offset in range(releasesPerRequest, releaseCount, releasesPerRequest):
                result = browseReleases(
                    release_group=releaseGroupMBID,
                    limit=releasesPerRequest,
                    offset=offset,
                    includes='media'
            )
            releaseList.extend(result.get('release-list',[]))

        for release in releaseList:
            for medium in release.get('medium-list', []):
                mediaformat = medium.get('format')
                if mediaformat:
                    formats.add(mediaformat)

                if not tracks:
                    trackList = medium.get('track-list', [])
                    for track in trackList:
                        recording = track.get('recording',{})
                        if recording:
                            tracks.append(
                                {
                                    'number': track.get('number'),
                                    'title': recording.get('title'),
                                    'length': int(recording.get('length', 0))
                                }
                            )
        return (formats, tracks)

    def fillWidget(self):
        if self.tempCollectionEntry['cover']:
            pixmap = QPixmap()
            pixmap.loadFromData(self.tempCollectionEntry['cover'])
            self.imgLabel.setPixmap(pixmap)
            self.addButton.setFixedWidth(pixmap.width())
            self.formatOption.setFixedWidth(pixmap.width())
            self.imgLabel.show()
        else:
            self.imgLabel.hide()

        pageTitle = (
            self.tempCollectionEntry['artist_credit_phrase']
            + ' - '
            + self.tempCollectionEntry['title']
        )
        self.artistTitleLabel.setText(pageTitle)

        self.typeLabel.setText(self.tempCollectionEntry['type'])
        self.releaseDateLabel.setText(self.tempCollectionEntry['release_date'])

        if self.sortedGenres:
            self.genreLabel.show()
            genreList = ', '.join(genre['name'].capitalize() for genre in self.sortedGenres)
            self.genreLabel.setText('Genres: ' + genreList)
        else:
            self.genreLabel.hide()

        if self.tracks:
            self.trackListWidget.show()
            self.trackListWidget.clear()
            for track in self.tracks:
                num = track['number']
                title = track['title']

                totalLengthMS = track['length']
                totalLengthS = totalLengthMS / 1000
                minutes = int(totalLengthS // 60)
                seconds = round(totalLengthS % 60)

                self.trackListWidget.addItem(f"{num} {title} ({minutes}:{seconds:02})")
        else:
            self.trackListWidget.hide()

    def runAddDialog(self):
        self.formatDropdown.clear()
        self.formatDropdown.addItems(self.formats)
        if self.addDialog.exec():
            if self.db.open():
                self.db.transaction()
                try:
                    query = QSqlQuery()
                    # Insert collection_entry record
                    query.prepare(
                        """INSERT INTO collection_entry(
                            release_group_mbid,
                            type,
                            title,
                            release_date,
                            format,
                            artist_credit_phrase,
                            cover
                        )
                        VALUES(
                            :release_group_mbid,
                            :type,
                            :title,
                            :release_date,
                            :format,
                            :artist_credit_phrase, 
                            :cover
                        )"""
                    )
                    
                    for key in self.tempCollectionEntry.keys():
                        query.bindValue(f":{key}", self.tempCollectionEntry[key])
                    if not query.exec():
                        raise Exception(
                            'Insert collection entry failed: ' + query.lastError().text()
                        )
                    collectionEntryID = query.lastInsertId()

                    for artist in self.artists:
                        artistMBID = artist['id']
                        # Check if artist record already exists
                        query.prepare("SELECT COUNT(*) FROM artist WHERE mbid = :mbid")
                        query.bindValue(':mbid', artistMBID)
                        if not query.exec():
                            raise Exception(
                                'Check artist failed: ' + query.lastError().text()
                            )
                        query.next()
                        if query.value(0) == 0:
                            # Insert artist record
                            query.prepare(
                                """INSERT OR IGNORE INTO artist (mbid, type, name)
                                VALUES (:mbid, :type, :name)"""
                            )
                            query.bindValue(':mbid', artistMBID)
                            query.bindValue(':type', artist.get('type'))
                            query.bindValue(':name', artist.get('name'))                      
                            if not query.exec():
                                raise Exception(
                                    'Insert artist failed: ' + query.lastError().text()
                                )
                            for genre in artist.get('genres', []):
                                # Insert genre record if one doesn't exist
                                query.prepare(
                                    """INSERT OR IGNORE INTO genre (mbid, name)
                                    VALUES (:mbid, :name)"""
                                )
                                genreMBID = genre['id']
                                query.bindValue(':mbid', genreMBID)
                                query.bindValue(':name', genre['name'])
                                if not query.exec():
                                    raise Exception(
                                        'Insert genre failed: ' + query.lastError().text()
                                    )
                                # Insert genre link to artist
                                query.prepare(
                                    """INSERT INTO genre_link (genre_mbid, vote_count, artist_mbid)
                                    VALUES (:genre_mbid, :vote_count, :artist_mbid)"""
                                )
                                query.bindValue(':genre_mbid', genreMBID)
                                query.bindValue(':vote_count', genre['count'])
                                query.bindValue(':artist_mbid', artistMBID)
                                if not query.exec():
                                    raise Exception(
                                        'Insert genre_link failed: ' + query.lastError().text()
                                    )
                        # Insert artist link to collection_entry
                        query.prepare(
                            """INSERT INTO artist_entry_link (collection_entry_id, artist_mbid)
                            VALUES (:collection_entry_id, :artist_mbid)"""
                        )
                        query.bindValue(':collection_entry_id', collectionEntryID)
                        query.bindValue(':artist_mbid', artistMBID)
                        if not query.exec():
                            raise Exception(
                                'Insert artist_entry_link failed: ' + query.lastError().text()
                            )
                    
                    for genre in self.sortedGenres:
                        # Insert genre record if one doesn't exist
                        query.prepare(
                            """INSERT OR IGNORE INTO genre (mbid, name)
                            VALUES (:mbid, :name)"""
                        )
                        genreMBID = genre['id']
                        query.bindValue(':mbid', genreMBID)
                        query.bindValue(':name', genre['name'])
                        if not query.exec():
                            raise Exception(
                                'Insert genre failed: ' + query.lastError().text()
                            )
                        # Insert genre link to collection_entry
                        query.prepare(
                            """INSERT INTO genre_link (genre_mbid, vote_count, collection_entry_id)
                            VALUES (:genre_mbid, :vote_count, :collection_entry_id)"""
                        )
                        query.bindValue(':genre_mbid', genreMBID)
                        query.bindValue(':vote_count', genre['count'])
                        query.bindValue(':collection_entry_id', collectionEntryID)
                        if not query.exec():
                            raise Exception(
                                'Insert genre_link failed: ' + query.lastError().text()
                            )
                        
                    for track in self.tracks:
                        # Insert track record
                        query.prepare(
                            """INSERT INTO track (number, title, length, collection_entry_id)
                            VALUES (:number, :title, :length, :collection_entry_id)"""
                        )
                        query.bindValue(':number', track['number'])
                        query.bindValue(':title', track['title'])
                        query.bindValue(':length', track['length'])
                        query.bindValue(':collection_entry_id', collectionEntryID)
                        if not query.exec():
                            raise Exception(
                                'Insert track failed: ' + query.lastError().text()
                            )
                        
                    self.db.commit()
                    print('Album inserted')
                except Exception as e:
                    print('Error:', e)
                    self.db.rollback()
                finally:
                    self.db.close()
            else:
                print("Failed to open database: ", self.db.lastError().text())

            self.addButton.hide()

    def checkFormat(self):
        self.tempCollectionEntry['format'] = self.formatDropdown.currentText()
        if self.db.open():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT COUNT(*) FROM collection_entry
                    WHERE release_group_mbid = :mbid AND format = :format"""
                )
                query.bindValue(':mbid', self.tempCollectionEntry['release_group_mbid'])
                query.bindValue(':format', self.tempCollectionEntry['format'])
                if not query.exec():
                    raise Exception(
                        'Check format failed: ' + query.lastError().text()
                    )
                query.next()
                if query.value(0) != 0:
                    ret = QMessageBox.warning(
                        self.addDialog,
                        'Duplicate format',
                        (
                            f"You already have {self.tempCollectionEntry['title']} in the "
                            f"{self.tempCollectionEntry['format']} format in your collection"
                            "\nWould you like to add another one?"
                        ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if ret == QMessageBox.No:
                        return
            except Exception as e:
                print('Error:', e)        
        else:
            print("Failed to open database: ", self.db.lastError().text())

        self.addDialog.accept()

    def populateFromDatabase(self, collectionEntry):
        self.addButton.hide()
        self.formatOption.show()
        self.formatOption.clear()
        self.formatOptionMapping.clear()
        self.tempCollectionEntry.clear()
        self.tracks.clear()

        self.tempCollectionEntry['release_group_mbid'] = collectionEntry['release_group_mbid']

        if self.db.open():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT id, format
                    FROM collection_entry
                    WHERE release_group_mbid = :mbid"""
                )
                query.bindValue(':mbid', self.tempCollectionEntry['release_group_mbid'])
                if not query.exec():
                    raise Exception(
                        'Format fetch failed: : ' + query.lastError().text()
                    )
                
                self.formatOption.blockSignals(True)
                while query.next():
                    self.formatOption.addItem(query.value('format'))
                    self.formatOptionMapping.append(query.value('id'))
                self.formatOption.blockSignals(False)

                query.prepare(
                    """SELECT number, title, length
                    FROM track
                    WHERE collection_entry_id = :id"""
                )
                query.bindValue(':id', self.formatOptionMapping[0])
                if not query.exec():
                    raise Exception(
                        'Track fetch failed: : ' + query.lastError().text()
                    )
                self.trackListWidget.show()
                while query.next():
                    self.tracks.append(
                        {
                            'number': query.value('number'),
                            'title': query.value('title'),
                            'length': query.value('length')
                        }
                    )
            except Exception as e:
                print('Error:', e)
                self.trackListWidget.hide()
        else:
            print("Failed to open database: ", self.db.lastError().text())
            self.trackListWidget.hide()

        self.tempCollectionEntry['id'] = collectionEntry['id']
        self.tempCollectionEntry['cover'] = collectionEntry['cover']
        self.tempCollectionEntry['artist_credit_phrase'] = collectionEntry['artist_credit_phrase']
        self.tempCollectionEntry['title'] = collectionEntry['title']
        self.tempCollectionEntry['type'] = collectionEntry['type'][0]
        self.tempCollectionEntry['release_date'] = collectionEntry['release_date']
        self.sortedGenres = [{'name': genre} for genre in collectionEntry['genres']]

        self.fillWidget()

    def switchFormat(self, index):
        colEntryID = self.formatOptionMapping[index]
        self.tracks.clear()
        if self.db.open():
            try:
                query = QSqlQuery()
                query.prepare(
                    """SELECT number, title, length
                    FROM track
                    WHERE collection_entry_id = :id"""
                )
                query.bindValue(':id', colEntryID)
                if not query.exec():
                    raise Exception(
                        'Track fetch failed: : ' + query.lastError().text()
                    )
                self.trackListWidget.show()
                while query.next():
                    self.tracks.append(
                        {
                            'number': query.value('number'),
                            'title': query.value('title'),
                            'length': query.value('length')
                        }
                    )
            except Exception as e:
                print('Error:', e)
                self.trackListWidget.hide() 
        else:
            print("Failed to open database: ", self.db.lastError().text())
            self.trackListWidget.hide()
