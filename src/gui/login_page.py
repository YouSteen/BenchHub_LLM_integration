import sys
import os
import msal
import requests
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QProgressBar,
    QApplication,
)
from PySide6.QtCore import Qt, Signal, QThread, QObject
import threading
import webbrowser

# --- MSAL/Graph/Whitelist config from a.py ---
CLIENT_ID = "2925c5fe-f4fd-4edb-99d1-4d2f703f0d1b"
AUTHORITY = "https://login.microsoftonline.com/0b3fc178-b730-4e8b-9843-e81259237b77"
SCOPES = [
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Files.Read",
    "https://graph.microsoft.com/Sites.Read.All",
]
DRIVE_ID = "b!S3Prhw2hHEWn7UN03_Oi2pBIKGHXwCNBuVM5m2H-ypjYLZcF2dGNQKT5LKlLzomK"
FILE_ID = "01S7UWZMWGQC7CVHLXMBAY7JS3KJKSQHW7"
WHITELIST_BROWSER_LINK = (
    "https://endava-my.sharepoint.com/:t:/g/personal/"
    "andrei_vataselu_endava_com/EcaAviqdd2BBj6ZbUlUoHt8B-wv4_u2zPdAJ3eKmuHgSyg"
    "?e=bMKaSo"
)

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


def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(self._default_style())
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._default_style())
        super().leaveEvent(event)

    def _default_style(self):
        return "QPushButton {background: #1138f5; color: #fff; border-radius: 8px; padding: 12px 32px; font-size: 17px; font-weight: 600;}"

    def _hover_style(self):
        return "QPushButton {background: #0a2e8c; color: #fff; border-radius: 8px; padding: 12px 32px; font-size: 17px; font-weight: 600;}"


class LoginWorker(QObject):
    finished = Signal(dict, str)

    def __init__(self):
        super().__init__()

    def run(self):
        print(
            "[DEBUG][LoginWorker.run] Current thread:", threading.current_thread().name
        )
        try:
            cache = load_cache()
            app = msal.PublicClientApplication(
                client_id=CLIENT_ID, authority=AUTHORITY, token_cache=cache
            )
            # Try IWA first
            try:
                result = app.acquire_token_by_integrated_windows_auth(scopes=SCOPES)
            except Exception as e:
                result = None
            if not result or "access_token" not in result:
                result = app.acquire_token_interactive(scopes=SCOPES)
            if "access_token" not in result:
                self.finished.emit({}, result.get("error_description", "Unknown error"))
                return
            save_cache(cache)
            token = result["access_token"]
            email = result.get("id_token_claims", {}).get("preferred_username")
            if not token or not email:
                self.finished.emit({}, "[SECURITY] ❌ Token sau email lipsă.")
                return
            self.finished.emit({"access_token": token, "email": email}, "")
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.finished.emit(
                {}, f"<span style='color:#b00020'><b>Error:</b> {e}</span>"
            )


class LoginPage(QWidget):
    code_ready = Signal(str, str)
    status_ready = Signal(str)
    login_success = Signal()

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.flow = None
        self.app = None
        self.cache = None
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel("<h1>Sign in to your account</h1>")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        self.login_btn = HoverButton("Login with Microsoft")
        self.login_btn.clicked.connect(self.do_login)
        self.login_btn.setFixedWidth(320)  # or whatever width you prefer
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.code_label = QLabel("")
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.code_label)
        self.open_browser_btn = HoverButton("Open Microsoft Login Page")
        self.open_browser_btn.setVisible(False)
        self.open_browser_btn.clicked.connect(self.open_browser)
        layout.addWidget(self.open_browser_btn)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        self.code_ready.connect(self._show_code_ui)
        self.status_ready.connect(self._show_status)
        self.login_success.connect(self._show_main)

    def validate_onedrive_access(self, token: str) -> bool:
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me/drive/root",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"[DEBUG] Verificare OneDrive: {resp.status_code}")
        return resp.status_code == 200

    def fetch_whitelist(self, token: str) -> list:
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_ID}/content"
        print(f"[DEBUG] Acces whitelist din cloud: {url}")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"}
        )
        if resp.status_code == 200:
            users = [l.strip().lower().replace(".", "") for l in resp.text.splitlines()]
            print(f"[DEBUG] Whitelist cloud: {users}")
            return users
        if resp.status_code == 403:
            print("[SECURITY] ❌ Acces blocat (403) la whitelist.")
            print("📎 Deschide fișierul în browser o dată:")
            print(f"🔗 {WHITELIST_BROWSER_LINK}")
            webbrowser.open(WHITELIST_BROWSER_LINK)
            return []
        print(f"[SECURITY] ⚠️ Eroare la fetch whitelist: {resp.status_code}")
        return []

    def is_allowed(self, user_part: str, token: str) -> bool:
        wl = self.fetch_whitelist(token)
        normalized = user_part.lower().replace(".", "")
        print(f"[DEBUG] Validare user: {normalized}")
        return normalized in wl

    def do_login(self):
        self._show_status("")
        self.login_btn.setEnabled(False)
        self.loading_bar.setVisible(True)
        self.thread = QThread()
        self.worker = LoginWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_login_finished)
import sys
import os
import msal
import requests
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QProgressBar,
    QApplication,
)
from PySide6.QtCore import Qt, Signal, QThread, QObject
import threading
import webbrowser

# --- MSAL/Graph/Whitelist config from a.py ---
CLIENT_ID = "2925c5fe-f4fd-4edb-99d1-4d2f703f0d1b"
AUTHORITY = "https://login.microsoftonline.com/0b3fc178-b730-4e8b-9843-e81259237b77"
SCOPES = [
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Files.Read",
    "https://graph.microsoft.com/Sites.Read.All",
]
DRIVE_ID = "b!S3Prhw2hHEWn7UN03_Oi2pBIKGHXwCNBuVM5m2H-ypjYLZcF2dGNQKT5LKlLzomK"
FILE_ID = "01S7UWZMWGQC7CVHLXMBAY7JS3KJKSQHW7"
WHITELIST_BROWSER_LINK = (
    "https://endava-my.sharepoint.com/:t:/g/personal/"
    "andrei_vataselu_endava_com/EcaAviqdd2BBj6ZbUlUoHt8B-wv4_u2zPdAJ3eKmuHgSyg"
    "?e=bMKaSo"
)

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


def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(self._default_style())
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._default_style())
        super().leaveEvent(event)

    def _default_style(self):
        return "QPushButton {background: #1138f5; color: #fff; border-radius: 8px; padding: 12px 32px; font-size: 17px; font-weight: 600;}"

    def _hover_style(self):
        return "QPushButton {background: #0a2e8c; color: #fff; border-radius: 8px; padding: 12px 32px; font-size: 17px; font-weight: 600;}"


class LoginWorker(QObject):
    finished = Signal(dict, str)

    def __init__(self):
        super().__init__()

    def run(self):
        print(
            "[DEBUG][LoginWorker.run] Current thread:", threading.current_thread().name
        )
        try:
            cache = load_cache()
            app = msal.PublicClientApplication(
                client_id=CLIENT_ID, authority=AUTHORITY, token_cache=cache
            )
            # Try IWA first
            try:
                result = app.acquire_token_by_integrated_windows_auth(scopes=SCOPES)
            except Exception as e:
                result = None
            if not result or "access_token" not in result:
                result = app.acquire_token_interactive(scopes=SCOPES)
            if "access_token" not in result:
                self.finished.emit({}, result.get("error_description", "Unknown error"))
                return
            save_cache(cache)
            token = result["access_token"]
            email = result.get("id_token_claims", {}).get("preferred_username")
            if not token or not email:
                self.finished.emit({}, "[SECURITY] ❌ Token sau email lipsă.")
                return
            self.finished.emit({"access_token": token, "email": email}, "")
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.finished.emit(
                {}, f"<span style='color:#b00020'><b>Error:</b> {e}</span>"
            )


class LoginPage(QWidget):
    code_ready = Signal(str, str)
    status_ready = Signal(str)
    login_success = Signal()

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.flow = None
        self.app = None
        self.cache = None
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel("<h1>Sign in to your account</h1>")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        self.login_btn = HoverButton("Login with Microsoft")
        self.login_btn.clicked.connect(self.do_login)
        self.login_btn.setFixedWidth(320)  # or whatever width you prefer
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.code_label = QLabel("")
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.code_label)
        self.open_browser_btn = HoverButton("Open Microsoft Login Page")
        self.open_browser_btn.setVisible(False)
        self.open_browser_btn.clicked.connect(self.open_browser)
        layout.addWidget(self.open_browser_btn)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        self.code_ready.connect(self._show_code_ui)
        self.status_ready.connect(self._show_status)
        self.login_success.connect(self._show_main)

    def validate_onedrive_access(self, token: str) -> bool:
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me/drive/root",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"[DEBUG] Verificare OneDrive: {resp.status_code}")
        return resp.status_code == 200

    def fetch_whitelist(self, token: str) -> list:
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_ID}/content"
        print(f"[DEBUG] Acces whitelist din cloud: {url}")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"}
        )
        if resp.status_code == 200:
            users = [l.strip().lower().replace(".", "") for l in resp.text.splitlines()]
            print(f"[DEBUG] Whitelist cloud: {users}")
            return users
        if resp.status_code == 403:
            print("[SECURITY] ❌ Acces blocat (403) la whitelist.")
            print("📎 Deschide fișierul în browser o dată:")
            print(f"🔗 {WHITELIST_BROWSER_LINK}")
            webbrowser.open(WHITELIST_BROWSER_LINK)
            return []
        print(f"[SECURITY] ⚠️ Eroare la fetch whitelist: {resp.status_code}")
        return []

    def is_allowed(self, user_part: str, token: str) -> bool:
        wl = self.fetch_whitelist(token)
        normalized = user_part.lower().replace(".", "")
        print(f"[DEBUG] Validare user: {normalized}")
        return normalized in wl

    def do_login(self):
        self._show_status("")
        self.login_btn.setEnabled(False)
        self.loading_bar.setVisible(True)
        self.thread = QThread()
        self.worker = LoginWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_login_finished)