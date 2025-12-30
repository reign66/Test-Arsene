import http.server
import socketserver
import os
import subprocess
import sys
from email.message import Message
import io

# Agence Web Locale - Dashboard (Python 3.13+ Compatible, No-dependency)
PORT = 8080
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agence Web Locale - Dashboard</title>
    <style>
        :root { --primary: #2c3e50; --secondary: #e17055; --bg: #f8f5f2; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--primary); display: flex; justify-content: center; align-items: center; height: 100vh; margin:0; }
        .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 100%; }
        h1 { margin-bottom: 24px; font-size: 1.5rem; }
        .upload-area { border: 2px dashed #cbd5e0; padding: 30px; border-radius: 12px; margin-bottom: 24px; cursor: pointer; transition: 0.3s; display: block; }
        .upload-area:hover { border-color: var(--secondary); background: #fffaf0; }
        input[type="file"] { display: none; }
        .btn { background: var(--secondary); color: white; padding: 12px 24px; border-radius: 8px; font-weight: 700; text-decoration: none; display: inline-block; cursor: pointer; border: none; width: 100%; font-size: 1rem; }
        .btn:hover { background: #d35400; transform: translateY(-2px); }
        .status { margin-top: 20px; font-size: 0.9rem; color: #718096; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Dashboard Agence Web</h1>
        <p>Déposez votre fichier <strong>.csv</strong> ici.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label class="upload-area">
                <span id="file-label">Cliquez pour choisir le CSV</span>
                <input type="file" name="file" accept=".csv" onchange="updateLabel(this)" required>
            </label>
            <button type="submit" class="btn">Analyser & Générer</button>
        </form>
        <div class="status" id="status">Prêt pour l'analyse.</div>
    </div>
    <script>
        function updateLabel(input) {
            const label = document.getElementById('file-label');
            if (input.files.length > 0) {
                label.innerText = input.files[0].name;
                label.style.color = "#e17055";
                label.style.fontWeight = "bold";
            }
        }
    </script>
</body>
</html>
"""

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(UPLOAD_PAGE.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type')
                if not content_type or 'multipart/form-data' not in content_type:
                    self.send_error(400, "Bad Request: Content-Type must be multipart/form-data")
                    return

                boundary = content_type.split("boundary=")[1].encode()
                content_length = int(self.headers.get('Content-Length'))
                body = self.rfile.read(content_length)

                # Split parts by boundary
                parts = body.split(b'--' + boundary)
                file_content = None
                
                for part in parts:
                    if b'filename=' in part:
                        # Extract headers and body of the part
                        header_end = part.find(b'\r\n\r\n')
                        if header_end != -1:
                            file_content = part[header_end+4:].rstrip(b'\r\n--')
                            break

                if file_content:
                    upload_path = os.path.join(SOURCE_DIR, "villes.csv")
                    with open(upload_path, 'wb') as f:
                        f.write(file_content)
                    print(f"✅ CSV enregistré avec succès.")

                    # Try to run generation (just one example first if needed, but here we run full for simplicity in this script)
                    # We will modify generate.py later to just do a test if preferred.
                    subprocess.run([sys.executable, os.path.join(SOURCE_DIR, "csv_to_json.py")], check=True)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1 style='color:green'>Fichier recu !</h1><p>Analyse en cours... revenez sur le chat Gemini.</p></body></html>")
                else:
                    self.send_error(400, "Aucun fichier trouve dans le formulaire.")

            except Exception as e:
                self.send_error(500, f"Erreur serveur: {str(e)}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🎉 Dashboard lance sur http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Arret.")
