import subprocess
import sys
import os
import time
import socket
import webbrowser
from threading import Thread

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PORT = 8000
DASHBOARD_URL = f"http://localhost:{BACKEND_PORT}"


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class BackendManager:
    def __init__(self):
        self.process = None
        self.port = BACKEND_PORT

    def start(self):
        if self.process is not None:
            return True

        if is_port_in_use(self.port):
            print(f"Port {self.port} is already in use")
            return False

        try:
            backend_path = os.path.join(BASE_DIR, "backend")
            python_exe = sys.executable

            self.process = subprocess.Popen(
                [
                    python_exe,
                    "-m",
                    "uvicorn",
                    "backend.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(self.port),
                ],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                ),
            )

            for _ in range(30):
                if is_port_in_use(self.port):
                    time.sleep(0.5)
                    return True
                if self.process.poll() is not None:
                    return False
                time.sleep(0.5)

            return False
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return False

    def stop(self):
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
            finally:
                self.process = None

    def open_dashboard(self):
        if not self.start():
            return False

        def open_browser():
            time.sleep(1)
            webbrowser.open(DASHBOARD_URL)

        Thread(target=open_browser, daemon=True).start()
        return True
