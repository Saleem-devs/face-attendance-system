import subprocess
import sys
import os
import time
import socket
import webbrowser
from threading import Thread
import uvicorn
from uvicorn import Config, Server

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
BACKEND_PORT = 8000
DASHBOARD_URL = f"http://localhost:{BACKEND_PORT}"


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class BackendManager:
    def __init__(self):
        self.process = None
        self.port = BACKEND_PORT
        self._server = None
        self._thread = None

    def start(self):
        if self.process is not None:
            return True

        if is_port_in_use(self.port):
            print(f"Port {self.port} is already in use")
            return False

        try:
            if BASE_DIR not in sys.path:
                sys.path.insert(0, BASE_DIR)
            from backend.main import app

            config = Config(
                app=app,
                host="127.0.0.1",
                port=self.port,
                reload=False,
                log_level="info",
            )
            server = Server(config)
            self._server = server

            def run_server():
                try:
                    uvicorn.run(app, host="127.0.0.1", port=self.port, log_level="info")
                except Exception as e:
                    print(f"Uvicorn server failed: {e}")

            thread = Thread(target=run_server, daemon=True)
            thread.start()
            self._thread = thread

            for _ in range(40):
                if is_port_in_use(self.port):
                    time.sleep(0.25)
                    return True
                time.sleep(0.25)

            return False
        except Exception as e:
            import traceback

            error_msg = f"Failed to start backend: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False

    def stop(self):
        try:
            if self._server is not None:
                self._server.should_exit = True
            self._server = None
        except Exception:
            pass

    def open_dashboard(self):
        if not self.start():
            return False

        def open_browser():
            time.sleep(1)
            webbrowser.open(DASHBOARD_URL)

        Thread(target=open_browser, daemon=True).start()
        return True
