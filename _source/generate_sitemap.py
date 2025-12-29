import json
import os
from datetime import datetime

def generate_sitemap():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%Y-%m-%d")
    cities_data_path = os.path.join(BASE_DIR, 'villes_enrichies_final-1.json')
    depts_data_path = os.path.join(BASE_DIR, 'departements.json')
    niche_path = os.path.join(BASE_DIR, 'niche_data.json')
    output_path = os.path.join(BASE_DIR, '../output/sitemap.xml')
    
    with open(niche_path, "r", encoding="utf-8") as f:
        niche = json.load(f)
    
    base_url = f"https://{niche['domain']}"
    niche_prefix = niche['base_path']
    
    sitemap_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Add homepage
    sitemap_content.append(f'  <url><loc>{base_url}/</loc><lastmod>{current_date}</lastmod><priority>1.0</priority></url>')

    # Cities
    if os.path.exists(cities_data_path):
        with open(cities_data_path, 'r', encoding='utf-8') as f:
            cities = json.load(f)
        for city in cities:
            slug = city.get('slug', '').lower()
            if slug:
                loc = f"{base_url}{niche_prefix}/{slug}.html"
                sitemap_content.append(f'  <url><loc>{loc}</loc><lastmod>{current_date}</lastmod><priority>0.8</priority></url>')
    
    # Departments
    if os.path.exists(depts_data_path):
        with open(depts_data_path, 'r', encoding='utf-8') as f:
            depts = json.load(f)
        for dept in depts:
            slug = dept.get('slug', '').lower()
            if slug:
                loc = f"{base_url}{niche_prefix}/departement-{slug}.html"
                sitemap_content.append(f'  <url><loc>{loc}</loc><lastmod>{current_date}</lastmod><priority>0.9</priority></url>')

    sitemap_content.append('</urlset>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))
    
    print(f"Sitemap generated at {output_path}")

if __name__ == "__main__":
    generate_sitemap()
