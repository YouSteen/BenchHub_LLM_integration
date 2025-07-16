from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class LoadingPage(QWidget):
    def __init__(self, manager=None):
        super().__init__()
        self.manager = manager
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("<font color='#FF4B2B' size=6>Loading...</font>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
