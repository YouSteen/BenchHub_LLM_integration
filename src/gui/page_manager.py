from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer
from .login_page import LoginPage
from .loading_page import LoadingPage
from .main_window import MainWindow


class PageManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Endava BenchHub")
        self.setMinimumSize(1100, 700)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.login_page = LoginPage(self)
        self.loading_page = LoadingPage(self)
        self.main_window = MainWindow(self)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.loading_page)
        self.stack.addWidget(self.main_window)
        self.stack.setCurrentWidget(self.login_page)

    def show_loading(self):
        self.stack.setCurrentWidget(self.loading_page)
        QTimer.singleShot(2000, self.show_main)

    def show_main(self):
        self.stack.setCurrentWidget(self.main_window)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)
