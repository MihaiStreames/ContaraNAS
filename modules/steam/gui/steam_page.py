import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QFrame, QTextBrowser, QToolButton
)

from .components.steam_game_button import SteamGameButton


class SteamPage(QWidget):
    def __init__(self, data, main_window):
        super().__init__()
        self.data = data
        self.main_window = main_window
        self.selected_button = None
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

        image_dir = os.path.join('resources', 'images', 'steam')

        for game_name, game_data in self.data.items():
            image_path = os.path.normpath(os.path.join(image_dir, f"{game_data['app_id']}.jpg"))
            button = SteamGameButton(image_path, game_data, self)
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

    def update_selected_game(self, button):
        if self.selected_button:
            # Reset the previous button's style
            self.selected_button.update_style(highlight=False)

        # Highlight the selected button
        button.update_style(highlight=True)
        self.selected_button = button

        # Update the right panel with game details
        game_data = button.game_data
        self.details_text.setHtml(self.format_game_details(game_data))

    @staticmethod
    def format_game_details(element_data):
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

        return html
