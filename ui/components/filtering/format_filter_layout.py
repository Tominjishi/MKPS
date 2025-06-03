# ui components
from ui.components.filtering.collection_filter_layout import FilterLayout
from ui.components.simple_insert_dialog import SimpleInsertDialog
# db queries
from data.queries import get_five_releases_of_format, delete_format, get_formats, exists_format, insert_format
# qt
from PySide6.QtWidgets import QMessageBox, QDialog


# Format filter area layout
class FormatFilterLayout(FilterLayout):
    def __init__(self, formats, col_page):
        super().__init__('Formats', formats)
        self.collection_page = col_page
        self.insert_dialog = SimpleInsertDialog(self.collection_page, 'Insert Type')
        self.insert_dialog.buttons.accepted.connect(self.validate_and_insert)

    def delete(self, name, db_id):
        # Check if deleting format will cause releases with no format
        has_orphans = False
        orphaned_releases = get_five_releases_of_format(db_id)
        if orphaned_releases:
            has_orphans = True
            message_text = (
                f'There are records of this format in your collection.\n'
                f'If you proceed, they will be deleted. Delete {name} anyway?\n'
                f'Deleted releases:'
            )
            for i, values in enumerate(orphaned_releases):
                if i == 4:
                    message_text += '\n...'
                    break
                artists = values[0]
                title = values[1]
                message_text += f'\n{artists} - {title}'
        else:
            message_text = f'Are you sure you want to delete the {name} format?'

        # Message box to confirm deletion of format (and releases if relevant)
        delete_confirmation = QMessageBox(self.collection_page)
        delete_confirmation.setIcon(QMessageBox.Icon.Warning)
        delete_confirmation.setWindowTitle('Delete format')
        delete_confirmation.setModal(True)
        delete_confirmation.setText(message_text)
        delete_confirmation.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        if delete_confirmation.exec() == QMessageBox.StandardButton.Ok:
            delete_format(db_id)
            # Clear and re-fill format filters
            self.clear()
            self.fill(get_formats())
            # Re-fill collection table due to deleted releases
            if has_orphans:
                self.collection_page.fill_table()

    def insert(self):
        # Dialog for manual format insertion
        self.insert_dialog.clear()
        if self.insert_dialog.exec() == QDialog.DialogCode.Accepted:
            return self.insert_dialog.inserted_id
        return None

    # Validate user input for new artist
    def validate_and_insert(self):
        name = self.insert_dialog.name_input.text()
        if not name.strip():
            QMessageBox.information(self.widget(), 'Insert error', 'Name is required.')
            return

        # Check for duplicate genre
        if exists_format(name):
            QMessageBox.information(
                self.widget(), 'Duplicate release type', 'There already is a format with that name in your collection'
            )
            return

        self.insert_dialog.inserted_id = insert_format(name)

        # Clear and re-fill genre filters
        self.clear()
        self.fill(get_formats())
        self.insert_dialog.accept()