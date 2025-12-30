export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const hostname = url.hostname;
        const path = url.pathname;

        // ============================================
        // CONFIGURATION
        // ============================================
        const NETLIFY_URL = "https://sitewen.netlify.app"; // Hosting for City/Demo pages
        const LOVABLE_URL = "https://sitewen.lovable.app"; // Hosting for Home/FAQ/Contact

        const nicheMapping = {
            "sites-restaurants.fr": "restaurant",
            "sitesartisans.fr": "artisan",
            "sites-beaute.fr": "beaute",
            "sites-immobiliers.fr": "immo",
            "sites-avocats.fr": "avocat",
            "sites-sante.fr": "sante"
        };

        // Helper for Content-Type
        const getContentType = (filename) => {
            if (filename.endsWith(".html")) return "text/html; charset=UTF-8";
            if (filename.endsWith(".css")) return "text/css; charset=UTF-8";
            if (filename.endsWith(".js")) return "application/javascript; charset=UTF-8";
            if (filename.endsWith(".svg")) return "image/svg+xml";
            if (filename.endsWith(".png")) return "image/png";
            if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) return "image/jpeg";
            if (filename.endsWith(".webp")) return "image/webp";
            if (filename.endsWith(".woff2")) return "font/woff2";
            if (filename.endsWith(".xml")) return "application/xml; charset=UTF-8";
            return "application/octet-stream";
        };

        // ============================================
        // 1. NICHE DOMAINS (Demos & Sitemaps)
        // ============================================
        for (const [domain, niche] of Object.entries(nicheMapping)) {
            if (hostname.endsWith(domain)) {
                const brandSlug = hostname.replace(`.${domain}`, "");

                // --- 1.1 Sitemaps for Niche Domains ---
                if ((hostname === domain || hostname === "www." + domain) && path === "/sitemap.xml") {
                    const response = await fetch(`${NETLIFY_URL}/sitemaps/sitemap-${niche}.xml`);
                    return new Response(response.body, {
                        status: response.status,
                        headers: { "Content-Type": "application/xml; charset=UTF-8", "Cache-Control": "public, max-age=86400" }
                    });
                }

                // --- 1.2 Home Redirect/Landing for Niche ---
                if (!brandSlug || brandSlug === "www" || brandSlug === domain) {
                    return Response.redirect("https://agence-web-locale.fr", 301);
                }

                // --- 1.3 Niche Demos (Subdomains) ---
                let targetPath = path;
                if (path === "/" || path === "") targetPath = "/index.html";
                else if (!path.includes(".")) targetPath = path + ".html";

                const targetUrl = `${NETLIFY_URL}/demos/${niche}/${brandSlug}${targetPath}`;
                const response = await fetch(targetUrl);

                return new Response(response.body, {
                    status: response.status,
                    headers: {
                        "Content-Type": getContentType(targetPath),
                        "Cache-Control": "public, max-age=3600"
                    }
                });
            }
        }

        // ============================================
        // 2. MAIN DOMAIN: agence-web-locale.fr
        // ============================================
        if (hostname === "agence-web-locale.fr" || hostname === "www.agence-web-locale.fr") {

            // Redirect www -> non-www
            if (hostname === "www.agence-web-locale.fr") {
                return Response.redirect("https://agence-web-locale.fr" + path + url.search, 301);
            }

            // 2.1 Netlify Functions (Forms/API)
            if (path.startsWith("/.netlify/functions/")) {
                if (request.method === "OPTIONS") {
                    return new Response(null, {
                        status: 204,
                        headers: {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type"
                        }
                    });
                }
                return fetch(NETLIFY_URL + path, {
                    method: request.method,
                    headers: request.headers,
                    body: request.body
                });
            }

            // 2.2 Sitemaps & Robots
            if (path === "/sitemap.xml") {
                const response = await fetch(NETLIFY_URL + "/sitemap.xml");
                return new Response(response.body, {
                    status: response.status,
                    headers: { "Content-Type": "application/xml; charset=UTF-8", "Cache-Control": "public, max-age=86400" }
                });
            }

            if (path === "/robots.txt") {
                const response = await fetch(NETLIFY_URL + "/robots.txt");
                if (response.status === 200) return response;
                const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: https://agence-web-locale.fr/sitemap.xml`;
                return new Response(robotsTxt, { headers: { "Content-Type": "text/plain; charset=UTF-8" } });
            }

            // 2.3 Assets (CSS, JS, Fonts)
            if (path.startsWith("/assets/")) {
                const response = await fetch(NETLIFY_URL + path);
                if (response.status === 200) {
                    return new Response(response.body, {
                        status: 200,
                        headers: { "Content-Type": getContentType(path), "Cache-Control": "public, max-age=604800" }
                    });
                }
                // Fallback to Lovable
                return fetch(LOVABLE_URL + path);
            }

            // 2.4 Siloed City Pages ( /[dept]/creation-site-internet-[city] )
            const cityPattern = /^\/[^\/]+\/creation-site-internet-[^\/]+$/;
            if (cityPattern.test(path)) {
                let targetPath = path;
                if (!targetPath.endsWith(".html")) targetPath += ".html";
                const response = await fetch(NETLIFY_URL + targetPath);
                if (response.status === 200) {
                    return new Response(response.body, {
                        status: 200,
                        headers: { "Content-Type": "text/html; charset=UTF-8", "Cache-Control": "public, max-age=3600" }
                    });
                }
            }

            // 2.5 Department/Region Hubs ( /departement-[slug] )
            if (path.startsWith("/departement-") || path.startsWith("/region-")) {
                let targetPath = path;
                if (!targetPath.endsWith(".html")) targetPath += ".html";
                const response = await fetch(NETLIFY_URL + targetPath);
                if (response.status === 200) {
                    return new Response(response.body, {
                        status: 200,
                        headers: { "Content-Type": "text/html; charset=UTF-8" }
                    });
                }
            }

            // 2.6 Legacy URLs (Compatibilty)
            if (path.startsWith("/creation-site-internet-") && !path.includes("/", 1)) {
                let targetPath = path;
                if (!targetPath.endsWith(".html")) targetPath += ".html";
                const response = await fetch(NETLIFY_URL + targetPath);
                if (response.status === 200) return response;
            }

            // 2.7 Default: Lovable (Home, FAQ, etc.)
            return fetch(LOVABLE_URL + path + url.search);
        }

        // Catch-all
        return fetch(NETLIFY_URL + path);
    }
}
