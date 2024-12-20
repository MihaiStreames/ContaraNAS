import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QPushButton, QFrame, QTextBrowser, QToolButton
)
from .components.steam_game_button import SteamGameButton


class SteamPage(QWidget):
    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Create left panel (game buttons)
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel, 1)

        # Create right panel (game details)
        self.right_panel = self.create_right_panel()
        layout.addWidget(self.right_panel, 2)

        # Back button
        back_button = QToolButton(self)
        back_button.setText("← Back to Modules")
        back_button.clicked.connect(self.main_window.go_back_to_selection)
        layout.addWidget(back_button)

    def create_left_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        image_dir = "resources/images"

        for game_name, game_data in self.data.items():
            image_path = os.path.normpath(os.path.join(image_dir, f"{game_data['app_id']}.jpg"))
            button = SteamGameButton(image_path)
            button.setProperty("element_data", game_data)
            button.clicked.connect(self.on_element_clicked)
            button_layout.addWidget(button)

        scroll.setWidget(button_widget)
        return scroll

    def create_right_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)

        self.details_text = QTextBrowser()
        self.details_text.setOpenExternalLinks(True)
        self.details_text.setPlaceholderText("Select a game to view details")
        self.details_layout.addWidget(self.details_text)

        scroll.setWidget(details_widget)
        return scroll

    def on_element_clicked(self):
        button = self.sender()
        element_data = button.property("element_data")

        # Display game details
        name = element_data.get("name", "Unknown Game")
        app_id = element_data.get("app_id", "")
        store_page_url = element_data.get("store_page_url", None)
        size_on_disk = element_data.get("size_on_disk", "N/A")
        dlc_size = element_data.get("dlc_size", "N/A")
        shader_cache_size = element_data.get("shader_cache_size", "N/A")
        workshop_content_size = element_data.get("workshop_content_size", "N/A")
        depots = element_data.get("depots", {})

        html = f"<h2><b>{name}</b></h2>"

        if store_page_url:
            html += f'<p><b>Store Page:</b> <a href="{store_page_url}">{store_page_url}</a></p>'

        html += f"<p><b>App ID:</b> {app_id}</p>"

        html += f"""
        <table border="0" cellspacing="5" cellpadding="5">
          <tr><td><b>Size on Disk:</b></td><td>{size_on_disk}</td></tr>
          <tr><td><b>DLC Size:</b></td><td>{dlc_size}</td></tr>
          <tr><td><b>Shader Cache Size:</b></td><td>{shader_cache_size}</td></tr>
          <tr><td><b>Workshop Content Size:</b></td><td>{workshop_content_size}</td></tr>
        </table>
        """

        if depots:
            html += "<h3>Depots:</h3><ul>"
            for depot_name, depot_size in depots.items():
                html += f"<li><b>{depot_name}:</b> {depot_size}</li>"
            html += "</ul>"
        else:
            html += "<p><i>No depots available</i></p>"

        self.details_text.setHtml(html)

        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 15px;
                    background-color: #f0f0f0;
                    border: 2px solid #ccc;
                }
            """)
        button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                background-color: lightblue;
                border: 2px solid #0078d7;
            }
        """)