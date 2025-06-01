from collections import defaultdict
from copy import deepcopy
# ui components
from ui.components.release_card_components.add_artist_dialog import AddArtistDialog
from ui.components.release_card_components.add_genre_dialog import AddGenreDialog
from ui.components.release_card_components.int_delegate import IntDelegate
from ui.components.release_card_components.edit_artist_genre_row import EditArtistGenreRow
# db queries
from data.queries import get_release_types, get_formats
from data.release import Release
# qt
from PySide6.QtCore import QDate, QByteArray
from PySide6.QtGui import QPixmap, QIcon, Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QDateEdit,
    QGroupBox,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog
)


class EditLayout(QScrollArea):
    def __init__(self, page=None):
        super().__init__(page)
        self.page = page
        self.release = None
        self.edited_data = defaultdict(set)

        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)

        # Artist credit phrase
        self.artist_credit = QLineEdit()
        self.artist_credit.textEdited.connect(self.on_artist_credit_edit)
        artist_credit_layout = QHBoxLayout()
        artist_credit_layout.addWidget(QLabel('Artist credit phrase:'))
        artist_credit_layout.addWidget(self.artist_credit)
        layout.addLayout(artist_credit_layout)

        # Title
        self.title = QLineEdit()
        self.title.textEdited.connect(self.on_title_edit)
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('Title:'))
        title_layout.addWidget(self.title)
        layout.addLayout(title_layout)

        # Type
        self.type = QComboBox()
        self.type.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.type.currentIndexChanged.connect(self.on_type_edit)
        new_type_button = QPushButton()
        new_type_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        new_type_button.clicked.connect(self.new_type)
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Type:'))
        type_layout.addWidget(self.type)
        type_layout.addWidget(new_type_button)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Format
        self.format = QComboBox()
        self.format.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.format.currentIndexChanged.connect(self.on_format_edit)
        new_format_button = QPushButton()
        new_format_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        new_format_button.clicked.connect(self.new_format)
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Format:'))
        format_layout.addWidget(self.format)
        format_layout.addWidget(new_format_button)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # Release date
        self.release_date = QDateEdit()
        self.release_date.userDateChanged.connect(self.on_date_change)
        self.release_date.setCalendarPopup(True)
        release_date_layout = QHBoxLayout()
        release_date_layout.addWidget(QLabel('Release date:'))
        release_date_layout.addWidget(self.release_date)
        release_date_layout.addStretch()
        layout.addLayout(release_date_layout)

        # Artists
        self.artist_ids = set()  # keep track of release related artist ids
        artist_list = QGroupBox('Artists:')
        self.artist_list_layout = QVBoxLayout(artist_list)
        self.artist_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        add_artist_button = QPushButton('Add artist')
        add_artist_button.clicked.connect(lambda checked, edit_layout = self: AddArtistDialog(edit_layout))
        self.artist_list_layout.addWidget(add_artist_button)
        layout.addWidget(artist_list)

        # Genres
        self.genre_ids = set()  # keep track of release related genre ids
        genre_box = QGroupBox('Genres:')
        genre_box_layout = QVBoxLayout(genre_box)
        add_genre_button = QPushButton('Add genre')
        add_genre_button.clicked.connect(lambda checked, edit_layout = self: AddGenreDialog(edit_layout))
        genre_box_layout.addWidget(add_genre_button)
        # Scroll area for genre list
        genre_scroll_area = QScrollArea()
        genre_scroll_area.setFixedHeight(150)
        genre_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        genre_scroll_area.setWidgetResizable(True)
        genre_scroll_widget = QWidget()
        genre_scroll_area.setWidget(genre_scroll_widget)
        self.genre_scroll_layout = QVBoxLayout(genre_scroll_widget)
        self.genre_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        genre_box_layout.addWidget(genre_scroll_area)
        layout.addWidget(genre_box)

        # Tracks
        self.track_list = QTableWidget()
        self.track_list.setMaximumWidth(720)
        self.track_list.setSizeAdjustPolicy(QScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.track_list.setColumnCount(6)
        self.track_list.setHorizontalHeaderLabels(['Position', 'Title', 'Min', 'Sec', ''])
        self.track_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.track_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # Hidden column to hold track_id
        self.track_list.setColumnHidden(5, True)
        # Allow only integers in minutes and seconds columns:
        min_delegate = IntDelegate(0, 999, self)
        self.track_list.setItemDelegateForColumn(2, min_delegate)
        sec_delegate = IntDelegate(0, 59, self)
        self.track_list.setItemDelegateForColumn(3, sec_delegate)
        # Connection to keep track whether tracks were edited
        self.track_list.cellChanged.connect(self.on_track_edit)

        # Button to add track over and under the track table
        track_add_button = QPushButton('Add track')
        track_add_button.clicked.connect(self.append_track_row)
        track_add_button_under = QPushButton('Add track')
        track_add_button_under.clicked.connect(self.append_track_row)

        # add track related widgets to layout
        layout.addWidget(QLabel('Tracks:'))
        layout.addWidget(track_add_button)
        layout.addWidget(self.track_list)
        layout.addWidget(track_add_button_under)

        layout.addStretch()

    def fill(self, release = None):
        self.clear()
        self.release = deepcopy(release)

        # If editing fill with existing data
        if release:
            if release.cover:
                cover_pixmap = QPixmap()
                cover_pixmap.loadFromData(release.cover)
                self.page.img_label.setPixmap(cover_pixmap)
                self.page.img_label.show()
                self.page.remove_image_button.show()
            else:
                self.page.remove_image_button.hide()
            self.title.setText(release.title)
            self.artist_credit.setText(release.artist_credit_phrase)

            self.type.blockSignals(True)
            for rel_type in get_release_types():
                self.type.addItem(rel_type['name'], rel_type['id'])
                if release.type_id == rel_type['id']:
                    self.type.setCurrentIndex(self.type.count() - 1)
            self.type.blockSignals(False)

            self.format.blockSignals(True)
            for rel_format in get_formats():
                self.format.addItem(rel_format['name'], rel_format['id'])
                if release.format_id == rel_format['id']:
                    self.format.setCurrentIndex(self.format.count() - 1)
            self.format.blockSignals(False)

            # Release date format: YYYY-MM-DD
            if release.release_date:
                date = {'year': int(release.release_date[:4])}
                if len(release.release_date) > 4:
                    date['month'] = int(release.release_date[5:7])
                    date['day'] = int(release.release_date[8:10])
                self.release_date.blockSignals(True)
                self.release_date.setDate(QDate(date['year'], date.get('month', 1), date.get('day', 1)))
                self.release_date.blockSignals(False)

            # Artists
            for artist in release.artists:
                self.artist_ids.add(artist['id'])
                artist_row = EditArtistGenreRow(artist)
                artist_row.remove_button.clicked.connect(
                    lambda checked, a_id=artist['id'], row_widget=artist_row: self.remove_artist(a_id, row_widget)
                )
                self.artist_list_layout.addWidget(artist_row)

            for genre in release.genres:
                if genre.get('id', None):
                    self.genre_ids.add(genre['id'])
                    genre_row = EditArtistGenreRow(genre)
                    genre_row.remove_button.clicked.connect(
                        lambda checked, g_id=genre['id'], row_widget=genre_row: self.remove_genre(g_id, row_widget))
                    self.genre_scroll_layout.addWidget(genre_row)

            if release.tracks:
                self.track_list.setRowCount(len(release.tracks))
                self.track_list.blockSignals(True)  # block signals to not call on_track_edit
                for row, track in enumerate(release.tracks):
                    pos = track['position']
                    title = track['title']
                    total_length_ms = track['length']
                    total_length_s = total_length_ms / 1000
                    minutes = int(total_length_s // 60)
                    seconds = round(total_length_s % 60)

                    self.track_list.setItem(row, 0, QTableWidgetItem(str(pos)))
                    self.track_list.setItem(row, 1, QTableWidgetItem(title))
                    minutes_item = QTableWidgetItem()
                    minutes_item.setData(Qt.ItemDataRole.EditRole, minutes)
                    self.track_list.setItem(row, 2, minutes_item)
                    seconds_item = QTableWidgetItem()
                    seconds_item.setData(Qt.ItemDataRole.EditRole, seconds)
                    self.track_list.setItem(row, 3, seconds_item)
                    remove_button = QPushButton()
                    remove_button.setIcon(QIcon.fromTheme('edit-delete'))
                    remove_button.setToolTip('Remove track')
                    remove_button.clicked.connect(self.remove_track)
                    self.track_list.setCellWidget(row, 4, remove_button)
                    self.track_list.setItem(row, 5, QTableWidgetItem(str(track['id'])))
                self.track_list.blockSignals(False)  # stop blocking signals
                self.adjust_track_table_height()
        # If creating new only add type and format options
        else:
            self.page.remove_image_button.hide()
            self.type.blockSignals(True)
            for rel_type in get_release_types():
                self.type.addItem(rel_type['name'], rel_type['id'])
            self.type.blockSignals(False)

            self.format.blockSignals(True)
            for rel_format in get_formats():
                self.format.addItem(rel_format['name'], rel_format['id'])
            self.format.blockSignals(False)

            # Create empty release object
            self.release = Release(
                release_type=self.type.currentText(),
                type_id=self.type.currentData(),
                release_format=self.format.currentText(),
                format_id=self.format.currentData(),
                title='',
                artist_credit_phrase='',
                artists=[],
            )

    def clear(self):
        self.edited_data.clear()
        self.release = None

        self.title.setText('')
        self.artist_credit.setText('')
        self.type.blockSignals(True)
        self.type.clear()
        self.type.blockSignals(False)
        self.format.blockSignals(True)
        self.format.clear()
        self.format.blockSignals(False)
        self.release_date.blockSignals(True)
        self.release_date.setDate(QDateEdit().date())  # Sets to default date (01.01.2000)
        self.release_date.blockSignals(False)

        self.artist_ids.clear()
        # Clear artist list layout except first child (add button)
        while self.artist_list_layout.count() > 1:
            item = self.artist_list_layout.takeAt(1)
            item.widget().deleteLater()

        self.genre_ids.clear()
        # Clear genre list layout
        while self.genre_scroll_layout.count():
            item = self.genre_scroll_layout.takeAt(0)
            item.widget().deleteLater()

        # Clear table and leave 1 empty row
        self.track_list.setRowCount(0)
        self.track_list.blockSignals(True)
        # Insert empty row
        self.append_track_row()
        self.track_list.blockSignals(False)
        self.adjust_track_table_height()

        self.page.img_label.hide()

    # Make track table height perfectly fit all rows
    def adjust_track_table_height(self):
        total_height = self.track_list.horizontalHeader().height()
        for row in range(self.track_list.rowCount()):
            total_height += self.track_list.rowHeight(row)
        total_height += 2 * self.track_list.frameWidth()
        self.track_list.setFixedHeight(total_height)

    # Add empty row to bottom of track table with appropriate position number and remove button
    def append_track_row(self):
        row = self.track_list.rowCount()
        self.track_list.insertRow(row)
        self.track_list.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        # Add empty items to not break validation
        self.track_list.setItem(row, 1, QTableWidgetItem())
        self.track_list.setItem(row, 2, QTableWidgetItem())
        self.track_list.setItem(row, 3, QTableWidgetItem())
        self.track_list.setItem(row, 5, QTableWidgetItem())
        # Add remove button
        remove_button = QPushButton()
        remove_button.setIcon(QIcon.fromTheme('edit-delete'))
        remove_button.setToolTip('Remove track')
        remove_button.clicked.connect(self.remove_track)
        self.track_list.setCellWidget(row, 4, remove_button)
        self.adjust_track_table_height()

    def on_artist_credit_edit(self):
        self.edited_data['artist_credit_phrase'] = self.artist_credit.text()
        self.release.artist_credit_phrase = self.artist_credit.text()

    def on_title_edit(self):
        self.edited_data['title'] = self.title.text()
        self.release.title = self.title.text()

    def on_type_edit(self):
        self.edited_data['type_id'] = self.type.currentData()
        self.release.type_id = self.type.currentData()
        self.release.type = self.type.currentText()

    def on_format_edit(self):
        self.edited_data['format_id'] = self.format.currentData()
        self.release.format_id = self.format.currentData()
        self.release.format = self.format.currentText()

    def on_date_change(self, date):
        date_string = date.toString('yyyy-MM-dd')
        self.edited_data['release_date'] = date_string
        self.release.release_date = date_string

    def on_track_edit(self):
        self.edited_data['tracks_edited'] = True

    def remove_artist(self, artist_id, row_widget):
        self.artist_ids.remove(artist_id)
        # If artist was added during editing, remove from added artists. Otherwise, add to deleted artists
        if artist_id in self.edited_data.get('added_artist_ids', []):
            self.edited_data['added_artist_ids'].remove(artist_id)
        else:
            self.edited_data['deleted_artist_ids'].add(artist_id)
        row_widget.deleteLater()

        for artist in self.release.artists:
            if artist['id'] == artist_id:
                self.release.artists.remove(artist)
                break

    def remove_genre(self, genre_id, row_widget):
        self.genre_ids.remove(genre_id)
        # If genre was added during editing, remove from added genres. Otherwise add to deleted genres
        if genre_id in self.edited_data.get('added_genre_ids', []):
            self.edited_data['added_genre_ids'].remove(genre_id)
        else:
            self.edited_data['deleted_genre_ids'].add(genre_id)
        row_widget.deleteLater()

        for genre in self.release.genres:
            if genre.get('id') == genre_id:
                self.release.genres.remove(genre)
                break

    def remove_track(self):
        button = self.sender()
        rowcount = self.track_list.rowCount()
        # Find row where clicked button is to get deleted track_id and row to remove
        for row in range(rowcount):
            if self.track_list.cellWidget(row, 4) == button:
                track_id_item = self.track_list.item(row, 5)
                if track_id_item:
                    self.edited_data['deleted_track_ids'].add(track_id_item.text())
                self.track_list.removeRow(row)
                break
        self.on_track_edit()
        self.track_list.setRowCount(rowcount - 1)
        self.adjust_track_table_height()

    def validate_and_update(self):
        # Validate existence of mandatory values
        error_msg = ''
        if self.artist_list_layout.count() == 1:  # If layout has only add artist button
            error_msg += 'At least one artist must be added\n'
        if self.artist_credit.text().strip() == '':
            error_msg += 'Artist credit phrase is required\n'
        if self.title.text().strip() == '':
            error_msg += 'Title is required\n'

        # Construct new tracklist if tracks were edited
        tracks = []
        if self.edited_data.get('tracks_edited'):
            for row in range(self.track_list.rowCount()):
                # Get track data
                position = self.track_list.item(row, 0).text().strip()
                title = self.track_list.item(row, 1).text().strip()
                # Add up minutes and seconds
                length = 0
                min_text = self.track_list.item(row, 2).text()
                if min_text:
                    length += int(min_text) * 60
                sec_text = self.track_list.item(row, 3).text()
                if sec_text:
                    length += int(sec_text)

                track_id_text = self.track_list.item(row, 5).text()
                if track_id_text:
                    track_id = int(track_id_text)
                else:
                    track_id = None

                # Return error if some data unfilled
                if not position or not title or not length:
                    error_msg += f'Track no. {row + 1} data is unfilled\n'
                else:
                    track = {
                        'position': position,
                        'title': title,
                        'length': length * 1000,
                        'id': track_id
                    }
                    tracks.append(track)
        if error_msg:
            QMessageBox.information(self, 'Save error', error_msg)
            return

        if self.release.id:
            self.release.update(self.edited_data, tracks)
        else:
            self.release.insert_manual(self.edited_data, tracks)
        self.page.release = self.release
        self.page.regular_layout.fill(self.page.release)
        self.page.switch_edit_mode()

        self.page.main_window.collection_page.fill_table()

    def new_format(self):
        new_id = self.page.main_window.collection_page.filter_boxes['format'].insert()
        if new_id:
            self.format.clear()
            for rel_format in get_formats():
                self.format.addItem(rel_format['name'], rel_format['id'])
                if new_id == rel_format['id']:
                    self.format.setCurrentIndex(self.format.count() - 1)

    def new_type(self):
        new_id = self.page.main_window.collection_page.filter_boxes['type'].insert()
        if new_id:
            self.type.clear()
            for rel_type in get_release_types():
                self.type.addItem(rel_type['name'], rel_type['id'])
                if new_id == rel_type['id']:
                    self.type.setCurrentIndex(self.type.count() - 1)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Image',
            '',
            'Images (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        # get binary file and set to pixmap
        if file_path:
            with open(file_path, 'rb') as f:
                img_data = QByteArray(f.read())
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                self.page.img_label.setPixmap(pixmap)
                self.page.img_label.show()
            self.edited_data['cover'] = img_data
            self.release.cover = img_data

    def remove_image(self):
        self.edited_data['cover'] = ''
        self.release.cover = ''
        self.page.img_label.setPixmap(QPixmap())