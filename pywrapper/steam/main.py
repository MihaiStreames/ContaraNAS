import os
import platform
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QTextBrowser
)

from manager import SteamGameManager


class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("JSON Element Viewer")
        self.setMinimumSize(QSize(800, 600))

        # data is now a dictionary of { "GameName": {...game_data...}, ... }
        self.data = data

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Create left panel (buttons)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)  # 1 is the stretch factor

        # Create right panel (details view)
        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel, 2)  # 2 is the stretch factor

    def create_left_panel(self):
        """Create scrollable left panel with buttons"""
        # Create a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Create widget to hold buttons
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create a button for each JSON element
        for index, element in enumerate(self.data):
            button = QPushButton(f"{index}: {element}")
            # Store the element data in the button's property
            button.setProperty("element_data", self.data[element])
            button.clicked.connect(self.on_element_clicked)
            button_layout.addWidget(button)

        scroll.setWidget(button_widget)
        return scroll

    def create_right_panel(self):
        """Create right panel for displaying element details"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)

        self.details_text = QTextBrowser()
        self.details_text.setOpenExternalLinks(True)
        self.details_text.setPlaceholderText("Select an element to view details")
        self.details_layout.addWidget(self.details_text)

        scroll.setWidget(details_widget)
        return scroll

    def on_element_clicked(self):
        """Handle button click and update details view with formatted HTML"""
        button = self.sender()
        element_data = button.property("element_data")

        # Extract known fields
        name = element_data.get("name", "Unknown Game")
        app_id = element_data.get("app_id", "")
        cover_image_url = element_data.get("cover_image_url", "")
        store_page_url = element_data.get("store_page_url", None)
        size_on_disk = element_data.get("size_on_disk", "N/A")
        dlc_size = element_data.get("dlc_size", "N/A")
        shader_cache_size = element_data.get("shader_cache_size", "N/A")
        workshop_content_size = element_data.get("workshop_content_size", "N/A")
        depots = element_data.get("depots", {})

        # Start constructing the HTML
        # Title
        html = f"<h2><b>{name}</b></h2>"

        # Optional cover image (if you want to display it):
        # if cover_image_url:
        #     html += f'<p><img src="{cover_image_url}" alt="Cover Image" width="300"></p>'

        # Store page link
        if store_page_url:
            html += f'<p><b>Store Page:</b> <a href="{store_page_url}">{store_page_url}</a></p>'

        # App ID
        html += f"<p><b>App ID:</b> {app_id}</p>"

        # Other attributes table
        html += """
        <table border="0" cellspacing="5" cellpadding="5">
          <tr><td><b>Size on Disk:</b></td><td>{size_on_disk}</td></tr>
          <tr><td><b>DLC Size:</b></td><td>{dlc_size}</td></tr>
          <tr><td><b>Shader Cache Size:</b></td><td>{shader_cache_size}</td></tr>
          <tr><td><b>Workshop Content Size:</b></td><td>{workshop_content_size}</td></tr>
        </table>
        """.format(
            size_on_disk=size_on_disk,
            dlc_size=dlc_size,
            shader_cache_size=shader_cache_size,
            workshop_content_size=workshop_content_size
        )

        # Depots Section
        if depots:
            html += "<h3>Depots:</h3><ul>"
            for depot_name, depot_size in depots.items():
                html += f"<b>{depot_name}:</b> {depot_size}</li>"
            html += "</ul>"
        else:
            html += "<p><i>No depots available</i></p>"

        self.details_text.setHtml(html)

        # Highlight the selected button
        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet("")
        button.setStyleSheet("background-color: lightblue;")


def main():
    if platform.system() == 'Windows':
        steam_path = r'C:\Program Files (x86)\Steam'
    else:
        steam_path = os.path.expanduser('~/.steam/steam')

    # Initialize SteamGameManager
    manager = SteamGameManager(steam_path, cache_dir=".cache/games")
    manager.load_installed_games()

    # Serialize the games into a list of dicts
    serialized_games = manager.serialize_games()

    # Convert the list of games into a dictionary keyed by game name for convenience
    # For example: {"GameName": {...}, "AnotherGame": {...}}
    # If you prefer AppID: {app_id: {...}}
    data_dict = {game["name"]: game for game in serialized_games}

    # Create the application instance
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow(data_dict)
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()