import json
import os
import random
import hashlib
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(BASE_DIR, "template.html")
data_path = os.path.join(BASE_DIR, "departements.json")
niche_path = os.path.join(BASE_DIR, "niche_data.json")
output_dir = os.path.join(BASE_DIR, "../output_departements")

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

def generate_dept_pages():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    with open(data_path, "r", encoding="utf-8") as f:
        departements = json.load(f)

    with open(niche_path, "r", encoding="utf-8") as f:
        niche = json.load(f)

    print(f"Generating department pages for niche: {niche['niche_name']}")
    count = 0
    
    # Generate common sections once
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

    for dept in departements:
        nom = dept.get("nom", "")
        slug = dept.get("slug", "").lower()
        code = dept.get("code", "")
        
        page_title = f"Agence Web {nom} ({code}) - Création de Site Internet & SEO - {niche['domain']}"

        # Simple FAQ for departments
        faq_html = ""
        for item in niche["faq"][:3]: # Only use first 3 for dept pages
            faq_html += f'''
                <div class="faq-item">
                    <button class="faq-btn">
                        {item["q"].replace("{{ville}}", nom)}
                        <i data-lucide="chevron-down" class="faq-icon"></i>
                    </button>
                    <div class="faq-content">
                        <p>{item["a"].replace("{{ville}}", nom)}</p>
                    </div>
                </div>
            '''
        
        replacements = {
            "{{ville}}": nom,
            "{{page_title}}": page_title,
            "{{domain}}": niche["domain"],
            "{{page_url}}": f"{niche['base_path']}/departement-{slug}.html",
            "{{code_postal}}": code,
            "{{telephone}}": niche["contact"]["phone"],
            "{{date_modified}}": get_current_date(),
            "{{services_html}}": services_html,
            "{{process_html}}": process_html,
            "{{pricing_html}}": pricing_html,
            "{{faq_html}}": faq_html,
            "{{maillage_interne}}": "", # Could add top cities of the dept here
            "{{departement_nom}}": nom,
            "{{image_url}}": f"https://{niche['domain']}/assets/dept-{slug}.jpg",
            "{{year}}": datetime.now().year,
            "{{words_json}}": json.dumps(niche["hero"]["words"], ensure_ascii=False)
        }

        content = template_content
        for key, value in replacements.items():
            content = content.replace(key, str(value))

        filename = f"departement-{slug}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(content)
        count += 1

    print(f"✅ Generated {count} department pages in {output_dir}")

if __name__ == "__main__":
    generate_dept_pages()
