from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton


class SteamGameButton(QPushButton):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.set_style()

    def set_style(self):
        max_w = 460 / 2
        max_h = 215 / 2

        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(max_w, max_h)
        self.setFixedSize(pixmap.width(), pixmap.height())

        if pixmap.isNull():
            return

        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: 15px;
                background-image: url("{self.image_path}");
                background-repeat: no-repeat;
                background-position: center;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)