import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Serving Agence Web Locale at http://localhost:{PORT}")
        print(f"📂 Output directory: {DIRECTORY}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")
