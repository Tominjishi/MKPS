from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        layout = QVBoxLayout(self)\

        search_artists_button = QPushButton('Search Artists', self)
        search_artists_button.clicked.connect(self.navigate_to_search_artists_page)
        layout.addWidget(search_artists_button)

        search_release_groups_button = QPushButton('Search Releases', self)
        search_release_groups_button.clicked.connect(self.navigate_to_search_release_groups_page)
        layout.addWidget(search_release_groups_button)

        collection_button = QPushButton('My Collection', self)
        collection_button.clicked.connect(self.navigate_to_collection_page)
        layout.addWidget(collection_button)


    def navigate_to_search_artists_page(self):
        self.main_window.navigate_to_page(self.main_window.search_artists_page)

    def navigate_to_search_release_groups_page(self):
        self.main_window.navigate_to_page(self.main_window.search_release_groups_page)

    def navigate_to_collection_page(self):
        self.main_window.navigate_to_page(self.main_window.collection_page)
