import csv
import os
import random
import json
import re
from datetime import datetime

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "../output/demos")
VILLES_PATH = os.path.join(BASE_DIR, "villes.csv")
DEMOS_SOURCE_DIR = os.path.join(BASE_DIR, "demos")

NICHES = {
    "restaurant": "restaurant.html",
    "artisan": "artisan.html",
    "avocat": "avocat.html",
    "immo": "immo.html",
    "beaute": "beaute.html",
    "sante": "sante.html"
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
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text

def extract_brand_from_url(url):
    """
    Extract brand name from URL like https://la-table-des-halles.sites-restaurants.fr
    Returns 'La Table des Halles'
    """
    if not url or "sites" not in str(url):
        return None
    
    match = re.search(r'https?://([^.]+)\.', str(url))
    if match:
        brand_slug = match.group(1)
        name = brand_slug.replace("-", " ").title()
        # Some French clean up
        name = name.replace("L ", "L'").replace("D ", "D'").replace("Du ", "du ").replace("De ", "de ")
        return name
    return None

def generate_random_siret(city_seed, dept_num="75"):
    random.seed(city_seed)
    num = "".join([str(random.randint(0, 9)) for _ in range(9)])
    nic = "".join([str(random.randint(0, 9)) for _ in range(5)])
    return f"{num} {nic}"

def generate_professional_data(row, niche):
    city = row.get("ville", "Paris")
    slug = row.get("slug", "paris")
    dept_nom = row.get("departement_nom", "Paris")
    seed = city + niche
    random.seed(seed)
    
    first_names = ["Marc-André", "Jean-Baptiste", "Lucie", "Aurélie", "Thomas", "Antoine", "Sophie", "Élodie", "Nicolas", "Benoit"]
    last_names = ["Valéry", "Moreau", "Lefebvre", "Roux", "Girard", "Petit", "Simon", "Bertrand", "Lauzier", "Gaillard"]
    
    owner = f"{random.choice(first_names)} {random.choice(last_names)}"
    phone = f"0{random.randint(1, 5)} {random.randint(40, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
    
    # Simple SIRET logic
    siret = generate_random_siret(seed)
    
    data = {
        "ville": city,
        "departement_nom": dept_nom,
        "demo_owner_name": owner,
        "demo_phone": phone,
        "demo_siret": siret,
        "demo_email": f"contact@{slugify(city)}-{niche}.fr",
        "demo_address": f"{random.randint(1, 150)} Boulevard de la République, {row.get('population', '75000')[:2]}000 {city}"
    }
    
    if niche == "avocat":
        data["demo_tva"] = f"FR {random.randint(10, 99)} {siret.split()[0]}"
    elif niche == "sante":
        data["demo_rpps"] = "".join([str(random.randint(0, 9)) for _ in range(11)])
        data["demo_tva"] = f"FR {random.randint(10, 99)} {siret.split()[0]}"
    elif niche == "artisan":
        data["demo_assurance"] = f"AXA-{random.randint(100000, 999999)}"
    elif niche == "immo":
        data["demo_carte_pro"] = f"CPI {random.randint(10, 99)}01 {random.randint(2018, 2024)} 000 0{random.randint(100, 999)}"
        
    return data

def generate_demos():
    print("🎨 Starting Ultimate Demo Generation...")
    
    # Load villes
    villes = []
    with open(VILLES_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes.append(row)
    
    # Load templates
    templates = {}
    for niche, filename in NICHES.items():
        path = os.path.join(DEMOS_SOURCE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                templates[niche] = f.read()
    
    # Load department slugs
    with open(os.path.join(BASE_DIR, "departements.json"), "r", encoding="utf-8") as f:
        depts_data = json.load(f)
    dept_name_to_slug = {d["nom"]: d["slug"] for d in depts_data}
    
    # Generate for each city
    count = 0
    
    # Mapping between niche key and CSV column prefix
    NICHE_TO_COL = {
        "restaurant": "resto",
        "artisan": "artisan",
        "avocat": "avocat",
        "immo": "immo",
        "beaute": "beaute",
        "sante": "sante"
    }
    
    for row in villes:
        city_slug = row.get("slug")
        dept_nom = row.get("departement_nom")
        dept_slug = dept_name_to_slug.get(dept_nom, slugify(dept_nom))
        
        for niche, template_content in templates.items():
            # Get brand name from CSV URL
            col_prefix = NICHE_TO_COL.get(niche, niche)
            url_col = f"url_{col_prefix}_complete"
            csv_url = row.get(url_col)
            brand_name = extract_brand_from_url(csv_url)
            
            if not brand_name:
                brand_name = f"{niche.title()} {row.get('ville')}"
            
            brand_slug = slugify(brand_name)
            
            # Prepare data
            data = generate_professional_data(row, niche)
            data["demo_brand_name"] = brand_name
            data["ville_slug"] = city_slug
            data["departement_slug"] = dept_slug
            data["quartiers"] = row.get("quartiers", "")
            data["fait_local"] = row.get("fait_local", "")
            
            # Split brand name for logo if possible
            parts = brand_name.split()
            if len(parts) > 1:
                data["demo_brand_main"] = parts[0].upper()
                data["demo_brand_sub"] = " ".join(parts[1:]).upper()
            else:
                data["demo_brand_main"] = brand_name.upper()
                data["demo_brand_sub"] = ""

            # Variables for template
            content = template_content
            for key, value in data.items():
                content = content.replace("{{" + key + "}}", str(value))
            
            # Output path
            # Strategy: /output/demos/[niche]/[brand-slug]/index.html
            target_dir = os.path.join(OUTPUT_DIR, niche, brand_slug)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(content)
            
            count += 1
            
        if count % 100 == 0:
            print(f"✅ {count} demo pages generated...")

    print(f"🏁 Generation Complete! {count} total demo pages in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_demos()
