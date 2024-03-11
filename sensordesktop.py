import threading
import webview
from sensor import app  # Import your Flask app

def run_flask():
    app.run()

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    webview.create_window('Sensor Data Dashboard', 'http://localhost:5000')
    webview.start()