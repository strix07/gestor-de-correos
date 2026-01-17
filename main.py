import os
import threading
import webview
from server.app import create_app

def start_server():
    app = create_app()
    app.run(port=5000, threaded=True, debug=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Create window
    webview.create_window('G-Thread Finder', 'http://127.0.0.1:5000', width=1200, height=800, resizable=True)
    webview.start(debug=False)
