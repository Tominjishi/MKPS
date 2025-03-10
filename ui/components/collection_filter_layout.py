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
    MAX_FILTER_AREA_HEIGHT = 150

    def __init__(self, title=''):
        super().__init__()
        # Header above filter list for displaying search bar and optional title
        header_bar = QHBoxLayout()
        if title:
            title_label = QLabel(title)
            header_bar.addWidget(title_label)
        self.search_bar = QLineEdit()
        header_bar.addWidget(self.search_bar)
        
        filter_scroll_area = QScrollArea()
        filter_scroll_area.setMaximumHeight(self.MAX_FILTER_AREA_HEIGHT)
        filter_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        filter_scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        scroll_area_widget = QWidget()  # widget for scrollarea
        self.check_box_layout = QVBoxLayout(scroll_area_widget)
        
        self.check_box_group = QButtonGroup(self)
        self.check_box_group.setExclusive(False)

        filter_scroll_area.setWidget(scroll_area_widget)

        self.addLayout(header_bar)
        self.addWidget(filter_scroll_area)

    def uncheck_all(self):
        self.search_bar.clear()
        self.check_box_group.blockSignals(True)
        for button in self.check_box_group.buttons():
            button.setChecked(False)
        self.check_box_group.blockSignals(False)