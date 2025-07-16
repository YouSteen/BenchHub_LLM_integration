from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFrame,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QMenu,
    QMessageBox,
)
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QThread,
    Signal,
    QObject,
    Slot,
)
from PySide6.QtGui import QPixmap, QFont
import os
import sys
import requests
import msal
import io
import pandas as pd
import threading

from .login_page import CLIENT_ID, AUTHORITY, SCOPES

# Token cache path
if sys.platform == "win32":
    CACHE_FILE = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "BenchHubLLM",
        "token_cache.json",
    )
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
else:
    CACHE_FILE = os.path.expanduser("~/.benchhubllm_token_cache.json")


def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    return cache


def get_cached_token():
    cache = load_cache()
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID, authority=AUTHORITY, token_cache=cache
    )
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]
    return None


class HoverLabel(QLabel):
    def __init__(self, *args, margin_right=0, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_style = f"margin-right: {margin_right}px;" if margin_right else ""
        self._hover_style = (
            f"background: #ffe5d0; border-radius: 6px; margin-right: {margin_right}px;"
        )
        self.setStyleSheet(self._default_style)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._default_style)
        super().leaveEvent(event)


class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(350)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)

    def setCurrentIndex(self, idx):
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        super().setCurrentIndex(idx)
        self.setWindowOpacity(0.0)
        self._anim.start()


class GraphAPIClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        token = get_cached_token()
        if not token:
            raise Exception("No valid token found. Please log in.")
        self.headers = {"Authorization": f"Bearer {token}"}

    def find_folder_by_name(self, name, parent_id=None):
        url = (
            f"{self.BASE_URL}/me/drive/items/{parent_id}/children"
            if parent_id
            else f"{self.BASE_URL}/me/drive/root/children"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        for item in resp.json().get("value", []):
            if item.get("name") == name and "folder" in item:
                return item
        return None

    def list_onedrive_files(self, folder_id=None):
        url = (
            f"{self.BASE_URL}/me/drive/items/{folder_id}/children"
            if folder_id
            else f"{self.BASE_URL}/me/drive/root/children"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("value", [])


class FileLoaderWorker(QObject):
    finished = Signal(list, object)
    error = Signal(str)

    def __init__(self, client, folder_id):
        super().__init__()
        self.client = client
        self.folder_id = folder_id

    def run(self):
        print(
            "[DEBUG][FileLoaderWorker.run] Current thread:",
            threading.current_thread().name,
        )
        try:
            files = self.client.list_onedrive_files(self.folder_id)
            self.finished.emit(files, None)
        except Exception as e:
            self.finished.emit([], e)


class ActionButton(QPushButton):
    def __init__(self, text, base_style, hover_style, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self._base_style = base_style
        self._hover_style = hover_style
        self.setStyleSheet(self._base_style)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        super().leaveEvent(event)


class FileListItemWidget(QWidget):
    def __init__(self, item_data, preview_callback, recommend_callback):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 6, 18, 6)
        layout.setSpacing(12)
        # Icon
        if "folder" in item_data:
            emoji = "\U0001f4c1"
        elif item_data.get("name", "").lower().endswith(".xlsx"):
            emoji = "\U0001f4c4"
        else:
            emoji = ""
        icon = QLabel(emoji)
        icon.setStyleSheet(
            "font-size: 28px; margin-right: 10px; background: transparent;"
        )
        layout.addWidget(icon)
        # File name
        label = QLabel(item_data.get("name", "Unnamed"))
        label.setStyleSheet(
            "font-size: 18px; font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
        )
        layout.addWidget(label, 1)
        # Action buttons for .xlsx files
        if "folder" not in item_data and item_data.get("name", "").lower().endswith(
            ".xlsx"
        ):
            preview_btn = ActionButton(
                " Preview",
                "border: none; font-size: 20px; font-weight: 600; color: #FF4B2B; background: #fff3ee; border-radius: 8px; margin-right: 12px; padding: 0 18px;",
                "border: none; font-size: 20px; font-weight: 600; color: #b92c00; background: #ffe5d0; border-radius: 8px; margin-right: 12px; padding: 0 18px;",
            )
            preview_btn.setFixedSize(160, 44)
            preview_btn.setToolTip("Preview file")
            preview_btn.clicked.connect(lambda _, d=item_data: preview_callback(d))
            layout.addWidget(preview_btn)
            email_btn = ActionButton(
                " Send email with recommendations ",
                "border: none; font-size: 16px; color: #fff; background: #FF4B2B; border-radius: 8px; padding: 0 18px; font-weight: 500;",
                "border: none; font-size: 16px; color: #fff; background: #ff7b5a; border-radius: 8px; padding: 0 18px; font-weight: 500;",
            )
            email_btn.setFixedSize(260, 44)
            email_btn.setToolTip(" Send email with recommendations ")
            email_btn.clicked.connect(lambda _, d=item_data: recommend_callback(d))
            layout.addWidget(email_btn)
        else:
            layout.addSpacing(160)
            layout.addSpacing(260)
        layout.addStretch(0)
        self.setStyleSheet("background: transparent;")


class MainWindow(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowOpacity(0.0)
        self._fade_in()
        self._current_folder_id = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._create_titlebar())
        self.stack = AnimatedStackedWidget()
        self.stack.addWidget(self._create_onedrive_page())
        root_layout.addWidget(self.stack, 1)

    def _fade_in(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(600)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        self._fade_anim = anim

    def _get_logo_path(self):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, "assets", "logo.png")
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
        )

    def _create_titlebar(self):
        bar = QFrame()
        bar.setFixedHeight(64)
        bar.setStyleSheet("background: #f5f6fa;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 8, 24, 8)

        # Logo
        logo_label = QLabel()
        pix = QPixmap(self._get_logo_path())
        if not pix.isNull():
            logo_label.setPixmap(
                pix.scaled(180, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_label.setMaximumHeight(48)
        layout.addWidget(logo_label)

        layout.addStretch(1)

        # Search bar
        search_frame = QFrame()
        search_frame.setStyleSheet("background: #fff; border-radius: 24px;")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(18, 0, 0, 0)
        icon = QLabel("🔍")
        icon.setFont(QFont("Segoe UI Emoji", 18))
        icon.setStyleSheet("color: #888;")
        sf_layout.addWidget(icon)
        search = QLineEdit()
        search.setPlaceholderText("Search")
        search.setFont(QFont("Segoe UI", 15))
        search.setStyleSheet("border: none; background: transparent; padding: 8px;")
        search.setMinimumWidth(340)
        sf_layout.addWidget(search)
        search_frame.setFixedHeight(44)
        layout.addWidget(search_frame)

        layout.addStretch(1)

        # Settings & maintenance icons
        for emoji in ("⚙️", "🛠️"):
            lbl = HoverLabel(emoji)
            lbl.setFont(QFont("Segoe UI Emoji", 38))
            layout.addWidget(lbl)
            layout.addSpacing(16)

        return bar

    def _create_onedrive_page(self):
        page = QFrame()
        v = QVBoxLayout(page)
        v.setContentsMargins(64, 48, 64, 48)
        v.setSpacing(24)

        # Title and refresh button row
        title_row = QHBoxLayout()
        title = QLabel("<b>BenchHub Drive</b>")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.refresh_btn = ActionButton(
            "\u27f3 Refresh",
            "border: none; font-size: 18px; color: #fff; background: #FF4B2B; border-radius: 8px; font-weight: 700;",
            "border: none; font-size: 18px; color: #fff; background: #ff7b5a; border-radius: 8px; font-weight: 700;",
        )
        self.refresh_btn.setFixedSize(140, 44)
        self.refresh_btn.setToolTip("Refresh file list")
        self.refresh_btn.clicked.connect(self._refresh_files)
        title_row.addWidget(self.refresh_btn)
        v.addLayout(title_row)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(
            "QListWidget { background: #fff; border-radius: 18px; border: 1.5px solid #e5e7eb; }"
        )
        self.file_list.setMinimumSize(800, 500)
        self.file_list.itemClicked.connect(self._on_item_clicked)
        v.addWidget(self.file_list, 1)

        self._nav_stack = []
        QTimer.singleShot(100, lambda: self._show_folder())
        return page

    def _refresh_files(self):
        self._show_folder(
            self._nav_stack[-1][0] if self._nav_stack else None, force_refresh=True
        )

    def _show_folder(self, folder_id=None, force_refresh=False):
        self.file_list.clear()
        self.refresh_btn.setText("\u27f3 Loading...")
        self.refresh_btn.setEnabled(False)
        client = GraphAPIClient()
        if folder_id is None:
            root = client.find_folder_by_name("BenchHub")
            if not root:
                self.file_list.addItem("(BenchHub folder not found)")
                self.refresh_btn.setText("\u27f3 Refresh")
                self.refresh_btn.setEnabled(True)
                return
            folder_id = root["id"]
            self._nav_stack = [(folder_id, "BenchHub")]
        self._current_folder_id = folder_id
        # Use a worker thread for loading
        self._file_loader_thread = QThread()
        self._file_loader_worker = FileLoaderWorker(client, folder_id)
        self._file_loader_worker.moveToThread(self._file_loader_thread)
        self._file_loader_thread.started.connect(self._file_loader_worker.run)
        self._file_loader_worker.finished.connect(self._on_files_loaded)
        self._file_loader_worker.finished.connect(self._file_loader_thread.quit)
        self._file_loader_worker.finished.connect(self._file_loader_worker.deleteLater)
        self._file_loader_thread.finished.connect(self._file_loader_thread.deleteLater)
        self._file_loader_thread.start()

    @Slot(list, object)
    def _on_files_loaded(self, files, err):
        print(
            "[DEBUG][MainWindow._on_files_loaded] Current thread:",
            threading.current_thread().name,
        )
        folder_id = self._current_folder_id
        self.refresh_btn.setText("\u27f3 Refresh")
        self.refresh_btn.setEnabled(True)
        self.file_list.clear()
        if err:
            self.file_list.addItem(QListWidgetItem(f"Error: {err}"))
            return
        # Up-item
        if len(self._nav_stack) > 1:
            up = QListWidgetItem(".. (Up)")
            up.setData(Qt.UserRole, {"up": True})
            self.file_list.addItem(up)
        for f in files:
            name = f.get("name", "").lower()
            if "folder" in f or name.endswith(".xlsx"):
                item = QListWidgetItem()
                item.setData(Qt.UserRole, f)
                self.file_list.addItem(item)
                widget = FileListItemWidget(
                    f,
                    preview_callback=self._on_preview,
                    recommend_callback=lambda data: QMessageBox.information(
                        self,
                        "Send recommendations",
                        f"Send recommendations for: {data['name']}",
                    ),
                )
                self.file_list.setItemWidget(item, widget)
                item.setSizeHint(widget.sizeHint())

    def _on_item_clicked(self, list_item):
        data = list_item.data(Qt.UserRole) or {}
        if data.get("up"):
            if len(self._nav_stack) > 1:
                self._nav_stack.pop()
                prev_id, _ = self._nav_stack[-1]
                self._show_folder(prev_id)
        elif "folder" in data:
            self._nav_stack.append((data["id"], data["name"]))
            self._show_folder(data["id"])

    def _on_preview(self, data):
        if "folder" in data or not data.get("name", "").lower().endswith(".xlsx"):
            QMessageBox.information(
                self, "Preview", "Only .xlsx files can be previewed."
            )
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Preview: {data['name']}")
        dlg.setMinimumSize(700, 500)
        vb = QVBoxLayout(dlg)
        lbl = QLabel(f"<b>Preview: {data['name']}</b>")
        vb.addWidget(lbl)
        prog = QProgressBar()
        prog.setRange(0, 0)
        vb.addWidget(prog)
        table = QTableWidget()
        table.setVisible(False)
        vb.addWidget(table, 1)
        back = QPushButton("Back")
        back.clicked.connect(dlg.close)
        vb.addWidget(back)

        def fetch():
            try:
                client = GraphAPIClient()
                url = f"https://graph.microsoft.com/v1.0/me/drive/items/{data['id']}/content"
                resp = requests.get(url, headers=client.headers)
                resp.raise_for_status()
                df = pd.read_excel(io.BytesIO(resp.content), engine="openpyxl").iloc[
                    :10, :10
                ]
                table.setRowCount(df.shape[0])
                table.setColumnCount(df.shape[1])
                table.setHorizontalHeaderLabels([str(c) for c in df.columns])
                for i in range(df.shape[0]):
                    for j in range(df.shape[1]):
                        table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.setVisible(True)
                prog.setVisible(False)
            except Exception as ex:
                lbl.setText(f"<span style='color:red'>Error: {ex}</span>")
                prog.setVisible(False)

        QTimer.singleShot(100, fetch)
        dlg.exec()
