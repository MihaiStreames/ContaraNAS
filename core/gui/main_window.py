from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget
)
from core.utils import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, module_loader):
        super().__init__()
        self.setWindowTitle("NAS.Manager")
        self.setMinimumSize(800, 600)
        self.module_loader = module_loader

        # Main layout with stacked widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Stacked widget to switch pages
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Module selection page
        self.module_selection_page = self.create_module_selection_page()
        self.stacked_widget.addWidget(self.module_selection_page)

    def create_module_selection_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Available Modules")
        layout.addWidget(title)

        for module_name, module_class in self.module_loader.modules.items():
            button = QPushButton(f"Open {module_name.capitalize()} Module")
            button.clicked.connect(lambda checked, cls=module_class: self.open_module(cls))
            layout.addWidget(button)

        return page

    def open_module(self, module_class):
        try:
            module_instance = module_class(self)
            module_instance.execute()
        except Exception as e:
            logger.error(f"Error executing module: {e}")

    def set_module_page(self, page):
        self.stacked_widget.addWidget(page)
        self.stacked_widget.setCurrentWidget(page)

    def go_back_to_selection(self):
        self.stacked_widget.setCurrentWidget(self.module_selection_page)