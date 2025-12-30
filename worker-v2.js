export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const hostname = url.hostname;
        const path = url.pathname;

        const NETLIFY_URL = "https://sitewen.netlify.app";
        const LOVABLE_URL = "https://sitewen.lovable.app";

        const nicheMapping = {
            "sites-restaurants.fr": "restaurant",
            "sitesartisans.fr": "artisan",
            "sites-beaute.fr": "beaute",
            "sites-immobiliers.fr": "immo",
            "sites-avocats.fr": "avocat",
            "sites-sante.fr": "sante"
        };

        const sitemapNicheMap = {
            "sites-restaurants.fr": "restaurant",
            "sitesartisans.fr": "artisan",
            "sites-beaute.fr": "beaute",
            "sites-immobiliers.fr": "immo",
            "sites-avocats.fr": "avocat",
            "sites-sante.fr": "sante"
        }

        // 1. NICHE SITEMAPS & HOME REDIRECT
        for (const [domain, niche] of Object.entries(nicheMapping)) {
            if (hostname === domain || hostname === "www." + domain) {
                // Serve specific niche sitemap
                if (path === "/sitemap.xml") {
                    const nicheKey = sitemapNicheMap[domain];
                    return fetch(NETLIFY_URL + "/sitemaps/sitemap-" + nicheKey + ".xml");
                }
                // Redirect homepage to main site
                return Response.redirect("https://agence-web-locale.fr", 301);
            }
        }

        // 2. NICHE SUBDOMAINS (DEMOS)
        for (const [domain, niche] of Object.entries(nicheMapping)) {
            if (hostname.endsWith(domain)) {
                const brandSlug = hostname.replace(`.${domain}`, "");
                if (brandSlug && brandSlug !== domain && brandSlug !== "www") {
                    let targetPath = path;
                    if (path === "/" || path === "") targetPath = "/index.html";
                    else if (!path.includes(".")) targetPath = path + ".html";

                    const targetUrl = `${NETLIFY_URL}/demos/${niche}/${brandSlug}${targetPath}`;
                    return fetch(targetUrl);
                }
            }
        }

        // 3. MAIN DOMAIN (agence-web-locale.fr)
        if (hostname === "agence-web-locale.fr" || hostname === "www.agence-web-locale.fr") {
            if (hostname === "www.agence-web-locale.fr") {
                return Response.redirect("https://agence-web-locale.fr" + path + url.search, 301);
            }

            // Sitemap & Robots
            if (path === "/sitemap.xml") return fetch(NETLIFY_URL + "/sitemap.xml");
            if (path === "/robots.txt") {
                const response = await fetch(NETLIFY_URL + "/robots.txt");
                if (response.status === 200) return response;
                const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: https://agence-web-locale.fr/sitemap.xml`;
                return new Response(robotsTxt, { headers: { "Content-Type": "text/plain" } });
            }

            // Static Assets
            if (path.startsWith("/assets/")) {
                const response = await fetch(NETLIFY_URL + path);
                if (response.status === 404) return fetch(LOVABLE_URL + path);
                return response;
            }

            // Siloed City Pages ( /[dept]/creation-site-internet-[city] )
            const cityPattern = /^\/[^\/]+\/creation-site-internet-[^\/]+$/;
            if (cityPattern.test(path)) {
                let targetPath = path;
                if (!targetPath.endsWith(".html")) targetPath += ".html";
                const response = await fetch(NETLIFY_URL + targetPath);
                if (response.status === 200) return response;
            }

            // Department Hubs ( /departement-[slug] )
            if (path.startsWith("/departement-") && !path.includes(".")) {
                let targetPath = path;
                if (!targetPath.endsWith(".html")) targetPath += ".html";
                const response = await fetch(NETLIFY_URL + targetPath);
                if (response.status === 200) return response;
            }

            // Default to Lovable for Home, FAQ, etc.
            return fetch(LOVABLE_URL + path + url.search);
        }

        // Catch-all
        return fetch(NETLIFY_URL + path);
    }
}
