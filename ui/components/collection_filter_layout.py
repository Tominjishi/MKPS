from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QLabel,
    QButtonGroup,
    QScrollArea,
    QSizePolicy,
    QHBoxLayout,
    QLineEdit,
)
from PySide6.QtCore import Qt

class FilterLayout(QVBoxLayout):
    def __init__(self, title=''):
        super().__init__()
        headerBar = QHBoxLayout()
        if title:
            titleLabel = QLabel(title)
            headerBar.addWidget(titleLabel)
        self.searchBar = QLineEdit()
        headerBar.addWidget(self.searchBar)
        
        filterArea = QScrollArea()
        filterArea.setMaximumHeight(150)
        filterArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        filterArea.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        areaWidget = QWidget()  # widget for scrollarea
        self.checkBoxLayout = QVBoxLayout(areaWidget)
        
        self.checkBoxGroup = QButtonGroup(self)
        self.checkBoxGroup.setExclusive(False)

        filterArea.setWidget(areaWidget)

        self.addLayout(headerBar)
        self.addWidget(filterArea)

    def uncheckAll(self):
        self.searchBar.clear()
        self.checkBoxGroup.blockSignals(True)
        for button in self.checkBoxGroup.buttons():
            button.setChecked(False)
        self.checkBoxGroup.blockSignals(False)