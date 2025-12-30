import csv
import json
import os
import re
import unicodedata

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "../output")
VILLES_PATH = os.path.join(BASE_DIR, "villes.csv")
DEPARTEMENTS_PATH = os.path.join(BASE_DIR, "departements.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_departement.html")

def slugify(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def load_data():
    villes = []
    if not os.path.exists(VILLES_PATH):
        print(f"❌ File not found: {VILLES_PATH}")
        return villes
    with open(VILLES_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes.append(row)
    return villes

def generate_departements():
    print("🚀 Starting Department Generation...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    villes = load_data()
    with open(DEPARTEMENTS_PATH, "r", encoding="utf-8") as f:
        depts_data = json.load(f)
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Group cities by department name
    dept_to_villes = {}
    for v in villes:
        d_nom = v.get("departement_nom")
        if d_nom:
            if d_nom not in dept_to_villes:
                dept_to_villes[d_nom] = []
            dept_to_villes[d_nom].append(v)

    count = 0
    for dept in depts_data:
        nom = dept["nom"]
        slug = dept["slug"]
        code = dept["code"]
        
        dept_villes = dept_to_villes.get(nom, [])
        if not dept_villes:
            continue
            
        # Sort cities by population or name (defaulting to name for consistency)
        dept_villes.sort(key=lambda x: x.get("ville", ""))
        
        villes_html = ""
        for v in dept_villes:
            # Important: Link to the SILO path /[dept_slug]/creation-site-internet-[ville_slug]
            city_url = f"/{slug}/creation-site-internet-{v['slug']}"
            villes_html += f'''
            <div class="city-card">
                <h3>{v['ville']}</h3>
                <p style="font-size:0.85rem; color:#636e72; margin-bottom:15px;">Expertise web locale pour {v.get('gentile', 'les professionnels')} de {v['ville']}.</p>
                <a href="{city_url}"><i data-lucide="external-link" size="16"></i> Voir l'offre</a>
            </div>
            '''

        replacements = {
            "departement_nom": nom,
            "departement_code": code,
            "villes_maillage": villes_html,
            "meta_title": f"Création de Site Internet en {nom} ({code}) | Agence Web Locale",
            "meta_description": f"Besoin d'un site web professionnel en {nom} ? Nous créons des sites optimisés pour les TPE et artisans de toutes les communes du département {code}.",
            "url_page": f"/departement/{slug}",
            "dept_slug": slug
        }

        content = template
        for key, value in replacements.items():
            placeholder = "{{" + key + "}}"
            content = content.replace(placeholder, str(value))
            
        # Write file as /departement/[slug]/index.html
        dept_hub_dir = os.path.join(OUTPUT_DIR, "departement", slug)
        if not os.path.exists(dept_hub_dir):
            os.makedirs(dept_hub_dir)
            
        output_path = os.path.join(dept_hub_dir, "index.html")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

    print(f"🏁 Department Generation Complete! {count} pages in /output")

if __name__ == "__main__":
    generate_departements()
