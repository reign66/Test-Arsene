import requests

domains = [
    "https://agence-web-locale.fr",
    "https://agence-web-locale.fr/haute-garonne/creation-site-internet-toulouse",
    "https://agence-web-locale.fr/sitemap.xml",
    "https://sites-restaurants.fr",
    "https://sitesartisans.fr",
    "https://sites-beaute.fr",
    "https://sites-immobiliers.fr",
    "https://sites-avocats.fr",
    "https://sites-sante.fr"
]

print("🔍 Starting Global Network Verification...")
for url in domains:
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        print(f"[{response.status_code}] {url}")
        if response.status_code == 200:
            print(f"   ✅ Live - Content Length: {len(response.content)}")
        else:
            print(f"   ⚠️ Warning - Status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {url} - {str(e)[:50]}...")

print("\n🏁 Diagnostics Complete.")
