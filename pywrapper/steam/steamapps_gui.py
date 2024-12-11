import platform, os, sys, json
from steamapps import get_steam_libraries, get_installed_games
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
    QTextEdit
)
from PyQt6.QtCore import Qt, QSize

class MainWindow(QMainWindow):
    def __init__(self, json_file):
        super().__init__()
        self.setWindowTitle("JSON Element Viewer")
        self.setMinimumSize(QSize(800, 600))
        
        # Load JSON data
        try:
            self.data = json_file
        except Exception as e:
            self.data = dict()
            print(f"Error loading JSON file: {e}")
        
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
            print(self.data)
            button = QPushButton(f"{index}: {element}")
            # Store the element data in the button's property
            button.setProperty("element_data", self.data[element])
            button.clicked.connect(self.on_element_clicked)
            button_layout.addWidget(button)
        
        scroll.setWidget(button_widget)
        return scroll
        
    def create_right_panel(self):
        """Create right panel for displaying element details"""
        # Create a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create widget to hold details
        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)
        
        # Add initial message
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select an element to view details")
        self.details_layout.addWidget(self.details_text)
        
        scroll.setWidget(details_widget)
        return scroll
    
    def on_element_clicked(self):
        """Handle button click and update details view"""
        button = self.sender()
        element_data = button.property("element_data")

        formatted_data = ""
        for key, value in element_data.items():
            formatted_data += f"{key}: {value}\n"
        # Format the JSON data for display
        # formatted_data = json.dumps(element_data, indent=2)
        self.details_text.setText(formatted_data)
        
        # Optional: Highlight the selected button
        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet("")
        button.setStyleSheet("background-color: lightblue;")

def main():
    steam_pth = (
        r'C:\Program Files (x86)\Steam' if platform.system() == 'Windows'
        else os.path.expanduser('~/.steam/steam')
    )

    lib_pths = get_steam_libraries(steam_pth)
    games = get_installed_games(lib_pths)
    

    # Create the application instance
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow(games)
    window.show()
    dict()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

