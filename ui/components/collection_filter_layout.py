from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QButtonGroup,
    QScrollArea,
    QSizePolicy,
)

class FilterLayout(QVBoxLayout):
    def __init__(self, title=''):
        super().__init__()
        if title:
            titleLabel = QLabel(title)
            self.addWidget(titleLabel)
        
        filterArea = QScrollArea()
        filterArea.setMaximumHeight(200)
        filterArea.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        areaWidget = QWidget()  # widget for scrollarea
        self.filterLayout = QVBoxLayout(areaWidget)
        
        selectAll = QCheckBox('Select all')
        selectAll.setChecked(True)
        selectAll.toggled.connect(self.filterAll)
        self.filterLayout.addWidget(selectAll)

        self.filterButtons = QButtonGroup()
        self.filterButtons.setExclusive(False)

        filterArea.setWidget(areaWidget)
        self.addWidget(filterArea)

    def filterAll(self, checked):
        for button in self.filterButtons.buttons():
            button.setChecked(checked)