#!/usr/bin/env python3
"""
Launcher script for k-method Antigravity 2.0 Webview GUI.
Binds to local TCP port, starts ASGI server, and opens default browser or native webview.
"""
import argparse
import os
import socket
import sys
import time
import urllib.request
import webbrowser
from dataclasses import dataclass
from typing import Optional, List

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@dataclass
class LauncherConfig:
    host: str
    port: int
    no_browser: bool


def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """
    Finds the first available local TCP port starting from start_port.
    """
    for offset in range(max_attempts):
        candidate_port = start_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", candidate_port))
                return candidate_port
            except OSError:
                continue
    return start_port


def parse_launcher_args(args: Optional[List[str]] = None) -> LauncherConfig:
    """
    Parses CLI launcher arguments.
    """
    parser = argparse.ArgumentParser(description="k-method app GUI Launcher")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Local bind address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Preferred TCP port (default: 8000, auto-finds next free if busy)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open the browser upon startup",
    )

    parsed = parser.parse_args(args if args is not None else sys.argv[1:])
    return LauncherConfig(
        host=parsed.host,
        port=parsed.port,
        no_browser=parsed.no_browser,
    )


def verify_server_health(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Pings the /api/status endpoint to check if the server is up and healthy.
    """
    url = f"http://{host}:{port}/api/status"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def run_gui(host: str = "127.0.0.1", preferred_port: int = 8000, no_browser: bool = False) -> int:
    """
    Launches uvicorn server and manages browser opening.
    """
    import uvicorn
    from scripts.harness.gui.server import app

    actual_port = find_available_port(preferred_port)
    url = f"http://{host}:{actual_port}"

    print("════════════════════════════════════════════════════════════════════")
    print("           🚀 k-method app - SDLC GRAPHICAL RUNNER                  ")
    print("════════════════════════════════════════════════════════════════════")
    print(f"  Servidor iniciado en: {url}")
    print("  Presiona Ctrl+C para detener el servidor.")
    print("════════════════════════════════════════════════════════════════════\n")

    if not no_browser:
        # Schedule browser launch after server spins up
        import threading

        def open_browser():
            time.sleep(0.8)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

    try:
        uvicorn.run(app, host=host, port=actual_port, log_level="warning")
        return 0
    except KeyboardInterrupt:
        print("\nServidor detenido limpiamente.")
        return 0


if __name__ == "__main__":
    cfg = parse_launcher_args()
    sys.exit(run_gui(host=cfg.host, preferred_port=cfg.port, no_browser=cfg.no_browser))
