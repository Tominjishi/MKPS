# ui components
from ui.components.filtering.collection_filter_layout import FilterLayout
from ui.components.simple_insert_dialog import SimpleInsertDialog
# db queries
from data.queries import get_five_solo_artist_release_titles, delete_artist, get_artists, insert_artist, exists_artist
# qt
from PySide6.QtWidgets import QMessageBox, QDialog


# Artist filter area layout
class ArtistFilterLayout(FilterLayout):
    def __init__(self, artists, col_page):
        super().__init__('Artists', artists)
        self.collection_page = col_page

    def delete(self, name, db_id):
        # Check if deleting artist will cause releases with no artist
        has_orphans = False
        orphaned_releases = get_five_solo_artist_release_titles(db_id)
        if orphaned_releases:
            message_text = (
                f'There are records in your collection without other associated artists. '
                f'If you do not add another artist to them, they will be deleted.\n\nDelete {name} anyway?\n\n'
                f'Deleted releases:'
            )
            for i, title in enumerate(orphaned_releases):
                if i == 4:
                    message_text += '\n...'
                    break
                message_text += '\n' + title
            has_orphans = True
        else:
            message_text = f'Are you sure you want to delete {name}?'

        # Message box to confirm deletion of artist (and releases if relevant)
        delete_confirmation = QMessageBox(self.collection_page)
        delete_confirmation.setIcon(QMessageBox.Icon.Warning)
        delete_confirmation.setWindowTitle('Delete artist')
        delete_confirmation.setModal(True)
        delete_confirmation.setText(message_text)
        delete_confirmation.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if delete_confirmation.exec() == QMessageBox.StandardButton.Ok:
            delete_artist(db_id)
            # Clear and re-fill artist filters
            self.clear()
            self.fill(get_artists())
            # Re-fill collection table due to deleted releases
            if has_orphans:
                self.collection_page.fill_table()

    def insert(self):
        # Dialog for manual artist insertion
        self.insert_dialog = SimpleInsertDialog(self.collection_page, 'Insert Artist', True)
        self.insert_dialog.buttons.accepted.connect(self.validate_and_insert)
        if self.insert_dialog.exec() == QDialog.DialogCode.Accepted:
            return self.insert_dialog.inserted_id
        return False

    # Validate user input for new artist
    def validate_and_insert(self):
        error = ''
        name = self.insert_dialog.name_input.text()
        artist_type = self.insert_dialog.type_dropdown.currentText()

        if not name.strip():
            error += 'Name is required.\n'
        if not artist_type:
            error += 'The artist type must be specified.'
        if error:
            QMessageBox.information(self.widget(), 'Insert error', error)
            return

        # Warn of duplicate artist
        if exists_artist(name, artist_type):
            duplicate_confirmation = QMessageBox(self.collection_page)
            duplicate_confirmation.setIcon(QMessageBox.Icon.Warning)
            duplicate_confirmation.setWindowTitle('Duplicate artist')
            duplicate_confirmation.setModal(True)
            duplicate_confirmation.setText('There already is an artist with that name in your collection.\n\n Add Anyway?')
            duplicate_confirmation.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if duplicate_confirmation.exec() != QMessageBox.StandardButton.Ok:
                return

        self.insert_dialog.inserted_id = insert_artist(name, artist_type)

        # Clear and re-fill artist filters
        self.clear()
        self.fill(get_artists())
        self.insert_dialog.accept()