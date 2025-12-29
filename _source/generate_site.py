import json
import os
import random
import hashlib
import math
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(BASE_DIR, "template.html")
data_path = os.path.join(BASE_DIR, "villes_enrichies_final-1.json")
niche_path = os.path.join(BASE_DIR, "niche_data.json")
output_dir = os.path.join(BASE_DIR, "../output")
depts_path = os.path.join(BASE_DIR, "departements.json")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_stable_random(seed_str, min_val, max_val):
    period = datetime.now().isocalendar()[1] // 2
    seed_data = f"{seed_str}-{period}"
    seed_hash = int(hashlib.md5(seed_data.encode()).hexdigest(), 16)
    random.seed(seed_hash)
    val = random.randint(min_val, max_val)
    random.seed()
    return val

def get_prochaine_dispo():
    now = datetime.now()
    days_to_add = 0 if now.hour < 18 else 1 
    # For a locksmith, "prochaine dispo" is often "Now" or "Today"
    # But for "Freshness", we can say "Intervention finished X minutes ago" or similar
    # Here we'll stick to a date for simplicity, but more specific
    return f"aujourd'hui à {get_stable_random(datetime.now().strftime('%Y-%m-%d'), 8, 22)}h{get_stable_random('min', 10, 55)}"

def get_mois_actuel():
    months_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return months_fr[datetime.now().month-1]

def generate_pages():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    with open(data_path, "r", encoding="utf-8") as f:
        all_cities = json.load(f)

    with open(niche_path, "r", encoding="utf-8") as f:
        niche = json.load(f)

    # Load department slugs
    dept_name_to_slug = {}
    if os.path.exists(depts_path):
        with open(depts_path, "r", encoding="utf-8") as f:
            depts_data = json.load(f)
            for d in depts_data:
                dept_name_to_slug[d["nom"]] = d["slug"]

    # Group cities by department for internal linking
    cities_by_dept = defaultdict(list)
    for city in all_cities:
        dept = city.get("departement_nom", "")
        if dept:
            cities_by_dept[dept].append(city)

    for dept in cities_by_dept:
        cities_by_dept[dept].sort(key=lambda x: int(x.get("population", 0) or 0), reverse=True)

    print(f"Generating site for niche: {niche['niche_name']}")
    count = 0
    for row in all_cities:
        ville = row.get("ville", "")
        slug = row.get("slug", "").strip().lower()
        dept_name = row.get("departement_nom", "")
        cp = row.get("code_postal", "")
        
        # SEO Titles
        page_title = f"Agence Web {ville} ({cp}) - Création Site Internet Premium - {niche['domain']}"
        
        # Internal Linking
        dept_cities = cities_by_dept.get(dept_name, [])
        siblings = [c for c in dept_cities if c.get("slug") != slug][:20]
        maillage_html = " ".join([f'<a href="{niche["base_path"]}/{c["slug"]}.html">Expert Web {c["ville"]}</a>' for c in siblings])

        # Services HTML Generation
        services_html = ""
        for s in niche["services"]:
            badge = f'<div class="card-badge">{s["badge"]}</div>' if "badge" in s else ""
            services_html += f'''
                <div class="service-card reveal">
                    {badge}
                    <div class="service-icon"><i data-lucide="{s["icon"].lower()}"></i></div>
                    <h3>{s["title"]}</h3>
                    <p>{s["description"]}</p>
                    <div class="service-price">{s["price"]}</div>
                </div>
            '''

        # Process HTML Generation
        process_html = ""
        for p in niche["process"]:
            process_html += f'''
                <div class="process-step reveal">
                    <div class="step-num">{p["step"]}</div>
                    <div class="step-content">
                        <h4>{p["title"]}</h4>
                        <p>{p["text"]}</p>
                    </div>
                </div>
            '''

        # Pricing HTML Generation
        pricing_html = ""
        for pr in niche["pricing"]:
            is_featured = "featured" if pr.get("badge") == "POPULAIRE" else ""
            badge = f'<div class="card-badge" style="top:25px; right:-25px;">{pr["badge"]}</div>' if "badge" in pr else ""
            features_html = "".join([f'<li><i data-lucide="check-circle"></i> {f}</li>' for f in pr["features"]])
            pricing_html += f'''
                <div class="price-card {is_featured} reveal">
                    {badge}
                    <div class="price-name">{pr["name"]}</div>
                    <div class="price-value">{pr["price"]}</div>
                    <div class="price-for">{pr["for"]}</div>
                    <ul class="price-features">
                        {features_html}
                    </ul>
                    <a href="tel:01XX" class="btn {'btn-primary' if is_featured else ''}" style="width:100%; display:block; border: 1px solid var(--primary);">Choisir</a>
                </div>
            '''

        # FAQ Generation
        faq_html = ""
        for item in niche["faq"]:
            q = item["q"].replace("{{ville}}", ville)
            a = item["a"].replace("{{ville}}", ville)
            faq_html += f'''
                <div class="faq-item">
                    <button class="faq-btn">
                        {q}
                        <i data-lucide="chevron-down" class="faq-icon"></i>
                    </button>
                    <div class="faq-content">
                        <p>{a}</p>
                    </div>
                </div>
            '''

        replacements = {
            "{{ville}}": ville,
            "{{page_title}}": page_title,
            "{{domain}}": niche["domain"],
            "{{page_url}}": f"{niche['base_path']}/{slug}.html",
            "{{code_postal}}": cp,
            "{{telephone}}": niche["contact"]["phone"],
            "{{date_modified}}": get_current_date(),
            "{{services_html}}": services_html,
            "{{process_html}}": process_html,
            "{{pricing_html}}": pricing_html,
            "{{faq_html}}": faq_html,
            "{{maillage_interne}}": maillage_html,
            "{{departement_nom}}": dept_name,
            "{{image_url}}": f"https://{niche['domain']}/assets/hero-{slug}.jpg",
            "{{year}}": datetime.now().year,
            "{{words_json}}": json.dumps(niche["hero"]["words"], ensure_ascii=False)
        }

        content = template_content
        for key, value in replacements.items():
            content = content.replace(key, str(value))
        
        filename = f"{slug}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(content)
        
        count += 1
        if count % 100 == 0:
            print(f"Generated {count} pages...")

    print(f"🏁 Successfully generated {count} pages in {output_dir}")

if __name__ == "__main__":
    generate_pages()
