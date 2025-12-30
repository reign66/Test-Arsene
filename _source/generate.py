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

TEST_MODE = False  # Set to True for fast testing

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
    if not name: return False
    return name.lower().strip() in FEMALE_NAMES

def load_data():
    villes = []
    if not os.path.exists(VILLES_PATH): return villes
    csv.field_size_limit(1000000)
    with open(VILLES_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes.append(row)
    return villes

def normalize_row(row):
    normalized = row.copy()
    mappings = {
        "accroche_hero": "Accroche Hero",
        "sous_titre_hero": "Sous Titre Hero",
        "description_p1": "Description P1",
        "description_p2": "Description P2"
    }
    for key, source in mappings.items():
        if not normalized.get(key) and normalized.get(source):
            normalized[key] = normalized[source]
    
    url_mappings = {
        "url_resto": "sites-restaurants.fr",
        "url_artisan": "sitesartisans.fr",
        "url_beaute": "sites-beaute.fr",
        "url_immo": "sites-immobiliers.fr",
        "url_avocat": "sites-avocats.fr",
        "url_sante": "sites-sante.fr"
    }
    for key, domain in url_mappings.items():
        normalized[key] = f"https://{normalized.get('slug', 'demo')}.{domain}"
        
    return normalized

def generate_maillage_footer():
    try:
        with open(DEPARTEMENTS_PATH, "r", encoding="utf-8") as f:
            depts = json.load(f)
            links = [f'<a href="/departement/{d["slug"]}">{d["nom"]}</a>' for d in depts]
            return " ".join(links)
    except: return ""

def generate_schema(v, dept_slug, current_url):
    ville = v.get("ville", "votre ville")
    dept_nom = v.get("departement_nom", "")
    
    local_business = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": f"Agence Web Locale {ville}",
        "description": f"Agence de création de sites internet à {ville}. Expert en SEO et design web.",
        "url": f"https://agence-web-locale.fr{current_url}",
        "telephone": "+33123456789",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": ville,
            "addressRegion": dept_nom,
            "addressCountry": "FR"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "128"
        }
    }

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            { "@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://agence-web-locale.fr/" },
            { "@type": "ListItem", "position": 2, "name": dept_nom, "item": f"https://agence-web-locale.fr/departement/{dept_slug}" },
            { "@type": "ListItem", "position": 3, "name": ville, "item": f"https://agence-web-locale.fr{current_url}" }
        ]
    }

    return f"""<script type="application/ld+json">{json.dumps(local_business, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>"""

def generate_site():
    print("🚀 Starting Generation (Technical SEO Mode)...")
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    villes = load_data()
    with open(DEPARTEMENTS_PATH, "r", encoding="utf-8") as f:
        depts_data = json.load(f)
    dept_name_to_slug = {d["nom"]: d["slug"] for d in depts_data}
    
    cities_by_dept = {}
    for v in villes:
        d = v.get("departement_nom", "Autres")
        if d not in cities_by_dept: cities_by_dept[d] = []
        cities_by_dept[d].append(v)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    maillage_footer = generate_maillage_footer()
    if TEST_MODE: villes = villes[:5]

    count = 0
    sitemap_entries = []
    
    for v in villes:
        v_normalized = normalize_row(v)
        replacements = v_normalized.copy()
        dept_nom = v_normalized.get("departement_nom", "")
        dept_slug = dept_name_to_slug.get(dept_nom, slugify(dept_nom))
        page_url = f"/{dept_slug}/creation-site-internet-{v['slug']}"
        
        # SEO & Schema
        replacements["schema_json_ld"] = generate_schema(v, dept_slug, page_url)
        
        # Nearby Cities Maillage
        dept_villes = cities_by_dept.get(dept_nom, [])
        others = [ov for ov in dept_villes if ov['slug'] != v['slug']]
        random.seed(v['slug'])
        selected = random.sample(others, min(len(others), 12))
        replacements["villes_proches_html"] = " ".join([f'<a href="/{dept_slug}/creation-site-internet-{ov["slug"]}">{ov["ville"]}</a>' for ov in selected])

        # Dynamic Stats
        random.seed(v['slug'] + "stats")
        replacements["nb_sites_realises"] = str(random.randint(45, 85))
        replacements["nb_avis"] = str(random.randint(110, 160))
        replacements["note_google"] = str(round(random.uniform(4.8, 5.0), 1))
        replacements["delai_jours"] = str(random.randint(7, 15))

        # Freshness
        now = datetime.now()
        replacements["mois_actuel"] = FRENCH_MONTHS[now.month]
        replacements["annee_actuelle"] = str(now.year)
        replacements["dernier_site_mois"] = f"{FRENCH_MONTHS[now.month]} {now.year}"
        
        # UI Avatars
        prenom = v_normalized.get("Prénom Aléatoire", "Marie")
        bg = "e17055" if is_female_name(prenom) else "2c3e50"
        replacements["avatar_url"] = f"https://ui-avatars.com/api/?name={prenom}&background={bg}&color=fff&size=150&bold=true"
        replacements["temoignage_prenom"] = prenom
        replacements["temoignage_metier"] = v_normalized.get("Métier Aléatoire", "Gérant")

        # FOMO
        random.seed(v['slug'] + str(now.month))
        replacements["places_restantes"] = str(random.randint(2, 4))

        # Defaults for others
        replacements["url_page"] = page_url
        replacements["slug_departement"] = dept_slug
        replacements["maillage_footer_france"] = maillage_footer
        replacements["year"] = str(now.year)
        
        # FAQ Titles
        ville = v.get("ville", "votre ville")
        replacements["h1_page"] = f"Création Site Internet à {ville}"
        replacements["meta_title"] = f"Agence Web {ville} - Création Site Internet & SEO"
        replacements["meta_description"] = f"Besoin d'un site internet à {ville} ? Notre agence web crée votre site vitrine ou e-commerce optimisé SEO. Devis gratuit."
        
        replacements["faq_6_question"] = f"Quel est le prix d'un site à {ville} ?"
        replacements["faq_6_reponse"] = "Nos tarifs débutent à 49€/mois sans frais de création. C'est une solution tout-inclus pour les entreprises locales."
        replacements["faq_7_question"] = "Le site est-il optimisé pour Google ?"
        replacements["faq_7_reponse"] = f"Oui, chaque site créé à {ville} bénéficie d'une optimisation technique SEO complète pour apparaître en haut des résultats."
        replacements["faq_8_question"] = "Proposez-vous une maintenance ?"
        replacements["faq_8_reponse"] = "Absolument. La maintenance, l'hébergement et les mises à jour de sécurité sont incluses dans tous nos forfaits."
        replacements["faq_9_question"] = "Puis-je modifier mon site moi-même ?"
        replacements["faq_9_reponse"] = "Oui, vous disposez d'un accès administrateur pour modifier vos textes et photos en toute autonomie."
        replacements["faq_10_question"] = "Quels sont les délais de création ?"
        replacements["faq_10_reponse"] = "En moyenne, votre site est mis en ligne sous 10 à 15 jours après validation de la maquette."

        content = template
        for key, val in replacements.items():
            content = content.replace("{{" + key + "}}", str(val))
            
        dept_dir = os.path.join(OUTPUT_DIR, dept_slug)
        if not os.path.exists(dept_dir): os.makedirs(dept_dir)
        with open(os.path.join(dept_dir, f"creation-site-internet-{v['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(content)
            
        sitemap_entries.append(f"https://agence-web-locale.fr{page_url}")
        count += 1
        if count % 100 == 0: print(f"✅ {count} pages...")

    # Sitemap
    if not TEST_MODE:
        with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for url in sitemap_entries:
                f.write(f'  <url><loc>{url}</loc><lastmod>{now.strftime("%Y-%m-%d")}</lastmod></url>\n')
            f.write('</urlset>')

    print(f"🏁 Done! {count} pages.")

if __name__ == "__main__":
    generate_site()
