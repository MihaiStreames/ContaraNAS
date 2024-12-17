from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPixmap, Qt


class SteamGameButton(QPushButton):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.set_style()

    def set_style(self):
        pixmap = QPixmap(self.image_path)

        max_size = 400
        scaled_pixmap = pixmap.scaled(max_size, max_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setFixedSize(scaled_pixmap.size())

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