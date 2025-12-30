import http.server
import socketserver
import os

PORT = 8081
# Serve the output directory relative to this script
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🎉 Serving TEST on http://localhost:{PORT}")
        httpd.serve_forever()
except OSError:
    print(f"⚠️ Port {PORT} busy. Check if previous server is still running.")
