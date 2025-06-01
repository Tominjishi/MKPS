import requests
# qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox, QSizePolicy


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(50)
        self.layout.setContentsMargins(30, 30, 30, 30)

        self.search_artists_button = self.add_button(
            'Search Artists', self.navigate_to_search_artists_page
        )
        self.search_release_groups_button = self.add_button(
            'Search releases', self.navigate_to_search_release_groups_page
        )
        self.go_online_button = self.add_button(
            'Go online', self.switch_online_mode
        )
        self.add_button(
            'My collection', self.navigate_to_collection_page
        )

        self.switch_online_mode()

    def add_button(self, text, connection):
        button = QPushButton(text, self)
        button.clicked.connect(connection)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setStyleSheet('font-size: 16px; font-weight: bold; padding: 10px;')
        self.layout.addWidget(button)
        return button

    def switch_online_mode(self):
        is_online = check_online_status()
        self.search_artists_button.setVisible(is_online)
        self.search_release_groups_button.setVisible(is_online)
        self.go_online_button.setVisible(not is_online)
        if not is_online:
            error_msg = (
                "Could not establish connection with MusicBrainz!\n\n"
                "Check your internet connection and/or the status of MuiscBrainz services"
            )
            QMessageBox.information(self, 'Connection error', error_msg)

    def navigate_to_search_artists_page(self):
        self.main_window.navigate_to_page(self.main_window.search_artists_page)

    def navigate_to_search_release_groups_page(self):
        self.main_window.navigate_to_page(self.main_window.search_release_groups_page)

    def navigate_to_collection_page(self):
        self.main_window.navigate_to_page(self.main_window.collection_page)

def check_online_status(timeout = 3):
    try:
        requests.get('https://musicbrainz.org/ws/2/', timeout=3)
        return True
    except requests.RequestException:
        return False
