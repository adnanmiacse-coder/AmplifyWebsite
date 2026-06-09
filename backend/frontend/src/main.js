// ─── Favicon ──────────────────────────────────────────────────
(function () {
    function setFavicon() {
        document.querySelectorAll('link[rel*="icon"]').forEach(el => el.remove());
        const link = document.createElement('link');
        link.rel  = 'icon';
        link.type = 'image/png';
        link.href = '/src/assets/amplify.png';
        document.head.appendChild(link);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setFavicon);
    } else {
        setFavicon();
    }
})();

// ─── Init ─────────────────────────────────────────────────────
console.log('%c✅ Amplify loaded', 'color:#00ff88;font-weight:700;font-size:14px;');

// ─── Language System ──────────────────────────────────────────
let currentLang = localStorage.getItem('amplify_lang') || 'en';

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('amplify_lang', lang);

    // Update toggle buttons
    document.getElementById('langEn')?.classList.toggle('active', lang === 'en');
    document.getElementById('langBn')?.classList.toggle('active', lang === 'bn');

    // Update all elements with data-en / data-bn attributes
    document.querySelectorAll('[data-en]').forEach(el => {
        const text = el.getAttribute('data-' + lang);
        if (text !== null) el.textContent = text;
    });

    // Update search placeholder
    const search = document.getElementById('oppSearch');
    if (search) {
        search.placeholder = lang === 'bn' ? 'সুযোগ খুঁজুন...' : 'Search opportunities...';
    }

    // Update html lang attribute
    document.documentElement.lang = lang === 'bn' ? 'bn' : 'en';
}

// ─── Header scroll ────────────────────────────────────────────
window.addEventListener('scroll', () => {
    const header = document.getElementById('header');
    if (!header) return;
    header.classList.toggle('scrolled', window.scrollY > 50);
}, { passive: true });

// ─── Utilities ───────────────────────────────────────────────
function showDownloadAlert() {
    const msg = currentLang === 'bn'
        ? 'অ্যাম্প্লিফাই ডাউনলোড করুন\n\nআপনার আগ্রহের জন্য ধন্যবাদ!\n(এটি একটি ডেমো বোতাম — আসল ডাউনলোড শীঘ্রই আসছে)'
        : 'Download Amplify\n\nThank you for your interest!\n(Demo button — real download coming soon)';
    alert(msg);
}

function stopVoice() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    const btn = document.getElementById('dashboardSpeakBtn');
    if (btn) btn.classList.remove('speaking');
}

// ─── DOM Ready ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved language on load
    setLang(currentLang);

    // Animate cards into view on scroll
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.08 }
    );

    document.querySelectorAll('.feature-card, .step-card, .card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
});