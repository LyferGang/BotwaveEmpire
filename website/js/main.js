// Botwave Empire - Main JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add scroll-based navbar styling
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.style.background = 'rgba(15, 15, 35, 0.95)';
        } else {
            navbar.style.background = 'rgba(15, 15, 35, 0.9)';
        }

        lastScroll = currentScroll;
    });

    // Health check - uncomment when API is deployed
    // checkHealth();
});

async function checkHealth() {
    try {
        const response = await fetch('https://api.botwave.app/health');
        const data = await response.json();
        console.log('Botwave API Status:', data.status);
    } catch (error) {
        console.log('API not available');
    }
}

// Copy code functionality
function copyCode(element) {
    const code = element.textContent;
    navigator.clipboard.writeText(code).then(() => {
        const original = element.textContent;
        element.textContent = 'Copied!';
        setTimeout(() => {
            element.textContent = original;
        }, 2000);
    });
}
