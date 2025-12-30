import csv
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VILLES_PATH = os.path.join(BASE_DIR, "villes.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "../output/sitemaps")

NICHES = {
    "restaurant": "sites-restaurants.fr",
    "artisan": "sitesartisans.fr",
    "beaute": "sites-beaute.fr",
    "immo": "sites-immobiliers.fr",
    "avocat": "sites-avocats.fr",
    "sante": "sites-sante.fr"
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

def extract_brand_from_url(url):
    if not url: return None
    try:
        brand = url.split('/')[-1].replace('-link', '').replace('link', '')
        return brand if brand else None
    except: return None

def generate_niche_sitemaps():
    print("🌐 Generating Niche Sitemaps...")
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    villes = []
    with open(VILLES_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            villes.append(row)

    NICHE_TO_COL = {
        "restaurant": "resto",
        "artisan": "artisan",
        "avocat": "avocat",
        "immo": "immo",
        "beaute": "beaute",
        "sante": "sante"
    }

    for niche, domain in NICHES.items():
        print(f"  - {domain}")
        sitemap_entries = []
        col_prefix = NICHE_TO_COL.get(niche)
        url_col = f"url_{col_prefix}_complete"

        for row in villes:
            csv_url = row.get(url_col)
            brand_name = extract_brand_from_url(csv_url)
            if not brand_name:
                brand_name = f"{niche.title()} {row.get('ville')}"
            
            brand_slug = slugify(brand_name)
            loc = f"https://{domain}/{niche}/{brand_slug}/"
            # Note: The worker handles the routing, so we use the final SEO domain.
            # But the demos are generated at output/[niche]/[brand-slug]/
            # The worker routes [domain]/... to Netlify/[niche]/[brand-slug]/
            # So the loc should be the domain loc.
            sitemap_entries.append(loc)

        # Write sitemap file for this niche
        with open(os.path.join(OUTPUT_DIR, f"sitemap-{niche}.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for url in sitemap_entries:
                f.write(f'  <url><loc>{url}</loc></url>\n')
            f.write('</urlset>')

    print(f"🏁 Done! 6 niche sitemaps generated in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_niche_sitemaps()
