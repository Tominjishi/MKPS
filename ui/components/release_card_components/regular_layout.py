# ui components
from ui.components.selectable_label import SelectableLabel
# qt
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget


class RegularLayout(QWidget):
    def __init__(self, page=None):
        super().__init__(page)
        self.page = page
        layout = QVBoxLayout(self)

        self.artist_title_label = SelectableLabel(self.page)
        self.artist_title_label.setStyleSheet('font-size: 20px; font-weight: bold;')
        self.artist_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.type_label = SelectableLabel(self.page)
        self.type_label.setStyleSheet('font-size: 15px;')
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.release_date_label = SelectableLabel(self.page)
        self.release_date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.genre_label = SelectableLabel(self.page)
        self.genre_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.track_list_widget = QListWidget(self.page)
        # self.trackListWidget.setMaximumHeight(300)

        layout.addWidget(self.artist_title_label)
        layout.addWidget(self.type_label)
        layout.addWidget(self.release_date_label)
        layout.addWidget(self.genre_label)
        layout.addWidget(self.track_list_widget)
        layout.addStretch()

    def fill(self, release):
        if release.cover:
            pixmap = QPixmap()
            pixmap.loadFromData(release.cover)
            self.page.img_label.setPixmap(pixmap)
            self.page.img_label.show()
        else:
            self.page.img_label.hide()

        page_title = (
                release.artist_credit_phrase
                + ' - '
                + release.title
        )
        self.artist_title_label.setText(page_title)

        self.type_label.setText(release.type)
        self.release_date_label.setText(release.release_date)

        # if len(release.genres) == 1:
        #     genre_list = release.genre
        genre_list = ', '.join(genre['name'].capitalize() for genre in release.genres)
        self.genre_label.setText('Genres: ' + genre_list)

        if release.tracks:
            self.track_list_widget.show()
            self.track_list_widget.clear()
            for track in release.tracks:
                pos = track['position']
                title = track['title']

                total_length_ms = track['length']
                total_length_s = total_length_ms / 1000
                minutes = int(total_length_s // 60)
                seconds = round(total_length_s % 60)

                self.track_list_widget.addItem(f'{pos} {title} ({minutes}:{seconds:02})')
        else:
            self.track_list_widget.hide()