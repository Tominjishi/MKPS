from PySide6.QtWidgets import(
    QMainWindow,
    QStatusBar,
    QStackedWidget,
    QToolBar,
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize

from ui.pages.home_page import HomePage
from ui.pages.artist_search_page import ArtistSearchPage
from ui.pages.release_group_list_page import ReleaseGroupListPage
from ui.pages.release_group_card_page import ReleaseGroupCardPage
from ui.pages.collection_page import CollectionPage

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

        # Initialize dynamic pages and add to stackedwidget
        self.homePage = HomePage(self)
        self.artistSearchPage = ArtistSearchPage(self)
        self.releaseGroupListPage = ReleaseGroupListPage(self)
        self.releaseGroupCardPage = ReleaseGroupCardPage(self)
        self.collectionPage = CollectionPage(self)
        self.pages.addWidget(self.homePage)
        self.pages.addWidget(self.artistSearchPage)
        self.pages.addWidget(self.releaseGroupListPage)
        self.pages.addWidget(self.releaseGroupCardPage)
        self.pages.addWidget(self.collectionPage)
        
        # Initialize ToolBar
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        # Home Action
        self.homeAction = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.GoHome),
            'Back',
            self.toolbar
        )
        self.homeAction.triggered.connect(
            lambda checked, page=self.homePage: self.navigateToPage(page)
        )
        self.homeAction.setDisabled(True)
        self.toolbar.addAction(self.homeAction)
        # Back Button
        self.backAction = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious),
            'Back',
            self.toolbar
        )
        self.backAction.setShortcut('Alt+Left')
        self.backAction.triggered.connect(self.goBack)
        self.backAction.setDisabled(True)
        self.toolbar.addAction(self.backAction)

        # Signal for page changes
        self.pages.currentChanged.connect(self.pageChangeCheck)

    def navigateToPage(self, page):
        currIndex = self.pages.currentIndex()
        self.history_stack.append(currIndex)
        self.pages.setCurrentWidget(page)
        self.backAction.setEnabled(True)

    def goBack(self):
        previousIndex = self.history_stack.pop()
        self.pages.setCurrentIndex(previousIndex)
        self.backAction.setDisabled(not self.history_stack)

    def pageChangeCheck(self):
        self.homeAction.setDisabled(self.pages.currentWidget() == self.homePage)
