# ui components
from ui.components.release_card_components.edit_artist_genre_row import EditArtistGenreRow
# db queries
from data.queries import get_artists
# qt
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QHBoxLayout, QPushButton


# Dialog for adding an artist to a release
class AddArtistDialog(QDialog):
    def __init__(self, edit_layout):
        super().__init__(edit_layout)
        self.edit_layout = edit_layout
        self.setWindowTitle('Add artist')
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.artist_choice = QComboBox()
        self.artist_choice.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for artist in get_artists():
            if artist['id'] not in self.edit_layout.artist_ids:
                self.artist_choice.addItem(artist['name'], artist['id'])
        new_artist_button = QPushButton()
        new_artist_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        new_artist_button.clicked.connect(self.new_artist)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        artist_layout = QHBoxLayout()
        artist_layout.addWidget(self.artist_choice)
        artist_layout.addWidget(new_artist_button)

        layout.addLayout(artist_layout)
        layout.addWidget(buttons)

        if self.exec() == QDialog.DialogCode.Accepted:
            artist = {'id': self.artist_choice.currentData(), 'name': self.artist_choice.currentText()}
            self.edit_layout.artist_ids.add(artist['id'])
            # If artist was already there before editing but was deleted, remove from deleted artists
            # Otherwise (new) add to added artists
            if artist['id'] in self.edit_layout.edited_data.get('deleted_artist_ids', []):
                self.edit_layout.edited_data['deleted_artist_ids'].remove(artist['id'])
            else:
                self.edit_layout.edited_data['added_artist_ids'].add(artist['id'])
            # Add artist row
            artist_row = EditArtistGenreRow(artist)
            artist_row.remove_button.clicked.connect(
                lambda checked, a_id=artist['id'], row_widget=artist_row: self.edit_layout.remove_artist(a_id, row_widget)
            )
            self.edit_layout.artist_list_layout.addWidget(artist_row)
            self.edit_layout.release.artists.append(artist)

    # Create a new artist
    def new_artist(self):
        new_id = self.edit_layout.page.main_window.collection_page.filter_boxes['artists'].insert()
        if new_id:
            self.artist_choice.clear()
            for artist in get_artists():
                if artist['id'] not in self.edit_layout.artist_ids:
                    self.artist_choice.addItem(artist['name'], artist['id'])
                    if artist['id'] == new_id:
                        self.artist_choice.setCurrentIndex(self.artist_choice.count() - 1)
