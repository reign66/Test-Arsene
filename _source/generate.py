import json
import os
import re
from datetime import datetime

# Agence Web Locale - Mass Site Generator (Anty Edition)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def generate_site():
    source_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(source_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Load Configs
    with open(os.path.join(source_dir, "config.json"), "r") as f:
        config = json.load(f)
    with open(os.path.join(source_dir, "departements.json"), "r") as f:
        depts = json.load(f)
    
    # Try to load villes.json (either user provided or dummy for test)
    villes_path = os.path.join(source_dir, "villes.json")
    if not os.path.exists(villes_path):
        print("⚠️ villes.json not found. Creating dummy data for testing...")
        # Creation of dummy data for demonstration if not provided
        villes = [
            {
                "ville": "Paris", "slug": "paris", "code_postal": "75000", "departement_nom": "Paris", "departement_code": "75",
                "meta_title": "Création Site Internet Paris | 0€ + 150€/mois | Agence Web",
                "meta_description": "Agence web à Paris. Création site internet pour TPE/PME Parisiens.",
                "h1_page": "Création de Site Internet à Paris", "url_page": "/creation-site-internet-paris",
                "prix_mensuel": "150", "code_promo": "PARIS", "reduction_pct": "10", "gentile": "Parisiens",
                "note_google": "4.9", "nb_avis": "250", "nb_sites_realises": "120", "delai_jours": "14",
                "accroche_hero": "Paris, capitale de l'innovation et du business.",
                "sous_titre_hero": "Boostez votre visibilité dans la Ville Lumière.",
                "description_p1": "Paris est le coeur battant de l'économie française...", "description_p2": "Notre agence vous accompagne dans tous les arrondissements...",
                "fait_local": "Paris abrite plus de 500 000 entreprises.", "quartiers": "Le Marais, Montmartre, Bastille, 8ème, 15ème",
                "temoignage_texte": "Un service irréprochable et un site qui convertit !", "temoignage_prenom": "Jean", "temoignage_metier": "Artisan", "temoignage_quartier": "11ème",
                "fa1_question": "Prix ?", "fa1_reponse": "0€ + 150€/mois.",
                "fa2_question": "Délai ?", "fa2_reponse": "14 jours.",
                "fa3_question": "Local ?", "fa3_reponse": "Oui, 100% français.",
                "fa4_question": "SEO ?", "fa4_reponse": "Inclus et optimisé.",
                "fa5_question": "Support ?", "fa5_reponse": "Illimité.",
                "commune_proche_1": "Boulogne-Billancourt", "slug_proche_1": "boulogne-billancourt",
                "commune_proche_2": "Neuilly-sur-Seine", "slug_proche_2": "neuilly-sur-seine",
                "commune_proche_3": "Saint-Ouen", "slug_proche_3": "saint-ouen",
                "url_resto_complete": "#", "url_artisan_complete": "#", "url_beaute_complete": "#", "url_immo_complete": "#", "url_avocat_complete": "#", "url_sante_complete": "#"
            }
        ]
    else:
        with open(villes_path, "r") as f:
            villes = json.load(f)

    # Load Template
    with open(os.path.join(source_dir, "template.html"), "r") as f:
        template = f.read()

    # Pre-generate Massive Footer Maillage (all depts)
    maillage_all_depts = ""
    for d in depts:
        maillage_all_depts += f'<a href="/departement-{d["slug"]}">{d["nom"]} ({d["code"]})</a> '

    # Group villes by department for local maillage
    villes_by_dept = {}
    for v in villes:
        d_code = v.get("departement_code")
        if d_code not in villes_by_dept: villes_by_dept[d_code] = []
        villes_by_dept[d_code].append(v)

    # Generation Loop
    count = 0
    sitemap_entries = []
    today = datetime.now().strftime("%Y-%m-%d")

    for v in villes:
        content = template
        
        # Local maillage for this dept
        d_code = v.get("departement_code")
        local_villes = villes_by_dept.get(d_code, [])
        maillage_dept = ""
        for lv in local_villes[:20]: # Limit to 20
            if lv["slug"] != v["slug"]:
                maillage_dept += f'<a href="/creation-site-internet-{lv["slug"]}">Expert Web {lv["ville"]}</a>'

        # Global Replacements from config
        replacements = {
            "{{domain}}": config["domain"],
            "{{base_path}}": config["base_path"],
            "{{phone}}": config["contact"]["phone"],
            "{{email}}": config["contact"]["email"],
            "{{year}}": str(config["year"]),
            "{{date_modified}}": today,
            "{{maillage_all_depts}}": maillage_all_depts,
            "{{maillage_dept}}": maillage_dept,
            "{{departement_slug}}": slugify(v.get("departement_nom", ""))
        }

        # City specific replacements
        for key, value in v.items():
            replacements[f"{{{{{key}}}}}"] = str(value)

        # Apply all
        for k, val in replacements.items():
            content = content.replace(k, val)

        # Output file
        filename = f"creation-site-internet-{v['slug']}.html"
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(content)

        sitemap_entries.append(f"https://{config['domain']}{v['url_page']}")
        
        count += 1
        if count % 100 == 0:
            print(f"✅ {count} pages generated...")

    # Generate Sitemap.xml
    with open(os.path.join(output_dir, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in sitemap_entries:
            f.write(f'  <url><loc>{url}</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>\n')
        f.write('</urlset>')

    print(f"🏁 Generation complete. {count} pages in /output.")

if __name__ == "__main__":
    generate_site()
