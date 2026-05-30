// src/main.js
console.log('%c✅ Amplify loaded successfully!', 'color:#00ff88; font-weight:700; font-size:15px;');

function showDownloadAlert() {
    alert("📱 Download Amplify App\n\nThank you for your interest!\n\n(This is a demo button - real download can be added later)");
}

function showRoutineAlert() {
    alert("🟢 Routine Mode Activated!\n\nThis is just a beautiful preview.\nThe actual Routine Planner feature is coming in the app.");
}

function stopVoice() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

// ✅ Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', () => {

    // Header scroll effect
    window.addEventListener('scroll', () => {
        const header = document.getElementById('header');
        if (header) {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
    });

    // Language toggle
    const langBn = document.getElementById('langBn');
    const langEn = document.getElementById('langEn');

    if (langBn && langEn) {
        langBn.addEventListener('click', () => {
            langBn.classList.add('active');
            langEn.classList.remove('active');
        });

        langEn.addEventListener('click', () => {
            langEn.classList.add('active');
            langBn.classList.remove('active');
        });
    }

});