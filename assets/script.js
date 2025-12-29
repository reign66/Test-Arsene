/* assets/script.js - Agence Web Locale (Anty Edition) */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // FAQ Accordion
    document.querySelectorAll('.faq-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.parentElement;
            const isActive = item.classList.contains('active');

            // Close all
            document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));

            // Toggle current
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // Reveal on Scroll (Intersection Observer)
    const revealCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');

                // If it's a counter, trigger count animation
                if (entry.target.querySelector('.counter')) {
                    triggerCounter(entry.target.querySelector('.counter'));
                }
            }
        });
    };

    const observer = new IntersectionObserver(revealCallback, {
        threshold: 0.1
    });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Counter Animation
    function triggerCounter(el) {
        if (el.dataset.animated) return;
        el.dataset.animated = "true";

        const target = +el.dataset.target;
        const speed = 100; // The higher the slower

        const updateCount = () => {
            const count = +el.innerText;
            const inc = target / speed;

            if (count < target) {
                el.innerText = Math.ceil(count + inc);
                setTimeout(updateCount, 10);
            } else {
                el.innerText = target;
            }
        };
        updateCount();
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation + Anti-spam (timestamp validation)
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        const loadTime = Date.now();

        contactForm.addEventListener('submit', (e) => {
            const now = Date.now();
            const diff = (now - loadTime) / 1000;

            if (diff < 3) {
                e.preventDefault();
                console.warn('Bot detected (too fast)');
                return;
            }

            const honeypot = contactForm.querySelector('input[name="honeypot"]');
            if (honeypot && honeypot.value !== "") {
                e.preventDefault();
                console.warn('Bot detected (honeypot)');
                return;
            }

            // Success placeholder
            // alert('Merci ! Votre demande pour ' + document.title + ' a été transmise.');
        });
    }
});
