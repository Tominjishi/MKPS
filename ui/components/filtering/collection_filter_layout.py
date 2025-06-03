from abc import abstractmethod
# ui components
from ui.components.filtering.filter_row import FilterRow
# qt
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QButtonGroup,
    QScrollArea,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QApplication,
)


# Abstract class for filter boxes in collection page
# General vertical layout:
#   Header horizontal layout:
#       Title - Search Bar - Add Button
#   Scroll area widget:
#       Vertical layout of FilterRows
class FilterLayout(QVBoxLayout):
    def __init__(self, title, elements):
        super().__init__()
        header_bar = QHBoxLayout()
        if title:
            title_label = QLabel(title)
            header_bar.addWidget(title_label)
        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.search)
        header_bar.addWidget(self.search_bar)

        add_button = QPushButton()
        add_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        add_button.clicked.connect(self.insert)
        header_bar.addWidget(add_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()  # widget for scrollarea
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(scroll_widget)

        self.check_box_group = QButtonGroup(self)
        self.check_box_group.setExclusive(False)

        self.addLayout(header_bar)
        self.addWidget(self.scroll_area)

        self.fill(elements)

    # Fill filter list using list of dictionaries with name and id key
    def fill(self, elements):
        for i, element in enumerate(elements):
            row = FilterRow(element['name'])
            self.check_box_group.addButton(row.checkbox)
            self.scroll_layout.addWidget(row)
            row.delete_button.clicked.connect(
                lambda checked, n=element['name'], db_id=element['id']: self.delete(n, db_id)
            )
        self.adjust_scrollarea_height()

    # Delete all rows
    def clear(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            item.widget().deleteLater()

    def search(self, text):
        for checkbox in self.check_box_group.buttons():
            checkbox.parentWidget().setVisible(text.lower() in checkbox.text().lower())

    def uncheck_all(self):
        self.search_bar.clear()
        self.check_box_group.blockSignals(True)
        for button in self.check_box_group.buttons():
            button.setChecked(False)
        self.check_box_group.blockSignals(False)

    # Limit scrollarea max height to just enough to fit all rows
    def adjust_scrollarea_height(self):
        QApplication.instance().processEvents()
        height = self.scroll_area.widget().sizeHint().height()
        self.scroll_area.setMaximumHeight(height)

    @abstractmethod
    def delete(self, name, db_id):
        pass

    @abstractmethod
    def insert(self):
        pass

