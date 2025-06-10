# ui components
from ui.components.filtering.collection_filter_layout import FilterLayout
from ui.components.simple_insert_dialog import SimpleInsertDialog
# db queries
from data.queries import (
    get_five_releases_of_type,
    get_types_but_one,
    delete_release_type,
    get_release_types,
    exists_release_type,
    insert_release_type,
)
# qt
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QLabel,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
)


# Release type filter area layout
class RelTypeFilterLayout(FilterLayout):
    def __init__(self, types, col_page):
        super().__init__('Types', types)
        self.collection_page = col_page
        self.insert_dialog = SimpleInsertDialog(self.collection_page, 'Insert Type')
        self.insert_dialog.buttons.accepted.connect(self.validate_and_insert)

    def delete(self, name, db_id):
        # Check if there are releases of that type
        type_releases = get_five_releases_of_type(db_id)
        if type_releases:
            # Offer user to reassign type for releases, delete releases or cancel deletion
            reassignment_message = (
                f'There are records in your collections that are of the {name} type.\n'
                f'Choose a different type to assign to these releases or delete them?\n\nReleases to be deleted:'
            )
            for i, values in enumerate(type_releases):
                if i == 4:
                    reassignment_message += '\n...'
                    break
                artists = values[0]
                title = values[1]
                reassignment_message += f'\n{artists} - {title}'

            available_types = get_types_but_one(db_id)
            self.type_dropdown = QComboBox()
            self.type_dropdown.insertItem(0, '')
            # Insert types in combobox index equal to id for easier id retrieval
            for release_type in available_types:
                self.type_dropdown.addItem(release_type['name'], release_type['id'])
            reassign_button = QPushButton('Reassign')
            reassign_button.clicked.connect(lambda checked, d=db_id: self.reassign(d))
            reassign_layout = QHBoxLayout()
            reassign_layout.addWidget(self.type_dropdown)
            reassign_layout.addWidget(reassign_button)

            self.reassignment_dialog = QDialog(self.collection_page)
            self.reassignment_dialog.setWindowTitle('Delete release type')
            self.reassignment_dialog.setModal(True)
            dialog_layout = QVBoxLayout(self.reassignment_dialog)
            dialog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            delete_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete), 'Delete')
            buttons = QDialogButtonBox()
            buttons.addButton(delete_button, QDialogButtonBox.ButtonRole.AcceptRole)
            buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(lambda d=db_id: self.delete_releases(d))
            buttons.rejected.connect(self.reassignment_dialog.reject)

            dialog_layout.addWidget(QLabel(reassignment_message))
            dialog_layout.addLayout(reassign_layout)
            dialog_layout.addWidget(buttons)

            self.reassignment_dialog.adjustSize()
            self.reassignment_dialog.exec()
            # Refresh collection table and type filters if reassigned or deleted
            if self.reassignment_dialog.result() == QDialog.DialogCode.Accepted:
                self.clear()
                self.fill(get_release_types())
                self.collection_page.fill_table()
        else:
            delete_confirmation = QMessageBox(self.collection_page)
            delete_confirmation.setIcon(QMessageBox.Icon.Warning)
            delete_confirmation.setWindowTitle('Delete release type')
            delete_confirmation.setModal(True)
            delete_confirmation.setText(f'Are you sure you want to delete the {name} type?')
            delete_confirmation.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

            if delete_confirmation.exec() == QMessageBox.StandardButton.Ok:
                delete_release_type(db_id)
                self.clear()
                self.fill(get_release_types())

    def reassign(self, db_id):
        reassign_type = self.type_dropdown.currentText()
        if not reassign_type:
            QMessageBox.information(self.widget(), 'Reassign error', 'You must choose a type if you wish to reassign')
            return
        else:
            reassign_type_id = self.type_dropdown.currentData()
            delete_release_type(db_id, reassign_type_id)
            self.reassignment_dialog.accept()

    def delete_releases(self, db_id):
        delete_confirmation = QMessageBox(
            QMessageBox.Icon.Warning,
            'Delete type and releases',
            f'Are you sure you want to delete both the release type and all associated releases?',
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            self.collection_page
        )
        if delete_confirmation.exec() == QMessageBox.StandardButton.Ok:
            delete_release_type(db_id)
            self.reassignment_dialog.accept()

            self.clear()
            self.fill(get_release_types())
            self.collection_page.fill_table()

    def insert(self):
        # Dialog for manual release type insertion
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
        if exists_release_type(name):
            QMessageBox.information(
                self.widget(),
                'Duplicate release type',
                'There already is a release type with that name in your collection'
            )
            return

        self.insert_dialog.inserted_id = insert_release_type(name)

        # Clear and re-fill genre filters
        self.clear()
        self.fill(get_release_types())
        self.insert_dialog.accept()
