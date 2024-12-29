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
        self.checkBoxLayout = QVBoxLayout(areaWidget)
        
        self.checkBoxGroup = QButtonGroup(self)
        self.checkBoxGroup.setExclusive(False)

        filterArea.setWidget(areaWidget)
        self.addWidget(filterArea)

    def uncheckAll(self):
        self.checkBoxGroup.blockSignals(True)
        for button in self.checkBoxGroup.buttons():
            button.setChecked(False)
        self.checkBoxGroup.blockSignals(False)