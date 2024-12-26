from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class HomePage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        
        layout = QVBoxLayout(self)
        artistSearchPageButton = QPushButton('Search Artists', self)
        artistSearchPageButton.clicked.connect(self.navigateToArtistSearchPage)
        collectionPageButton = QPushButton('My Collection', self)
        collectionPageButton.clicked.connect(self.navigateToCollectionPage)

        layout.addWidget(artistSearchPageButton)
        layout.addWidget(collectionPageButton)

        testButton = QPushButton('test', self)
        testButton.clicked.connect(self.testButtonClick)
        layout.addWidget(testButton)

    def navigateToArtistSearchPage(self):
        self.mainWindow.navigateToPage(self.mainWindow.artistSearchPage)

    def navigateToCollectionPage(self):
        self.mainWindow.navigateToPage(self.mainWindow.collectionPage)

    def testButtonClick(self):
        # for testing
        return