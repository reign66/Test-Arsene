import json
import os
import datetime
import requests
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
STATE_FILE = os.path.join(BASE_DIR, "indexing_state.json")
SITEMAP_URL = "https://france-bal.fr/sitemap.xml"
DAILY_LIMIT = 199
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

SCOPES = ["https://www.googleapis.com/auth/indexing"]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"submitted": [], "last_run": "", "today_count": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_sitemap_urls():
    try:
        # Priority: Local relative to script
        path_output = os.path.join(BASE_DIR, "output/sitemap.xml")
        path_root = os.path.join(BASE_DIR, "../sitemap.xml")
        
        if os.path.exists(path_output):
            path = path_output
        elif os.path.exists(path_root):
            path = path_root
        elif os.path.exists("sitemap.xml"):
            path = "sitemap.xml"
        else:
            print("⚠️ Sitemap local introuvable, tentative de téléchargement...")
            response = requests.get(SITEMAP_URL)
            content = response.text
            path = None
        
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        
        urls = re.findall(r'<loc>(.*?)</loc>', content)
        return urls
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du sitemap : {e}")
        return []

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"❌ Erreur: Le fichier '{CLIENT_SECRET_FILE}' est manquant.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    
    return creds

def main():
    print("🚀 Démarrage du script d'indexation Google (Service de Bureau)...")
    
    state = load_state()
    today = datetime.date.today().isoformat()
    
    if state["last_run"] != today:
        state["last_run"] = today
        state["today_count"] = 0
        print("📅 Nouvelle journée détectée. Compteur remis à 0.")
    
    if state["today_count"] >= DAILY_LIMIT:
        print(f"🛑 Limite quotidienne atteinte ({state['today_count']}/{DAILY_LIMIT}). À demain !")
        return

    all_urls = get_sitemap_urls()
    if not all_urls:
        print("❌ Aucune URL trouvée.")
        return
        
    print(f"🔍 URLs trouvées : {len(all_urls)}")
    
    submitted_set = set(state["submitted"])
    to_submit = [u for u in all_urls if u not in submitted_set]
    
    print(f"📝 URLs restant à indexer : {len(to_submit)}")
    
    if not to_submit:
        print("✅ Toutes les URLs ont déjà été soumises !")
        return

    creds = get_credentials()
    if not creds:
        return

    count = 0
    quota_left = DAILY_LIMIT - state["today_count"]
    batch = to_submit[:quota_left]
    
    print(f"📤 Envoi de {len(batch)} URLs vers Google...")
    
    for url in batch:
        try:
            # Add auth to header
            headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}
            response = requests.post(ENDPOINT, json={
                "url": url,
                "type": "URL_UPDATED"
            }, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ OK: {url}")
                state["submitted"].append(url)
                state["today_count"] += 1
                count += 1
            elif response.status_code == 429:
                print("🛑 Quota Google atteint (429).")
                break
            elif response.status_code == 401:
                print("⚠️ Token expiré. Refreshing...")
                creds.refresh(Request())
                headers["Authorization"] = f"Bearer {creds.token}"
                # Retry once
                response = requests.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"}, headers=headers)
                if response.status_code == 200:
                    print(f"✅ OK (after refresh): {url}")
                    state["submitted"].append(url)
                    state["today_count"] += 1
                    count += 1
            else:
                print(f"❌ Erreur ({response.status_code}): {url} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception sur {url}: {e}")
            
    save_state(state)
    print(f"🏁 Terminé. {count} URLs soumises aujourd'hui. Total soumis : {len(state['submitted'])}/{len(all_urls)}")

if __name__ == "__main__":
    main()
