"""
Desktop launcher for Scholaris Pro.
Starts Streamlit in background thread, then opens a native desktop window.
"""
import os
import sys
import time
import socket
import threading
from pathlib import Path


def base_dir() -> Path:
    """Get the base directory — works in dev AND PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


BASE = base_dir()


def find_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_streamlit(port: int):
    """Start Streamlit programmatically (no subprocess)."""
    app_file = BASE / "app.py"
    if not app_file.exists():
        raise FileNotFoundError(f"app.py not found at {app_file}")

    # Set environment variables
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

    # Use streamlit's internal CLI
    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit", "run", str(app_file),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
    ]
    stcli.main()


def wait_for_server(port: int, timeout: int = 60) -> bool:
    """Wait until Streamlit is ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def main():
    port = find_free_port()

    # Start Streamlit in background
    thread = threading.Thread(target=start_streamlit, args=(port,), daemon=True)
    thread.start()

    # Wait for server
    if not wait_for_server(port):
        print("❌ Streamlit failed to start within 60s")
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"

    # Try PyWebView for a native window
    try:
        import webview
        window = webview.create_window(
            title="Scholaris Pro — School Management ERP",
            url=url,
            width=1400,
            height=900,
            min_size=(1000, 700),
            resizable=True,
            text_select=True,
            confirm_close=True,
        )
        webview.start()
    except Exception as e:
        print(f"⚠️ PyWebView unavailable ({e}) — opening in browser")
        import webbrowser
        webbrowser.open(url)
        # Keep process alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()