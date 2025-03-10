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
# api services
import services.musicbrainz_api as mb
from services.cover_art_archive import get_release_group_front_cover_data
# release class
from data.release import Release

class ReleaseGroupCardPage(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.release = None # instance of Release class

        main_layout = QHBoxLayout(self)

        # Layout for left side (img and button/combobox under)
        left_layout = QVBoxLayout()
        
        self.img_label = QLabel(self)
        self.img_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.add_button = QPushButton('Add to collection', self)
        self.add_button.clicked.connect(self.run_add_dialog)
        # self.addButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        left_layout.addWidget(self.img_label)
        left_layout.addWidget(self.add_button)
        left_layout.addStretch()
        # Hide add button by default
        self.add_button.hide()

        # Right side
        right_layout = QVBoxLayout()

        self.artist_title_label = QLabel(self)
        self.artist_title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.artist_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.type_label = QLabel(self)
        self.type_label.setStyleSheet("font-size: 15px;")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.release_date_label = QLabel(self)
        self.release_date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.genre_label = QLabel(self)
        self.genre_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.track_list_widget = QListWidget(self)
        # self.trackListWidget.setMaximumHeight(300)

        right_layout.addWidget(self.artist_title_label)
        right_layout.addWidget(self.type_label)
        right_layout.addWidget(self.release_date_label)
        right_layout.addWidget(self.genre_label)
        right_layout.addWidget(self.track_list_widget)
        right_layout.addStretch()
    
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Dialog for creating collection entry
        self.add_dialog = QDialog(self)
        self.add_dialog.setModal(True)
        self.add_dialog.setWindowTitle('Add to collection')
        self.add_dialog.setFixedWidth(200)
        add_dialog_layout = QVBoxLayout(self.add_dialog)
        # Format Choice
        format_label = QLabel('Choose a format')
        self.format_dropdown = QComboBox(self.add_dialog)
        # Tracklist information
        tracklist_change_info = QLabel('You may change the tracklist later')
        # Buttons
        button_layout = QHBoxLayout()
        add_dialog_add_button = QPushButton('Add')
        add_dialog_add_button.setDefault(True)
        add_dialog_cancel_button = QPushButton('Cancel')
        add_dialog_add_button.clicked.connect(self.check_format)
        add_dialog_cancel_button.clicked.connect(self.add_dialog.reject)
        button_layout.addWidget(add_dialog_add_button)
        button_layout.addWidget(add_dialog_cancel_button)

        add_dialog_layout.addWidget(format_label)
        add_dialog_layout.addWidget(self.format_dropdown)
        add_dialog_layout.addWidget(tracklist_change_info)
        add_dialog_layout.addLayout(button_layout)

    def populate_from_api(self, release_group_mbid):
        self.add_button.show()

        # Construct Release object from mb API
        release_group_response = mb.lookup_release_group_dict(release_group_mbid, 'genres+artists')
        if release_group_response[0] == 200:
            result = release_group_response[1]

            # Construct artist credit phrase and list of artists
            artist_credit_phrase = ''
            artists = []
            for artist in result.get('artist-credit', []):
                name = artist.get('name')
                joinphrase = artist.get('joinphrase')
                artist_credit_phrase += name + joinphrase
                artists.append(artist.get('artist'))

            # Get album cover
            cover_response = get_release_group_front_cover_data(release_group_mbid, 's')
            if cover_response[0] == 200:
                cover = QByteArray(cover_response[1])
            else:
                cover = None

            # Get and sort genres
            genres = result.get('genres')
            if genres:
                genres = sorted(genres, key=lambda a: a['count'], reverse=True)

            # Get tracks and formats
            formats, tracks = mb.get_formats_and_tracks(release_group_mbid)

            # Add possible formats to dropdown when running add dialog
            self.format_dropdown.clear()
            self.format_dropdown.addItems(formats)

            self.release = Release(result.get('id'), result.get('primary-type'), result.get('title'), artist_credit_phrase,
                              artists, tracks, genres, cover, result.get('first-release-date'))

        else:
            # handle error
            # self.collectionEntryGroupBox.setTitle(release_group_response[1])
            return

        self.fill_widget()



    def fill_widget(self):
        if self.release.cover:
            pixmap = QPixmap()
            pixmap.loadFromData(self.release.cover)
            self.img_label.setPixmap(pixmap)
            self.add_button.setFixedWidth(pixmap.width())
            self.img_label.show()
        else:
            self.img_label.hide()

        page_title = (
            self.release.artist_credit_phrase
            + ' - '
            + self.release.title
        )
        self.artist_title_label.setText(page_title)

        self.type_label.setText(self.release.type)
        self.release_date_label.setText(self.release.release_date)
        if self.release.genres:
            self.genre_label.show()
            if self.release.collection_entry_id:
                genre_list = ', '.join(genre.capitalize() for genre in self.release.genres)
            else:
                genre_list = ', '.join(genre['name'].capitalize() for genre in self.release.genres)
            self.genre_label.setText('Genres: ' + genre_list)
        else:
            self.genre_label.hide()

        if self.release.tracks:
            self.track_list_widget.show()
            self.track_list_widget.clear()
            for track in self.release.tracks:
                num = track['number']
                title = track['title']

                total_length_ms = track['length']
                total_length_s = total_length_ms / 1000
                minutes = int(total_length_s // 60)
                seconds = round(total_length_s % 60)

                self.track_list_widget.addItem(f"{num} {title} ({minutes}:{seconds:02})")
        else:
            self.track_list_widget.hide()

    def run_add_dialog(self):
        if self.add_dialog.exec():
            self.release.insert(self.format_dropdown.currentText())
            self.add_button.hide()
            self.main_window.collection_page.fill_table()

    def check_format(self):
        format = self.format_dropdown.currentText()
        if Release.exists_format(self.release.mbid, format):
            ret = QMessageBox.warning(
                self.add_dialog,
                'Duplicate format',
                (
                    f"You already have {self.release.title} in the "
                    f"{format} format in your collection"
                    "\nWould you like to add another one?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if ret == QMessageBox.StandardButton.No:
                return

        self.add_dialog.accept()

    def populate_from_database(self, release):
        self.add_button.hide()
        self.release = release
        release.fill_tracks()
        self.fill_widget()

    # def switchFormat(self, index):
    #     colEntryID = self.formatOptionMapping[index]
    #     self.tracks.clear()
    #     if self.db.open():
    #         try:
    #             query = QSqlQuery()
    #             query.prepare(
    #                 """SELECT number, title, length
    #                 FROM track
    #                 WHERE collection_entry_id = :id"""
    #             )
    #             query.bindValue(':id', colEntryID)
    #             if not query.exec():
    #                 raise Exception(
    #                     'Track fetch failed: : ' + query.lastError().text()
    #                 )
    #             self.trackListWidget.show()
    #             while query.next():
    #                 self.tracks.append(
    #                     {
    #                         'number': query.value('number'),
    #                         'title': query.value('title'),
    #                         'length': query.value('length')
    #                     }
    #                 )
    #         except Exception as e:
    #             print('Error:', e)
    #             self.trackListWidget.hide()
    #     else:
    #         print("Failed to open database: ", self.db.lastError().text())
    #         self.trackListWidget.hide()
