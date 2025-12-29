import http.server
import socketserver
import os
import shutil
import cgi
import subprocess
import sys

# Agence Web Locale - Dashboard (No-dependency Edition)
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
        .upload-area { border: 2px dashed #cbd5e0; padding: 30px; border-radius: 12px; margin-bottom: 24px; cursor: pointer; transition: 0.3s; }
        .upload-area:hover { border-color: var(--secondary); background: #fffaf0; }
        input[type="file"] { display: none; }
        .btn { background: var(--secondary); color: white; padding: 12px 24px; border-radius: 8px; font-weight: 700; text-decoration: none; display: inline-block; cursor: pointer; border: none; width: 100%; }
        .btn:hover { background: #d35400; transform: translateY(-2px); }
        .status { margin-top: 20px; font-size: 0.9rem; color: #718096; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Générateur Agence Web</h1>
        <p>Déposez votre fichier <strong>villes.csv</strong> pour lancer la génération.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label class="upload-area" id="drop-area">
                <span id="file-label">Cliquez ou glissez le CSV ici</span>
                <input type="file" name="file" accept=".csv" onchange="updateLabel(this)" required>
            </label>
            <button type="submit" class="btn">Générer le Site</button>
        </form>
        <div class="status" id="status">En attente de fichier...</div>
    </div>
    <script>
        function updateLabel(input) {
            const label = document.getElementById('file-label');
            const status = document.getElementById('status');
            if (input.files.length > 0) {
                label.innerText = input.files[0].name;
                status.innerText = "Fichier prêt pour la génération !";
                status.style.color = "#27ae60";
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
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            if 'file' in form:
                file_item = form['file']
                if file_item.filename:
                    # Save the uploaded file as villes.csv
                    upload_path = os.path.join(SOURCE_DIR, "villes.csv")
                    with open(upload_path, 'wb') as f:
                        f.write(file_item.file.read())
                    
                    print(f"📂 Fichier {file_item.filename} reçu et enregistré en tant que villes.csv")

                    # Trigger scripts
                    try:
                        print("⚙️ Lancement de csv_to_json.py...")
                        subprocess.run([sys.executable, os.path.join(SOURCE_DIR, "csv_to_json.py")], check=True)
                        
                        print("⚙️ Lancement de generate.py...")
                        subprocess.run([sys.executable, os.path.join(SOURCE_DIR, "generate.py")], check=True)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        success_html = """
                        <html><body style="font-family:sans-serif; text-align:center; padding-top:100px;">
                            <h1 style="color:#27ae60">✅ Génération terminée avec succès !</h1>
                            <p>Toutes les pages ont été générées dans le dossier <code>output/</code>.</p>
                            <a href="/" style="color:#e17055; text-decoration:none; font-weight:bold;">← Retour au dashboard</a>
                            <br><br>
                            <p>Vous pouvez prévisualiser le site sur <code>http://localhost:8000</code></p>
                        </body></html>
                        """
                        self.wfile.write(success_html.encode('utf-8'))
                    except Exception as e:
                        self.send_error(500, f"Erreur lors de la génération: {str(e)}")
                else:
                    self.send_error(400, "Aucun fichier sélectionné.")
            else:
                self.send_error(400, "Champ 'file' manquant.")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🎉 Dashboard Agence Web lancé sur http://localhost:{PORT}")
        print(f"👉 Déposez votre CSV ici pour tout automatiser.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Dashboard arrêté.")
