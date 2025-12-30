import csv
import json
import os
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VILLES_PATH = os.path.join(BASE_DIR, "villes.csv")
DEPARTEMENTS_PATH = os.path.join(BASE_DIR, "departements.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "../output/sitemap.xml")
BASE_URL = "https://agence-web-locale.fr"

def generate_sitemap():
    print("🌐 Generating Sitemap...")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    sitemap_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # 1. Homepage
    sitemap_content.append(f'  <url><loc>{BASE_URL}/</loc><lastmod>{current_date}</lastmod><priority>1.0</priority></url>')

    # 2. Departments Hubs
    if os.path.exists(DEPARTEMENTS_PATH):
        with open(DEPARTEMENTS_PATH, "r", encoding="utf-8") as f:
            depts = json.load(f)
            # Map name to slug for cities
            dept_name_to_slug = {d["nom"]: d["slug"] for d in depts}
            
            for d in depts:
                loc = f"{BASE_URL}/departement-{d['slug']}"
                sitemap_content.append(f'  <url><loc>{loc}</loc><lastmod>{current_date}</lastmod><priority>0.9</priority></url>')
    else:
        print("⚠️ Warning: departements.json not found.")

    # 3. Cities (Siloed)
    if os.path.exists(VILLES_PATH):
        with open(VILLES_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                slug = row.get("slug", "").strip().lower()
                dept_nom = row.get("departement_nom", "")
                dept_slug = dept_name_to_slug.get(dept_nom, "")
                
                if slug and dept_slug:
                    loc = f"{BASE_URL}/{dept_slug}/creation-site-internet-{slug}"
                    sitemap_content.append(f'  <url><loc>{loc}</loc><lastmod>{current_date}</lastmod><priority>0.8</priority></url>')
                    count += 1
            print(f"✅ Added {count} city URLs to sitemap.")
    else:
        print("⚠️ Warning: villes.csv not found.")

    sitemap_content.append('</urlset>')

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_content))
    
    print(f"🏁 Sitemap complete: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_sitemap()
