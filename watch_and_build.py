import time
import threading
import subprocess
import os
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_DIRS = ["src/"]  # Watch the whole src directory recursively
DEBOUNCE_SECONDS = 1.0  # Wait this long after last change before restarting


class DevServerHandler(FileSystemEventHandler):
    def __init__(self, start_app_callback):
        self._lock = threading.Lock()
        self._changed = False
        self._timer = None
        self._start_app_callback = start_app_callback

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".py"):
            with self._lock:
                self._changed = True
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._trigger_restart)
            self._timer.start()

    def _trigger_restart(self):
        with self._lock:
            if self._changed:
                print("Change detected. Restarting app...")
                self._start_app_callback()
                self._changed = False


def run_dev_server():
    app_process = None
    process_lock = threading.Lock()

    def start_app():
        nonlocal app_process
        with process_lock:
            if app_process and app_process.poll() is None:
                print("Stopping previous app instance...")
                if os.name == "nt":
                    app_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    app_process.terminate()
                try:
                    app_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    app_process.kill()
            print("Starting app: py src/main.py")
            app_process = subprocess.Popen(
                ["py", "src/main.py"],
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                ),
            )

    observer = Observer()
    handler = DevServerHandler(start_app)
    for d in WATCHED_DIRS:
        observer.schedule(handler, d, recursive=True)
    observer.start()
    print("Watching for changes in src/ ...")
    print("Starting app: py src/main.py")
    start_app()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping dev server...")
        observer.stop()
        with process_lock:
            if app_process and app_process.poll() is None:
                if os.name == "nt":
                    app_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    app_process.terminate()
                try:
                    app_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    app_process.kill()
    observer.join()


if __name__ == "__main__":
    run_dev_server()
