import requests
import json

# Setup
MAIN_DOMAIN = "https://agence-web-locale.fr"
NETLIFY_URL = "https://sitewen.netlify.app"

# Configuration des tests
TESTS = [
    {"name": "Site Principal (Root)", "url": f"{MAIN_DOMAIN}/", "expected": 200},
    {"name": "Sitemap Global", "url": f"{MAIN_DOMAIN}/sitemap.xml", "expected": 200},
    {"name": "Page Silo Toulouse", "url": f"{MAIN_DOMAIN}/haute-garonne/creation-site-internet-toulouse", "expected": 200},
    {"name": "Page Hub Haute-Garonne", "url": f"{MAIN_DOMAIN}/departement-haute-garonne", "expected": 200},
]

NICHES = {
    "sites-restaurants.fr": "La Table des Halles",
    "sitesartisans.fr": "Artisan Express",
    "sites-beaute.fr": "Espace Beaute",
    "sites-immobiliers.fr": "Immo Pro",
    "sites-avocats.fr": "Cabinet Avocat",
    "sites-sante.fr": "Sante Plus"
}

def slugify(text):
    import re
    text = text.lower().replace(" ", "-")
    return re.sub(r'[^a-z0-9\-]', '', text)

# Ajout des tests niche
for domain, brand in NICHES.items():
    # Test Sitemap Niche sur domaine nu
    TESTS.append({
        "name": f"Sitemap {domain}",
        "url": f"https://{domain}/sitemap.xml",
        "expected": 200
    })
    # Test Redirection domaine nu -> Main
    TESTS.append({
        "name": f"Redirect {domain} -> Main",
        "url": f"https://{domain}",
        "expected": 200 # Redirect should end up on 200 at Main
    })
    # Test Démo Premium (Subdomain)
    brand_slug = slugify(brand)
    TESTS.append({
        "name": f"Demo {brand} ({domain})",
        "url": f"https://{brand_slug}.{domain}/",
        "expected": 200
    })

def run_checks():
    print("🚀 Démarrage du Ping Master Network...")
    print("="*60)
    
    success_count = 0
    
    for test in TESTS:
        print(f"📡 Testing: {test['name']}")
        try:
            # On suit les redirections pour vérifier la destination finale
            response = requests.get(test['url'], timeout=10, allow_redirects=True)
            
            if response.status_code == test['expected']:
                print(f"   ✅ SUCCESS ({response.status_code}) - {test['url']}")
                success_count += 1
            else:
                print(f"   ❌ FAILED ({response.status_code}) - {test['url']}")
                if response.status_code == 404:
                    print(f"      👉 Vérifiez si Netlify a fini le déploiement ou si le Worker est actif.")
                elif response.status_code == 525:
                    print(f"      👉 Erreur SSL : Vérifiez que Cloudflare est en mode SSL 'Full'.")
        except Exception as e:
            print(f"   ⚠️ ERROR: {str(e)[:100]}")
        print("-" * 60)

    print(f"\n🏁 Résultats : {success_count}/{len(TESTS)} liens sont opérationnels.")
    if success_count < len(TESTS):
        print("💡 Conseil : Si vous venez de déployer le Worker, attendez 1-2 minutes et relancez le script.")

if __name__ == "__main__":
    run_checks()
