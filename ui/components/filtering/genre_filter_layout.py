# ui components
from ui.components.filtering.collection_filter_layout import FilterLayout
from ui.components.simple_insert_dialog import SimpleInsertDialog
# db queries
from data.queries import delete_genre, get_genres, exists_genre, insert_genre
# qt
from PySide6.QtWidgets import QMessageBox, QDialog


# Genre filter area layout
class GenreFilterLayout(FilterLayout):
    def __init__(self, genres, col_page):
        super().__init__('Genres', genres)
        self.collection_page = col_page
        self.insert_dialog = SimpleInsertDialog(self.collection_page, 'Insert Genre')
        self.insert_dialog.buttons.accepted.connect(self.validate_and_insert)

    def delete(self, name, db_id):
        # Message box to confirm genre deletion
        delete_confirmation = QMessageBox(self.collection_page)
        delete_confirmation.setIcon(QMessageBox.Icon.Warning)
        delete_confirmation.setWindowTitle('Delete genre')
        delete_confirmation.setModal(True)
        delete_confirmation.setText(f'Are you sure you want to delete {name}?')
        delete_confirmation.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if delete_confirmation.exec() == QMessageBox.StandardButton.Ok:
            delete_genre(db_id)
            # Clear and re-fill artist filters
            self.clear()
            self.fill(get_genres())

    def insert(self):
        # Dialog for manual genre insertion
        self.insert_dialog.clear()
        if self.insert_dialog.exec() == QDialog.DialogCode.Accepted:
            return self.insert_dialog.inserted_id
        return None

    # Validate user input for new artist
    def validate_and_insert(self):
        name = self.insert_dialog.name_input.text()
        if not name.strip():
            QMessageBox.information(self.widget(), 'Insert error', 'Genre name is required.')
            return

        # Check for duplicate genre
        if exists_genre(name):
            QMessageBox.information(
                self.widget(), 'Duplicate genre', 'There already is a genre with that name in your collection'
            )
            return

        self.insert_dialog.inserted_id = insert_genre(name)

        # Clear and re-fill genre filters
        self.clear()
        self.fill(get_genres())
        self.insert_dialog.accept()
