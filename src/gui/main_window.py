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
    QTableView,
    QSplitter,
    QTextEdit,
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
    QAbstractTableModel,
    QModelIndex,
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
        # First, search in the specified parent or root
        url = (
            f"{self.BASE_URL}/me/drive/items/{parent_id}/children"
            if parent_id
            else f"{self.BASE_URL}/me/drive/root/children"
        )
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        for item in resp.json().get("value", []):
            if item.get("name") == name and "folder" in item:
                # Personal folder: return with driveId=None
                return {**item, "driveId": None}
        # If not found and searching root, also check sharedWithMe
        if parent_id is None:
            shared_url = f"{self.BASE_URL}/me/drive/sharedWithMe"
            shared_resp = requests.get(shared_url, headers=self.headers)
            shared_resp.raise_for_status()
            for shared_item in shared_resp.json().get("value", []):
                remote = shared_item.get("remoteItem", {})
                if remote.get("name") == name and "folder" in remote:
                    # Shared folder: return with driveId and id from remoteItem
                    return {
                        **remote,
                        "id": remote.get("id"),
                        "name": remote.get("name"),
                        "folder": remote.get("folder"),
                        "driveId": remote.get("parentReference", {}).get("driveId"),
                    }
        return None

    def list_onedrive_files(self, folder_id=None, drive_id=None):
        if drive_id:
            url = f"{self.BASE_URL}/drives/{drive_id}/items/{folder_id}/children"
        elif folder_id:
            url = f"{self.BASE_URL}/me/drive/items/{folder_id}/children"
        else:
            url = f"{self.BASE_URL}/me/drive/root/children"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json().get("value", [])


class FileLoaderWorker(QObject):
    finished = Signal(list, object)
    error = Signal(str)

    def __init__(self, client, folder_id, drive_id=None):
        super().__init__()
        self.client = client
        self.folder_id = folder_id
        self.drive_id = drive_id

    def run(self):
        print(
            "[DEBUG][FileLoaderWorker.run] Current thread:",
            threading.current_thread().name,
        )
        try:
            files = self.client.list_onedrive_files(self.folder_id, self.drive_id)
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
        # File name and creator
        name = item_data.get("name", "Unnamed")
        creator = "Unknown"
        created_by = item_data.get("createdBy", {})
        if isinstance(created_by, dict):
            user = created_by.get("user", {})
            if isinstance(user, dict):
                creator = user.get("displayName") or user.get("email") or "Unknown"
        label = QLabel(
            f"{name} <span style='color:#888;font-size:13px;'>(created by: {creator})</span>"
        )
        label.setStyleSheet(
            "font-size: 18px; font-family: 'Segoe UI', Arial, sans-serif; background: transparent;"
        )
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label, 1)
        # Only add preview button for .xlsx files
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
        else:
            layout.addSpacing(160)
        layout.addStretch(0)
        self.setStyleSheet("background: transparent;")


class PandasTableModel(QAbstractTableModel):
    def __init__(self, df, chunk_size=100):
        super().__init__()
        self._df = df
        self._chunk_size = chunk_size
        self._loaded_rows = min(chunk_size, len(df))

    def rowCount(self, parent=None):
        return self._loaded_rows

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self._df.iat[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        else:
            return str(self._df.index[section])

    def canFetchMore(self, parent=None):
        return self._loaded_rows < len(self._df)

    def fetchMore(self, parent=None):
        remaining = len(self._df) - self._loaded_rows
        items_to_fetch = min(self._chunk_size, remaining)
        if items_to_fetch > 0:
            self.beginInsertRows(
                parent or QModelIndex(),
                self._loaded_rows,
                self._loaded_rows + items_to_fetch - 1,
            )
            self._loaded_rows += items_to_fetch
            self.endInsertRows()


class MainWindow(QWidget):
    def _sidebar_btn_style(self, active=False):
        base = "padding: 16px; font-size: 16px; border: none; text-align: left; border-radius: 0 18px 18px 0; background: transparent; color: #222; font-family: 'Segoe UI', Arial, sans-serif;"
        active_bg = (
            "background: #FF4B2B; color: #fff; font-weight: 600;" if active else ""
        )
        # Orange hover for all, white text on hover
        hover = "QPushButton:hover { background: #FF4B2B; color: #fff; }"
        active_hover = "QPushButton:checked, QPushButton:pressed { background: #FF4B2B; color: #fff; }"
        return f"{base}{active_bg}{hover}{active_hover}"

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowOpacity(0.0)
        self._fade_in()
        self._current_folder_id = None

        # Main vertical layout: top bar, then horizontal split
        main_vlayout = QVBoxLayout(self)
        main_vlayout.setContentsMargins(0, 0, 0, 0)
        main_vlayout.setSpacing(0)

        # Top bar (titlebar) spans full width
        self._titlebar = self._create_titlebar()
        main_vlayout.addWidget(self._titlebar)

        # Horizontal layout: sidebar + content
        main_hlayout = QHBoxLayout()
        main_hlayout.setContentsMargins(0, 0, 0, 0)
        main_hlayout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("background: #fff; border-right: 1px solid #e5e7eb;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)
        # Sidebar title
        sb_title = QLabel("Navigation")
        sb_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #FF4B2B; padding: 24px 0 12px 24px;"
        )
        sb_layout.addWidget(sb_title)
        self.btn_main = QPushButton("Main")
        self.btn_main.setCheckable(True)
        self.btn_main.setChecked(True)
        self.btn_main.setCursor(Qt.PointingHandCursor)
        self.btn_main.setStyleSheet(self._sidebar_btn_style(active=True))
        self.btn_logs = QPushButton("Logs")
        self.btn_logs.setCheckable(True)
        self.btn_logs.setCursor(Qt.PointingHandCursor)
        self.btn_logs.setStyleSheet(self._sidebar_btn_style(active=False))
        sb_layout.addWidget(self.btn_main)
        sb_layout.addWidget(self.btn_logs)
        sb_layout.addStretch(1)
        main_hlayout.addWidget(sidebar)

        # Stacked content area
        self.stack = QStackedWidget()
        # Main file list page
        self.main_page = QWidget()
        main_page_layout = QVBoxLayout(self.main_page)
        main_page_layout.setContentsMargins(0, 0, 0, 0)
        main_page_layout.setSpacing(0)
        # Remove titlebar from here
        self.file_stack = AnimatedStackedWidget()
        self.file_stack.addWidget(self._create_onedrive_page())
        main_page_layout.addWidget(self.file_stack, 1)
        self.stack.addWidget(self.main_page)
        # Logs page
        self.logs_page = QWidget()
        logs_layout = QVBoxLayout(self.logs_page)
        logs_layout.setContentsMargins(24, 24, 24, 24)
        logs_layout.setSpacing(0)
        logs_label = QLabel("<b>Logs</b>")
        logs_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        logs_layout.addWidget(logs_label)
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet(
            "background: #f7f8fa; border-radius: 8px; font-size: 14px;"
        )
        self.logs_text.setText(
            "[INFO] App started\n[INFO] Ready for user actions\n[MOCK] This is a mock log entry."
        )
        logs_layout.addWidget(self.logs_text, 1)
        self.stack.addWidget(self.logs_page)
        main_hlayout.addWidget(self.stack, 1)

        main_vlayout.addLayout(main_hlayout, 1)

        # Sidebar button logic
        self.btn_main.clicked.connect(self._show_main_page)
        self.btn_logs.clicked.connect(self._show_logs_page)
        self.btn_main.installEventFilter(self)
        self.btn_logs.installEventFilter(self)

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
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.search.setFont(QFont("Segoe UI", 15))
        self.search.setStyleSheet(
            "border: none; background: transparent; padding: 8px;"
        )
        self.search.setMinimumWidth(340)
        sf_layout.addWidget(self.search)
        search_frame.setFixedHeight(44)
        layout.addWidget(search_frame)

        layout.addStretch(1)

        # Settings & maintenance icons
        for emoji in ("⚙️", "🛠️"):
            lbl = HoverLabel(emoji)
            lbl.setFont(QFont("Segoe UI Emoji", 38))
            layout.addWidget(lbl)
            layout.addSpacing(16)

        # Connect search bar to filter
        self.search.textChanged.connect(self._filter_files)

        return bar

    def _create_onedrive_page(self):
        page = QFrame()
        v = QVBoxLayout(page)
        v.setContentsMargins(64, 48, 64, 48)
        v.setSpacing(24)

        # Title and refresh/email button row
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
        self.refresh_btn.setFixedSize(160, 44)
        self.refresh_btn.setToolTip("Refresh file list")
        self.refresh_btn.clicked.connect(self._refresh_files)
        title_row.addWidget(self.refresh_btn)
        # Add the new 'Send email with recommendation' button
        self.email_all_btn = ActionButton(
            "✉️ Send email with recommendation",
            "border: none; font-size: 16px; color: #fff; background: #FF4B2B; border-radius: 8px; padding: 0 28px; font-weight: 700;",
            "border: none; font-size: 16px; color: #fff; background: #ff7b5a; border-radius: 8px; padding: 0 28px; font-weight: 700;",
        )
        self.email_all_btn.setMinimumWidth(280)
        self.email_all_btn.setFixedHeight(44)
        self.email_all_btn.setToolTip("Send email with recommendations for all files")
        self.email_all_btn.clicked.connect(self._send_email_all)
        title_row.addSpacing(18)
        title_row.addWidget(self.email_all_btn)
        v.addLayout(title_row)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(
            """
            QListWidget { background: #fff; border-radius: 18px; border: 1.5px solid #e5e7eb; }
            QScrollBar:vertical {
                background: #f5f6fa;
                width: 14px;
                margin: 0px 0px 0px 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #FF4B2B;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #f5f6fa;
                height: 14px;
                margin: 0px 0px 0px 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #FF4B2B;
                min-width: 30px;
                border-radius: 7px;
                border: 2px solid #FF4B2B;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QTableView {
                selection-background-color: #FF4B2B;
                selection-color: white;
            }
            QTableView::item:selected {
                background-color: #FF4B2B;
                color: white;
            }
            QTableView::item:focus {
                border: 1px solid #FF4B2B;
                outline: none;
            }
            """
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

    def _show_folder(self, folder_id=None, drive_id=None, force_refresh=False):
        self._all_files = []  # Store all files for filtering
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
            drive_id = root.get("driveId")
            self._nav_stack = [(folder_id, drive_id, "BenchHub")]
        self._current_folder_id = folder_id
        self._current_drive_id = drive_id
        # Use a worker thread for loading
        self._file_loader_thread = QThread()
        self._file_loader_worker = FileLoaderWorker(client, folder_id, drive_id)
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
        self._all_files = files or []  # Save for filtering
        if err:
            self.file_list.addItem(QListWidgetItem(f"Error: {err}"))
            return
        # Up-item
        if len(self._nav_stack) > 1:
            up = QListWidgetItem(".. (Up)")
            up.setData(Qt.UserRole, {"up": True})
            self.file_list.addItem(up)
        self._filter_files()  # Show filtered files (or all if no filter)

    def _filter_files(self):
        # Remove all items except the up-item (if present)
        up_item = None
        if self.file_list.count() > 0:
            first_item = self.file_list.item(0)
            if first_item.data(Qt.UserRole) and first_item.data(Qt.UserRole).get("up"):
                up_item = first_item
        self.file_list.clear()
        if up_item:
            self.file_list.addItem(up_item)
        query = self.search.text().strip().lower() if hasattr(self, "search") else ""
        for f in self._all_files:
            name = f.get("name", "").lower()
            creator = ""
            created_by = f.get("createdBy", {})
            if isinstance(created_by, dict):
                user = created_by.get("user", {})
                if isinstance(user, dict):
                    creator = (
                        user.get("displayName") or user.get("email") or ""
                    ).lower()
            # Only show folders and .xlsx files (as before)
            if "folder" in f or name.endswith(".xlsx"):
                if not query or query in name or query in creator:
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
                prev_id, prev_drive_id, _ = self._nav_stack[-1]
                self._show_folder(prev_id, prev_drive_id)
        elif "folder" in data:
            folder_id = data["id"]
            drive_id = (
                data.get("parentReference", {}).get("driveId") or self._current_drive_id
            )
            self._nav_stack.append((folder_id, drive_id, data["name"]))
            self._show_folder(folder_id, drive_id)

    def _on_preview(self, data):
        if "folder" in data or not data.get("name", "").lower().endswith(".xlsx"):
            QMessageBox.information(
                self, "Preview", "Only .xlsx files can be previewed."
            )
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Preview: {data['name']}")
        dlg.setMinimumSize(900, 600)
        vb = QVBoxLayout(dlg)
        lbl = QLabel(f"<b>Preview: {data['name']}</b>")
        vb.addWidget(lbl)
        prog = QProgressBar()
        prog.setRange(0, 0)
        vb.addWidget(prog)
        table_view = QTableView()
        table_view.setVisible(False)
        table_view.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        table_view.setVerticalScrollMode(QTableView.ScrollPerPixel)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        table_view.setSelectionMode(QTableView.SingleSelection)
        table_view.setAlternatingRowColors(True)
        # Custom scrollbar style
        scrollbar_style = """
            QScrollBar:vertical {
                background: #f5f6fa;
                width: 14px;
                margin: 0px 0px 0px 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #FF4B2B;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #f5f6fa;
                height: 14px;
                margin: 0px 0px 0px 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #FF4B2B;
                min-width: 30px;
                border-radius: 7px;
                border: 2px solid #FF4B2B;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QTableView {
                selection-background-color: #FF4B2B;
                selection-color: white;
            }
            QTableView::item:selected {
                background-color: #FF4B2B;
                color: white;
            }
            QTableView::item:focus {
                border: 1px solid #FF4B2B;
                outline: none;
            }
        """
        table_view.setStyleSheet(scrollbar_style)
        dlg.setStyleSheet(scrollbar_style)
        table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        vb.addWidget(table_view, 1)
        btn_row = QHBoxLayout()
        back = QPushButton("Back")
        back.clicked.connect(dlg.close)
        btn_row.addWidget(back)
        maximize_btn = QPushButton("Maximize")
        maximize_btn.setCheckable(True)
        btn_row.addWidget(maximize_btn)
        vb.addLayout(btn_row)

        def toggle_maximize():
            if maximize_btn.isChecked():
                dlg.showMaximized()
                maximize_btn.setText("Restore")
            else:
                dlg.showNormal()
                maximize_btn.setText("Maximize")

        maximize_btn.clicked.connect(toggle_maximize)

        def fetch():
            try:
                client = GraphAPIClient()
                # Use /drives/{drive_id}/items/{id}/content for shared files, /me/drive/items/{id}/content for personal
                drive_id = data.get("parentReference", {}).get("driveId") or data.get(
                    "driveId"
                )
                if drive_id:
                    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{data['id']}/content"
                else:
                    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{data['id']}/content"
                resp = requests.get(url, headers=client.headers)
                resp.raise_for_status()
                df = pd.read_excel(io.BytesIO(resp.content), engine="openpyxl")
                model = PandasTableModel(df, chunk_size=100)
                table_view.setModel(model)
                table_view.horizontalHeader().setSectionResizeMode(
                    QHeaderView.Interactive
                )
                table_view.resizeColumnsToContents()
                table_view.setVisible(True)
                prog.setVisible(False)

                # Infinite loading: connect to scroll event
                def on_scroll():
                    if (
                        model.canFetchMore()
                        and table_view.verticalScrollBar().value()
                        == table_view.verticalScrollBar().maximum()
                    ):
                        model.fetchMore()

                table_view.verticalScrollBar().valueChanged.connect(
                    lambda _: on_scroll()
                )
            except Exception as ex:
                lbl.setText(f"<span style='color:red'>Error: {ex}</span>")
                prog.setVisible(False)

        QTimer.singleShot(100, fetch)
        dlg.exec()

    def _send_email_all(self):
        # Mock sending email for all .xlsx files in the current list
        files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            data = item.data(Qt.UserRole)
            if (
                data
                and isinstance(data, dict)
                and "folder" not in data
                and data.get("name", "").lower().endswith(".xlsx")
            ):
                files.append(data["name"])
        if files:
            QMessageBox.information(
                self,
                "Mock Email",
                f"Would send recommendations for:\n\n" + "\n".join(files),
            )
        else:
            QMessageBox.information(
                self, "Mock Email", "No .xlsx files to send recommendations for."
            )

    def _show_main_page(self):
        self.btn_main.setChecked(True)
        self.btn_logs.setChecked(False)
        self.btn_main.setStyleSheet(self._sidebar_btn_style(active=True))
        self.btn_logs.setStyleSheet(self._sidebar_btn_style(active=False))
        self.stack.setCurrentWidget(self.main_page)

    def _show_logs_page(self):
        self.btn_main.setChecked(False)
        self.btn_logs.setChecked(True)
        self.btn_main.setStyleSheet(self._sidebar_btn_style(active=False))
        self.btn_logs.setStyleSheet(self._sidebar_btn_style(active=True))
        self.stack.setCurrentWidget(self.logs_page)
