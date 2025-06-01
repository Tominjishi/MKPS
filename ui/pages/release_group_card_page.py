from concurrent.futures import ThreadPoolExecutor
# api services
import services.musicbrainz_api as mb
from services.cover_art_archive import get_release_group_front_cover_data
# ui components
from ui.components.release_card_components.regular_layout import RegularLayout
from ui.components.release_card_components.edit_layout import EditLayout
# db queries
from data.queries import get_release_types, get_formats, get_artists, get_genres
from data.release import Release
# qt
from PySide6.QtCore import QByteArray, QSize
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QDialog,
    QMessageBox,
    QDialogButtonBox,
    QStackedLayout,
)


class ReleaseGroupCardPage(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.release = None  # instance of Release class
        self.edit_mode = False
        self.regular_layout = RegularLayout(self)
        self.edit_layout = EditLayout(self)

        main_layout = QHBoxLayout(self)

        # Layout for left side (img and button/combobox under)
        left_layout = QVBoxLayout()

        self.img_label = QLabel(self)
        # self.img_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(QSize(250, 250))
        self.img_label.setScaledContents(True)

        self.remove_image_button = QPushButton('Remove image')
        self.remove_image_button.clicked.connect(self.edit_layout.remove_image)
        self.remove_image_button.hide()

        self.upload_image_button = QPushButton('Upload image')
        self.upload_image_button.clicked.connect(self.edit_layout.upload_image)
        self.upload_image_button.hide()

        self.add_button = QPushButton('Add to collection', self)
        self.add_button.clicked.connect(self.run_add_dialog)
        self.add_button.setFixedWidth(250)

        self.edit_button = QPushButton('Edit', self)
        self.edit_button.clicked.connect(self.switch_edit_mode)
        self.edit_button.setFixedWidth(250)

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.edit_layout.validate_and_update)
        self.save_button.setFixedWidth(250)
        self.save_button.hide()

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.switch_edit_mode)
        self.cancel_button.hide()

        self.delete_button = QPushButton('Delete', self)
        self.delete_button.clicked.connect(self.run_delete_dialog)

        left_layout.addWidget(self.img_label)
        left_layout.addWidget(self.remove_image_button)
        left_layout.addWidget(self.upload_image_button)
        left_layout.addWidget(self.add_button)
        left_layout.addWidget(self.edit_button)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.cancel_button)
        left_layout.addWidget(self.delete_button)
        left_layout.addStretch()
        # Hide add button by default

        # Right side
        self.right_layout = QStackedLayout()
        self.right_layout.addWidget(self.regular_layout)
        self.right_layout.addWidget(self.edit_layout)
        self.right_layout.setCurrentIndex(0)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(self.right_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Dialog for saving release in collection
        self.add_dialog = AddDialog(self)
        self.delete_dialog = DeleteDialog(self)

    # Construct Release object from mb API and cover art archive
    def populate_from_api(self, release_group_mbid):
        release_group, cover_art, formats_and_tracks = fetch_release_group_data(release_group_mbid)
        if isinstance(release_group, dict):
            self.right_layout.setCurrentIndex(0)
            self.switch_online_mode(True)

            # Construct artist credit phrase and list of artists
            artist_credit_phrase = ''
            artists = []
            for artist in release_group.get('artist-credit', []):
                name = artist.get('name')
                joinphrase = artist.get('joinphrase')
                artist_credit_phrase += name + joinphrase
                artists.append(artist.get('artist'))

            # Get album cover
            if isinstance(cover_art, bytes):
                cover = QByteArray(cover_art)
            else:
                cover = None

            # Get and sort genres
            genres = release_group.get('genres')
            if genres:
                genres = sorted(genres, key=lambda a: a['count'], reverse=True)

            # Get tracks and formats
            formats, tracks = formats_and_tracks

            # Add possible formats to dropdown when running add dialog
            self.add_dialog.format_dropdown.clear()
            self.add_dialog.format_dropdown.addItems(formats)

            self.release = Release(
                mbid=release_group.get('id'),
                release_type=release_group.get('primary-type'),
                title=release_group.get('title'),
                artist_credit_phrase=artist_credit_phrase,
                artists=artists,
                tracks=tracks,
                genres=genres,
                cover=cover,
                release_date=release_group.get('first-release-date')
            )
            self.regular_layout.fill(self.release)
            return True, None

        else:
            return False, release_group

    def run_add_dialog(self):
        if self.add_dialog.exec():
            type_inserted, format_inserted, artist_inserted, genre_inserted = self.release.insert_from_mb(
                self.add_dialog.format_dropdown.currentText()
            )
            # Reload collection table and filter boxes if needed
            self.main_window.collection_page.fill_table()
            if type_inserted:
                self.main_window.collection_page.filter_boxes['type'].clear()
                self.main_window.collection_page.filter_boxes['type'].fill(get_release_types())
            if format_inserted:
                self.main_window.collection_page.filter_boxes['format'].clear()
                self.main_window.collection_page.filter_boxes['format'].fill(get_formats())
            if artist_inserted:
                self.main_window.collection_page.filter_boxes['artists'].clear()
                self.main_window.collection_page.filter_boxes['artists'].fill(get_artists())
            if genre_inserted:
                self.main_window.collection_page.filter_boxes['genres'].clear()
                self.main_window.collection_page.filter_boxes['genres'].fill(get_genres())
            # Hide online buttons and show database buttons
            self.switch_online_mode(False)
            # Make sure edit mode is off
            if self.edit_mode:
                self.switch_edit_mode()

    def run_delete_dialog(self):
        if self.delete_dialog.exec():
            self.release.delete()
            self.main_window.collection_page.fill_table()
            self.main_window.navigate_to_page(self.main_window.collection_page)

    def check_format(self):
        release_format = self.add_dialog.format_dropdown.currentText()
        if Release.exists_in_format(self.release.title, release_format):
            ret = QMessageBox.warning(
                self.add_dialog,
                'Duplicate format',
                (
                    f'You already have {self.release.title} in the '
                    f'{release_format} format in your collection'
                    '\nWould you like to add another one?'
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if ret == QMessageBox.StandardButton.No:
                return

        self.add_dialog.accept()

    def populate_from_database(self, release):
        if self.edit_mode:
            self.switch_edit_mode()
        self.right_layout.setCurrentIndex(0)
        self.switch_online_mode(False)

        self.release = release
        self.release.fill_tracks()
        self.regular_layout.fill(self.release)

    def switch_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.edit_button.setVisible(not self.edit_mode)
        self.remove_image_button.setVisible(self.edit_mode)
        self.upload_image_button.setVisible(self.edit_mode)
        self.save_button.setVisible(self.edit_mode)
        self.cancel_button.setVisible(self.edit_mode)
        self.right_layout.setCurrentIndex(self.edit_mode)
        if self.edit_mode:
            self.edit_layout.fill(self.release)
        else:
            self.regular_layout.fill(self.release)

    # Show appropriate buttons whether release from online or in db
    def switch_online_mode(self, is_online):
        self.add_button.setVisible(is_online)
        self.edit_button.setVisible(not is_online)
        self.delete_button.setVisible(not is_online)
        self.upload_image_button.setVisible(not is_online and self.edit_mode)
        self.save_button.setVisible(not is_online and self.edit_mode)


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add to collection')
        self.setModal(True)
        self.page = parent

        layout = QVBoxLayout(self)

        # Format Choice
        format_label = QLabel('Choose a format')
        self.format_dropdown = QComboBox(self)

        # Tracklist information
        change_info = QLabel('You may edit the entry later')

        # Buttons
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons, self)
        button_box.accepted.connect(self.page.check_format)
        button_box.rejected.connect(self.reject)

        layout.addWidget(format_label)
        layout.addWidget(self.format_dropdown)
        layout.addWidget(change_info)
        layout.addWidget(button_box)


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Delete')
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Buttons
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_box = QDialogButtonBox(buttons, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(QLabel('Are you sure you want to delete this release?'))
        layout.addWidget(QLabel('This action cannot be undone!'))
        layout.addWidget(button_box)


def fetch_release_group_data(mbid):
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_release_group = executor.submit(mb.lookup_release_group_dict, mbid, 'genres artists')
        future_cover_data = executor.submit(get_release_group_front_cover_data, mbid, 's')
        future_formats_and_tracks = executor.submit(mb.get_formats_and_tracks, mbid)

        release_group = future_release_group.result()
        cover_data = future_cover_data.result()
        formats_and_tracks = future_formats_and_tracks.result()

    return release_group, cover_data, formats_and_tracks
