import csv
import os
import time
import json
import random
from datetime import datetime

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "../output")
VILLES_PATH = os.path.join(BASE_DIR, "villes.csv")
DEPARTEMENTS_PATH = os.path.join(BASE_DIR, "departements.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.html")

TEST_MODE = False  # Full generation enabled

# French female first names for gender detection
FEMALE_NAMES = {
    "julie", "marie", "sophie", "claire", "anne", "nathalie", "céline", "isabelle",
    "laurence", "sandrine", "valérie", "christine", "catherine", "patricia", "sylvie",
    "caroline", "virginie", "stéphanie", "émilie", "aurélie", "delphine", "florence",
    "béatrice", "véronique", "dominique", "martine", "françoise", "monique", "danielle",
    "michelle", "brigitte", "hélène", "jacqueline", "chantal", "nicole", "pauline",
    "camille", "margot", "léa", "emma", "chloé", "manon", "océane", "laura", "sarah",
    "amélie", "lucie", "mathilde", "alice", "jeanne", "charlotte", "juliette", "louise",
    "zoé", "inès", "lola", "jade", "léna", "clara", "eva", "lisa", "anna", "nina",
    "rose", "victoire", "agathe", "adèle", "clémence", "margaux", "marion", "elsa"
}

# French month names
FRENCH_MONTHS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

def slugify(text):
    text = str(text).lower().strip()
    replacements = [
        (" ", "-"), ("'", "-"), ("à", "a"), ("â", "a"), ("ä", "a"),
        ("é", "e"), ("è", "e"), ("ê", "e"), ("ë", "e"),
        ("î", "i"), ("ï", "i"), ("ô", "o"), ("ö", "o"),
        ("ù", "u"), ("û", "u"), ("ü", "u"), ("ç", "c"),
        ("œ", "oe"), ("æ", "ae")
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def is_female_name(name):
    """Check if a first name is typically female."""
    if not name:
        return False
    return name.lower().strip() in FEMALE_NAMES

def load_data():
    villes = []
    if not os.path.exists(VILLES_PATH):
        print(f"❌ File not found: {VILLES_PATH}")
        return villes
    csv.field_size_limit(1000000)
    with open(VILLES_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes.append(row)
    return villes

def normalize_row(row):
    """Map CSV headers to template variables."""
    normalized = row.copy()
    
    mappings = {
        "accroche_hero": "Accroche Hero",
        "sous_titre_hero": "Sous Titre Hero",
        "description_p1": "Description P1",
        "description_p2": "Description P2",
        "quartiers": "Quartiers",
        "fait_local": "Fait Local",
        "temoignage_texte": "Temoignage Texte",
        "temoignage_prenom": "Temoignage Prenom",
        "temoignage_metier": "Temoignage Metier",
        "temoignage_quartier": "Temoignage Quartier"
    }

    for key, source in mappings.items():
        if not normalized.get(key) and normalized.get(source):
            normalized[key] = normalized[source]
    
    # Also check "Prénom Aléatoire" as fallback for temoignage_prenom
    if not normalized.get("temoignage_prenom") and normalized.get("Prénom Aléatoire"):
        normalized["temoignage_prenom"] = normalized["Prénom Aléatoire"]
    
    # Check "Métier Aléatoire" as fallback for temoignage_metier
    if not normalized.get("temoignage_metier") and normalized.get("Métier Aléatoire"):
        normalized["temoignage_metier"] = normalized["Métier Aléatoire"]

    url_mappings = {
        "url_resto": "url_resto_complete",
        "url_artisan": "url_artisan_complete",
        "url_beaute": "url_beaute_complete",
        "url_immo": "url_immo_complete",
        "url_avocat": "url_avocat_complete",
        "url_sante": "url_sante_complete"
    }

    for key, source in url_mappings.items():
        if normalized.get(source):
            normalized[key] = normalized.get(source)

    return normalized

def generate_maillage_footer():
    """Generate footer links for all French departments."""
    try:
        with open(os.path.join(SOURCE_DIR, "departements.json"), "r", encoding="utf-8") as f:
            depts = json.load(f)
            links = []
            for d in depts:
                links.append(f'<a href="/departement/{d["slug"]}">{d["nom"]}</a>')
            return " ".join(links)
    except:
        return ""

def generate_site():
    print("🚀 Starting Generation (SEO MAX Mode)...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    villes = load_data()
    
    # Load departments for mapping
    with open(DEPARTEMENTS_PATH, "r", encoding="utf-8") as f:
        depts_data = json.load(f)
    dept_name_to_slug = {d["nom"]: d["slug"] for d in depts_data}

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    maillage_footer = generate_maillage_footer()

    if TEST_MODE:
        print("⚠️ TEST MODE: Generating only Toulouse...")
        target = next((v for v in villes if "Toulouse" in v.get("ville", "")), villes[0])
        villes = [target]

    count = 0
    sitemap_entries = []
    
    for v in villes:
        content = template
        v_normalized = normalize_row(v)
        replacements = v_normalized.copy()
        
        dept_nom = v_normalized.get("departement_nom", "")
        dept_slug = dept_name_to_slug.get(dept_nom, slugify(dept_nom))
        
        # Randomize stats (seeded by city for consistency)
        random.seed(v_normalized.get("ville", "default"))
        
        base_sites = int(v_normalized.get("nb_sites_realises") or 47)
        base_avis = int(v_normalized.get("nb_avis") or 127)
        
        replacements["nb_sites_realises"] = str(base_sites + random.randint(-5, 15))
        replacements["nb_avis"] = str(base_avis + random.randint(-10, 30))
        replacements["note_google"] = str(round(random.uniform(4.7, 5.0), 1))
        
        # Avatar - use UI Avatars (100% reliable, generates initials)
        prenom = v_normalized.get("temoignage_prenom", "Client")
        # UI Avatars generates colored initials - always works
        initials = prenom[:2].upper() if prenom else "CL"
        # Different background colors based on gender
        if is_female_name(prenom):
            bg_color = "e17055"  # Coral for female
        else:
            bg_color = "2c3e50"  # Dark blue for male
        replacements["avatar_url"] = f"https://ui-avatars.com/api/?name={prenom}&background={bg_color}&color=fff&size=150&font-size=0.4&bold=true"
        
        # Dynamic freshness: current month for "Dernier site livré"
        now = datetime.now()
        current_month = FRENCH_MONTHS[now.month]
        current_year = now.year
        
        replacements["mois_actuel"] = current_month
        replacements["annee_actuelle"] = str(current_year)
        replacements["dernier_site_mois"] = f"{current_month} {current_year}"
        
        # FOMO: Random but seeded values for scarcity
        random.seed(v_normalized.get("ville", "") + str(now.month))
        places_restantes = random.randint(2, 5)
        jours_prochain_creneau = random.randint(3, 12)
        
        replacements["places_restantes"] = str(places_restantes)
        replacements["prochain_creneau_jours"] = str(jours_prochain_creneau)
        
        # FAQ 6-10: SEO-optimized trust-building questions (as variables)
        ville = v_normalized.get("ville", "votre ville")
        
        replacements["faq_6_question"] = f"Le site m'appartient-il vraiment après création à {ville} ?"
        replacements["faq_6_reponse"] = f"Oui, à 100%. Contrairement aux plateformes de location comme Wix ou Squarespace, vous êtes propriétaire de votre nom de domaine et du code source. À {ville}, nous vous remettons tous les accès et fichiers sources à la fin du projet. Aucune dépendance."
        
        replacements["faq_7_question"] = "L'hébergement et le nom de domaine sont-ils inclus ?"
        replacements["faq_7_reponse"] = f"Tout est inclus dans le forfait mensuel : hébergement haute performance sur serveurs français, nom de domaine (.fr ou .com), certificat SSL (cadenas vert HTTPS), sauvegardes automatiques quotidiennes, et monitoring 24/7. Vous n'avez rien à gérer techniquement."
        
        replacements["faq_8_question"] = "Mon site sera-t-il vraiment adapté aux mobiles ?"
        replacements["faq_8_reponse"] = f"Absolument. En 2025, plus de 70% des recherches locales à {ville} se font sur smartphone. Nous appliquons une approche 'Mobile First' : votre site est conçu d'abord pour mobile, puis adapté aux tablettes et PC. Google privilégie les sites mobile-friendly dans ses résultats."
        
        replacements["faq_9_question"] = "Puis-je modifier le contenu de mon site moi-même ?"
        replacements["faq_9_reponse"] = "Oui, c'est vous qui décidez. Sur demande, nous intégrons un panneau d'administration simple et intuitif (type WordPress) qui vous permet de modifier vos horaires, ajouter des photos, publier des actualités ou créer des pages, sans toucher une ligne de code. Formation incluse."
        
        replacements["faq_10_question"] = "Y a-t-il des frais cachés ou des engagements ?"
        replacements["faq_10_reponse"] = f"Aucun frais caché, c'est notre engagement. Le devis est ferme et définitif. Le tarif mensuel couvre tout : hébergement, maintenance, support technique illimité, mises à jour de sécurité. Pas d'engagement longue durée, résiliable à tout moment avec préavis de 30 jours."
        
        # Computed variables
        replacements["slug_departement"] = dept_slug
        replacements["maillage_footer_france"] = maillage_footer
        replacements["timestamp_now"] = str(int(time.time()))
        replacements["year"] = "2025"
        
        # Apply all replacements
        for key, value in replacements.items():
            placeholder = "{{" + key + "}}"
            content = content.replace(placeholder, str(value))
            
        # Hierarchical Silo Structure: /output/dept-slug/creation-site-internet-ville-slug.html
        dept_dir = os.path.join(OUTPUT_DIR, dept_slug)
        if not os.path.exists(dept_dir):
            os.makedirs(dept_dir)
            
        filename = f"creation-site-internet-{v['slug']}.html"
        output_path = os.path.join(dept_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        # SEO URL structure: /dept_slug/creation-site-internet-ville_slug
        page_url = f"/{dept_slug}/creation-site-internet-{v['slug']}"
        sitemap_entries.append(f"https://agence-web-locale.fr{page_url}")
        count += 1

        if count % 100 == 0:
            print(f"✅ {count} pages generated...")

    # Generate Sitemap
    if not TEST_MODE:
        with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for url in sitemap_entries:
                f.write(f'  <url><loc>{url}</loc><lastmod>{datetime.today().strftime("%Y-%m-%d")}</lastmod></url>\n')
            f.write('</urlset>')

    print(f"🏁 Generation Complete! {count} pages in /output")
    print(f"👉 Test: http://localhost:8081/creation-site-internet-{villes[0]['slug']}.html")

if __name__ == "__main__":
    generate_site()
