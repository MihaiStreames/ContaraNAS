from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar


class LoadingScreen(QDialog):
    def __init__(self, loader, callback):
        super().__init__()
        self.setWindowTitle("Loading...")
        self.setFixedSize(400, 200)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Initializing game cache...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)

        loader.progress.connect(self.update_progress)
        loader.finished.connect(self.on_finished)
        self.finished_callback = callback

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        self.close()
        self.finished_callback()
