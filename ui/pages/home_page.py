from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QPushButton
)

class HomePage(QWidget):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        
        layout = QVBoxLayout(self)
        artistSearchPageButton = QPushButton('Search Artists', self)
        artistSearchPageButton.clicked.connect(self.navigateToArtistSearchPage)
        collectionPageButton = QPushButton('My Collection', self)

        layout.addWidget(artistSearchPageButton)
        layout.addWidget(collectionPageButton)

    def navigateToArtistSearchPage(self):
        self.mainWindow.navigateToPage(self.mainWindow.artistSearchPage)