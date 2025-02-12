import sys

from PySide6.QtWidgets import QApplication

from core.gui import MainWindow
from core.gui.utils import ModuleLoader


def main():
    app = QApplication(sys.argv)
    loader = ModuleLoader()
    loader.discover_modules()

    main_window = MainWindow(loader)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
