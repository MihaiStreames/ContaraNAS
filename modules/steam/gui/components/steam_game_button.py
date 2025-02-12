from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton


class SteamGameButton(QPushButton):
    def __init__(self, image_path, game_data, steam_page):
        super().__init__()
        self.image_path = image_path
        self.game_data = game_data
        self.steam_page = steam_page
        self.selected = False
        self.init_ui()

    def init_ui(self):
        pixmap = QPixmap(self.get_absolute_path(self.image_path))

        if pixmap.isNull():
            print(f"Image not found: {self.image_path}")
            self.set_default_style()
            return

        max_w = 460 / 2
        max_h = 215 / 2
        scaled_pixmap = pixmap.scaled(max_w, max_h)

        self.setFixedSize(scaled_pixmap.width(), scaled_pixmap.height())
        self.update_style(highlight=False)

    def get_absolute_path(self, path):
        import os
        return os.path.abspath(path)

    def set_default_style(self):
        self.setFixedSize(100, 50)
        self.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                background-color: #ccc;
                color: black;
                border: 2px dashed #999;
                font: bold 12px;
                text-align: center;
            }
        """)
        self.setText("No Image")

    def update_style(self, highlight):
        base_style = f"""
            QPushButton {{
                border-radius: 15px;
                background-image: url("{self.get_absolute_path(self.image_path)}");
                background-repeat: no-repeat;
                background-position: center;
                border: 2px solid #ccc;
            }}
        """
        if highlight:
            base_style += """
                QPushButton {
                    background-color: lightblue;
                    border: 2px solid #0078d7;
                }
            """
        self.setStyleSheet(base_style)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.steam_page.update_selected_game(self)
