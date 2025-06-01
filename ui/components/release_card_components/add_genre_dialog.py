# ui components
from ui.components.release_card_components.edit_artist_genre_row import EditArtistGenreRow
# db queries
from data.queries import get_genres
# qt
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QHBoxLayout, QPushButton



class AddGenreDialog(QDialog):
    def __init__(self, edit_layout):
        super().__init__(edit_layout)
        self.edit_layout = edit_layout
        self.setWindowTitle('Add genre')
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.genre_choice = QComboBox()
        self.genre_choice.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for genre in get_genres():
            if genre['id'] not in self.edit_layout.genre_ids:
                self.genre_choice.addItem(genre['name'], genre['id'])
        new_genre_button = QPushButton()
        new_genre_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        new_genre_button.clicked.connect(self.new_genre)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        genre_layout = QHBoxLayout()
        genre_layout.addWidget(self.genre_choice)
        genre_layout.addWidget(new_genre_button)

        layout.addLayout(genre_layout)
        layout.addWidget(buttons)

        if self.exec() == self.DialogCode.Accepted:
            genre = {'id': self.genre_choice.currentData(), 'name': self.genre_choice.currentText()}
            self.edit_layout.genre_ids.add(genre['id'])
            # If genre was already there before editing but was deleted, remove from deleted genres
            # Otherwise (new) add to added genres
            if genre['id'] in self.edit_layout.edited_data.get('deleted_genre_ids', []):
                self.edit_layout.edited_data['deleted_genre_ids'].remove(genre['id'])
            else:
                self.edit_layout.edited_data['added_genre_ids'].add(genre['id'])
            # Add genre row
            genre_row = EditArtistGenreRow(genre)
            genre_row.remove_button.clicked.connect(
                lambda checked, g_id=genre['id'], row_widget=genre_row: self.edit_layout.remove_genre(g_id, row_widget)
            )
            self.edit_layout.genre_scroll_layout.addWidget(genre_row)
            self.edit_layout.release.genres.append(genre)

    def new_genre(self):
        new_id = self.edit_layout.page.main_window.collection_page.filter_boxes['genres'].insert()
        if new_id:
            self.genre_choice.clear()
            for genre in get_genres():
                if genre['id'] not in self.edit_layout.genre_ids:
                    self.genre_choice.addItem(genre['name'], genre['id'])
                    if genre['id'] == new_id:
                        self.genre_choice.setCurrentIndex(self.genre_choice.count() - 1)
