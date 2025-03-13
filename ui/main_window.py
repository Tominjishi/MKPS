from PySide6.QtWidgets import(
    QMainWindow,
    QStatusBar,
    QStackedWidget,
    QToolBar,
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize

from ui.pages.home_page import HomePage
from ui.pages.search_artists_page import SearchArtistsPage
from ui.pages.release_group_list_page import ReleaseGroupListPage
from ui.pages.release_group_card_page import ReleaseGroupCardPage
from ui.pages.collection_page import CollectionPage
from ui.pages.search_release_groups_page import SearchReleaseGroupsPage

class MainWindow(QMainWindow):
    def __init__ (self, app):
        super().__init__()
        # Initialize main window parameters
        self.app = app
        self.setWindowTitle('MKPS')
        self.resize(QSize(1280, 720))
        self.setStatusBar(QStatusBar(self))

        # Initialize central QStackedWidget
        self.pages = QStackedWidget(self)
        self.setCentralWidget(self.pages)
        self.history_stack = []

        # Initialize dynamic pages and add to StackedWidget
        self.home_page = HomePage(self)
        self.pages.addWidget(self.home_page)
        self.search_artists_page = SearchArtistsPage(self)
        self.pages.addWidget(self.search_artists_page)
        self.release_group_list_page = ReleaseGroupListPage(self)
        self.pages.addWidget(self.release_group_list_page)
        self.release_group_card_page = ReleaseGroupCardPage(self)
        self.pages.addWidget(self.release_group_card_page)
        self.collection_page = CollectionPage(self)
        self.pages.addWidget(self.collection_page)
        self.search_release_groups_page = SearchReleaseGroupsPage(self)
        self.pages.addWidget(self.search_release_groups_page)

        # Initialize ToolBar
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        # Home Button
        self.home_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.GoHome), 'Home', self.toolbar)
        self.home_action.triggered.connect(lambda checked, page=self.home_page: self.navigate_to_page(page))
        self.home_action.setDisabled(True)
        self.toolbar.addAction(self.home_action)
        # Back Button
        self.back_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), 'Back', self.toolbar)
        self.back_action.setShortcut('Alt+Left')
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setDisabled(True)
        self.toolbar.addAction(self.back_action)

        # Signal for page changes
        self.pages.currentChanged.connect(self.page_change_check)

    def navigate_to_page(self, page):
        self.history_stack.append(self.pages.currentIndex())
        self.pages.setCurrentWidget(page)
        self.back_action.setEnabled(True)

    def go_back(self):
        self.pages.setCurrentIndex(self.history_stack.pop())
        self.back_action.setDisabled(not self.history_stack)

    def page_change_check(self):
        self.home_action.setDisabled(self.pages.currentWidget() == self.home_page)
