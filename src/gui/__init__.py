# Modular GUI package for Endava OneDrive-mimic App
from .page_manager import PageManager
from PySide6.QtWidgets import QApplication
import sys
from PySide6.QtCore import Qt

__all__ = ["run_app"]


def run_app():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background: #f7f8fa;
            color: #222;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 15px;
        }
        QLabel, QLineEdit, QTextEdit {
            color: #222;
            font-size: 15px;
            font-weight: 400;
        }
        QPushButton {
            background: transparent;
            color: #222;
            border: none;
            border-radius: 8px;
            padding: 7px 18px;
            font-size: 15px;
            font-weight: 500;
        }
        QPushButton:hover {
            background: #f0f1f5;
        }
        QPushButton#uploadBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0a2e8c, stop:1 #1138f5);
            color: #fff;
            font-size: 16px;
            border-radius: 22px;
            padding: 10px 32px;
            font-weight: 600;
            margin-bottom: 18px;
        }
        QPushButton#uploadBtn:hover {
            background: #1138f5;
        }
        QFrame#sidebar {
            background: #fff;
            border-right: 1px solid #e5e7eb;
        }
        QFrame#sidebar QPushButton {
            background: transparent;
            color: #222;
            border-radius: 8px;
            padding: 8px 0 8px 12px;
            text-align: left;
            font-size: 15px;
            font-weight: 400;
        }
        QFrame#sidebar QPushButton:hover {
            background: #f0f1f5;
            color: #1138f5;
        }
        QFrame#sidebar QLabel {
            color: #888;
            font-size: 13px;
            margin-top: 16px;
            margin-bottom: 2px;
            font-weight: 600;
        }
        QFrame#sidebar QPushButton[quickaccess="true"] {
            color: #1138f5;
            font-size: 14px;
            font-weight: 500;
        }
        QLabel#logo {
            font-size: 26px;
            font-weight: bold;
            color: #ff4b2b;
        }
        QFrame#topbar {
            background: #ff4b2b;
            min-height: 56px;
            border-bottom: 1px solid #f7f8fa;
        }
        QFrame#topbar QLabel, QFrame#topbar QLineEdit {
            color: #fff;
        }
        QFrame#card {
            background: #fff;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            padding: 18px 18px 12px 18px;
            box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
        }
        QPushButton#filterBtn {
            background: #fff;
            color: #222;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 6px 20px;
            font-weight: 500;
            margin-right: 6px;
        }
        QPushButton#filterBtn[selected="true"] {
            background: #1138f5;
            color: #fff;
            border: 1px solid #1138f5;
        }
        QTableWidget {
            background: #fff;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            font-size: 15px;
            font-weight: 400;
            gridline-color: #f0f1f5;
        }
        QHeaderView::section {
            background: #f3f4f6;
            font-weight: 600;
            border: none;
            padding: 8px;
            color: #222;
        }
        QTableWidget::item {
            padding: 8px 4px;
        }
        QTableWidget::item:selected {
            background: #eaf1fb;
        }
    """)
    manager = PageManager()
    manager.show()
    sys.exit(app.exec())
