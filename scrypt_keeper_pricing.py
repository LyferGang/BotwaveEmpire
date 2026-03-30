#!/usr/bin/env python3
"""
SCRIPT KEEPER #1: PRICING + STRIPE ORCHESTRATOR
Implements: Service tiers ($299/$499/$1499) with live Stripe checkout
Run: python script_keeper_pricing.py
"""

import os
import sys
import re
from pathlib import Path

class PricingKeeper:
    """Orchestrates pricing page and Stripe integration implementation."""

    def __init__(self):
        self.base_path = Path("/home/gringo/BotwaveEmpire")
        self.changes_made = []

    def log(self, msg):
        print(f"[SCRIPT KEEPER] {msg}")
        self.changes_made.append(msg)

    def update_web_app(self):
        """Update dashboard/web_app.py with new pricing tiers."""
        web_app_path = self.base_path / "dashboard" / "web_app.py"

        if not web_app_path.exists():
            self.log("ERROR: web_app.py not found")
            return False

        content = web_app_path.read_text()

        # Update PLANS dictionary
        old_plans = '''PLANS = {
            "starter": {"price_id": os.getenv("STRIPE_PRICE_ID_STARTER"), "amount": 4900},
            "professional": {"price_id": os.getenv("STRIPE_PRICE_ID_PROFESSIONAL"), "amount": 14900}
        }'''

        new_plans = '''PLANS = {
            "starter": {"price_id": os.getenv("STRIPE_PRICE_ID_STARTER"), "amount": 29900, "name": "Starter"},
            "professional": {"price_id": os.getenv("STRIPE_PRICE_ID_PROFESSIONAL"), "amount": 49900, "name": "Professional"},
            "enterprise": {"price_id": os.getenv("STRIPE_PRICE_ID_ENTERPRISE"), "amount": 149900, "name": "Enterprise"}
        }'''

        if old_plans in content:
            content = content.replace(old_plans, new_plans)
            self.log("Updated PLANS dictionary with new pricing tiers")
        else:
            # Try to find and replace with regex
            pattern = r'PLANS = \{[^}]+\}'
            if re.search(pattern, content):
                content = re.sub(pattern, new_plans.strip(), content)
                self.log("Updated PLANS dictionary (regex match)")

        # Update checkout session to support dynamic price creation
        old_session = '''session_data = stripe_service.create_checkout_session(
            success_url=f"{request.host_url}checkout/success",
            cancel_url=f"{request.host_url}checkout/canceled",
            line_items=[{"price": PLANS[plan]["price_id"], "quantity": 1}]
        )'''

        new_session = '''session_data = stripe_service.create_checkout_session(
            success_url=f"{request.host_url}checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}checkout/canceled",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": PLANS[plan]["amount"],
                    "product_data": {"name": f"Botwave {PLANS[plan]['name']} Plan", "description": "AI Automation Platform"}
                },
                "quantity": 1
            }],
            mode="subscription" if plan != "enterprise" else "payment"
        )'''

        if old_session in content:
            content = content.replace(old_session, new_session)
            self.log("Updated checkout session creation")

        web_app_path.write_text(content)
        self.log(f"Written: {web_app_path}")
        return True

    def update_pricing_html(self):
        """Update website/pricing.html with new tiers and working checkout."""
        pricing_path = self.base_path / "website" / "pricing.html"

        if not pricing_path.exists():
            self.log("ERROR: pricing.html not found")
            return False

        # New pricing page content
        pricing_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pricing | Botwave - AI Automation Platform</title>
    <meta name="description" content="Botwave pricing plans - AI-powered business automation for every stage">
    <link rel="stylesheet" href="css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://js.stripe.com/v3/"></script>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --accent: #10b981;
            --bg: #0f0f23;
            --bg-card: #1a1a2e;
            --bg-hover: #252542;
            --text: #ffffff;
            --text-muted: #94a3b8;
            --border: #333355;
            --success: #10b981;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }

        /* Navigation */
        .navbar {
            background: rgba(15, 15, 35, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 1.2rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
        }

        .navbar .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.75rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
        }

        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }

        .nav-links a:hover { color: var(--text); }

        .btn-nav {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important;
            padding: 0.5rem 1.25rem;
            border-radius: 0.5rem;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .btn-nav:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        }

        /* Hero */
        .hero {
            padding: 10rem 0 5rem;
            text-align: center;
            background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 60%);
        }

        .hero h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 1.25rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
        }

        /* Pricing Grid */
        .pricing-section { padding: 4rem 0; }

        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin-top: 3rem;
        }

        @media (max-width: 1024px) {
            .pricing-grid { grid-template-columns: 1fr; max-width: 500px; margin: 3rem auto 0; }
        }

        .pricing-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 1.5rem;
            padding: 2.5rem;
            position: relative;
            transition: all 0.3s;
        }

        .pricing-card:hover {
            transform: translateY(-8px);
            border-color: var(--primary);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
        }

        .pricing-card.featured {
            border-color: var(--primary);
            box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
            transform: scale(1.05);
        }

        .pricing-card.featured:hover { transform: scale(1.05) translateY(-8px); }

        .popular-badge {
            position: absolute;
            top: -14px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .plan-name {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .plan-description {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }

        .price {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #fff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .price span {
            font-size: 1.25rem;
            font-weight: 400;
            color: var(--text-muted);
            -webkit-text-fill-color: var(--text-muted);
        }

        .price-note {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }

        .features-list {
            list-style: none;
            margin: 2rem 0;
        }

        .features-list li {
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.95rem;
        }

        .features-list li:last-child { border-bottom: none; }

        .features-list li::before {
            content: "✓";
            color: var(--success);
            font-weight: bold;
            font-size: 1.1rem;
            width: 20px;
        }

        .btn-checkout {
            width: 100%;
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            display: block;
            text-decoration: none;
            border: none;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-checkout.primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }

        .btn-checkout.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }

        .btn-checkout.secondary {
            background: transparent;
            color: var(--text);
            border: 2px solid var(--border);
        }

        .btn-checkout.secondary:hover {
            background: var(--bg-hover);
            border-color: var(--primary);
        }

        .secure-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        .secure-badge svg { width: 16px; height: 16px; }

        /* FAQ Section */
        .faq-section {
            padding: 6rem 0;
            background: radial-gradient(ellipse at bottom, rgba(99, 102, 241, 0.1), transparent 60%);
        }

        .faq-section h2 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
        }

        .faq-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }

        @media (max-width: 768px) { .faq-grid { grid-template-columns: 1fr; } }

        .faq-item {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 1.5rem;
        }

        .faq-item h3 {
            color: var(--primary);
            margin-bottom: 0.75rem;
            font-size: 1.1rem;
        }

        .faq-item p { color: var(--text-muted); font-size: 0.95rem; }

        /* CTA Section */
        .cta-section {
            padding: 6rem 0;
            text-align: center;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        }

        .cta-section h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .cta-section p {
            color: var(--text-muted);
            font-size: 1.1rem;
            margin-bottom: 2rem;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Footer */
        footer {
            border-top: 1px solid var(--border);
            padding: 3rem 0;
            text-align: center;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
        }

        .footer-links a {
            color: var(--text-muted);
            text-decoration: none;
            transition: color 0.3s;
        }

        .footer-links a:hover { color: var(--primary); }

        /* Loading State */
        .btn-checkout.loading {
            opacity: 0.7;
            cursor: not-allowed;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
        }

        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">Botwave</a>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="pricing.html">Pricing</a></li>
                <li><a href="customer_portal.html">Portal</a></li>
                <li><a href="onboarding.html" class="btn-nav">Get Started</a></li>
            </ul>
        </div>
    </nav>

    <section class="hero">
        <div class="container">
            <h1>Simple, Transparent Pricing</h1>
            <p>Choose the plan that fits your business. All plans include a 14-day free trial. No credit card required.</p>
        </div>
    </section>

    <section class="pricing-section">
        <div class="container">
            <div class="pricing-grid">
                <!-- STARTER -->
                <div class="pricing-card">
                    <div class="plan-name">Starter</div>
                    <p class="plan-description">Perfect for small businesses getting started with AI automation</p>
                    <div class="price">$299<span>/month</span></div>
                    <p class="price-note">$3,588 billed annually (save 20%)</p>

                    <ul class="features-list">
                        <li>1 Business Agent</li>
                        <li>500 tasks/month</li>
                        <li>Email support (48hr response)</li>
                        <li>SQLite database</li>
                        <li>Basic analytics dashboard</li>
                        <li>Web dashboard access</li>
                        <li>Telegram bot integration</li>
                        <li>Standard reports</li>
                    </ul>

                    <button class="btn-checkout secondary" onclick="checkout('starter', this)">Get Started</button>
                    <div class="secure-badge">
                        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.2v3.5c0 .7-.6 1.3-1.2 1.3H9.2c-.6 0-1.2-.6-1.2-1.2v-3.5c0-.7.6-1.3 1.2-1.3V9.5C9.2 8.1 10.6 7 12 7zm0 1c-.8 0-1.5.7-1.5 1.5V11h3V9.5c0-.8-.7-1.5-1.5-1.5z"/></svg>
                        <span>Secured by Stripe</span>
                    </div>
                </div>

                <!-- PROFESSIONAL -->
                <div class="pricing-card featured">
                    <div class="popular-badge">Most Popular</div>
                    <div class="plan-name">Professional</div>
                    <p class="plan-description">For growing businesses that need multiple agents and priority support</p>
                    <div class="price">$499<span>/month</span></div>
                    <p class="price-note">$5,988 billed annually (save 20%)</p>

                    <ul class="features-list">
                        <li>5 Agents (Business, Intelligence, Service + custom)</li>
                        <li>Unlimited tasks</li>
                        <li>Priority support (24hr response)</li>
                        <li>PostgreSQL database</li>
                        <li>Advanced analytics & insights</li>
                        <li>Custom workflow builder</li>
                        <li>API access</li>
                        <li>Webhook integrations</li>
                        <li>White-label option</li>
                        <li>Dedicated account manager</li>
                    </ul>

                    <button class="btn-checkout primary" onclick="checkout('professional', this)">Get Started</button>
                    <div class="secure-badge">
                        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.2v3.5c0 .7-.6 1.3-1.2 1.3H9.2c-.6 0-1.2-.6-1.2-1.2v-3.5c0-.7.6-1.3 1.2-1.3V9.5C9.2 8.1 10.6 7 12 7zm0 1c-.8 0-1.5.7-1.5 1.5V11h3V9.5c0-.8-.7-1.5-1.5-1.5z"/></svg>
                        <span>Secured by Stripe</span>
                    </div>
                </div>

                <!-- ENTERPRISE -->
                <div class="pricing-card">
                    <div class="plan-name">Enterprise</div>
                    <p class="plan-description">Full AI transformation with dedicated infrastructure and custom development</p>
                    <div class="price">$1,499<span>/month</span></div>
                    <p class="price-note">Custom billing available</p>

                    <ul class="features-list">
                        <li>Unlimited agents</li>
                        <li>Unlimited tasks</li>
                        <li>24/7 dedicated support</li>
                        <li>Managed cloud hosting</li>
                        <li>Custom agent development</li>
                        <li>SLA guarantee (99.9% uptime)</li>
                        <li>On-premise deployment option</li>
                        <li>Advanced security features</li>
                        <li>Dedicated infrastructure</li>
                        <li>Quarterly business reviews</li>
                    </ul>

                    <button class="btn-checkout secondary" onclick="checkout('enterprise', this)">Contact Sales</button>
                    <div class="secure-badge">
                        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.2v3.5c0 .7-.6 1.3-1.2 1.3H9.2c-.6 0-1.2-.6-1.2-1.2v-3.5c0-.7.6-1.3 1.2-1.3V9.5C9.2 8.1 10.6 7 12 7zm0 1c-.8 0-1.5.7-1.5 1.5V11h3V9.5c0-.8-.7-1.5-1.5-1.5z"/></svg>
                        <span>Enterprise-grade security</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="faq-section">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <h3>Can I self-host Botwave?</h3>
                    <p>Yes! Botwave is open source. You can self-host for free or use our managed service with professional support.</p>
                </div>
                <div class="faq-item">
                    <h3>What payment methods do you accept?</h3>
                    <p>We accept all major credit cards, debit cards, and ACH bank transfers through Stripe's secure payment platform.</p>
                </div>
                <div class="faq-item">
                    <h3>Is there a free trial?</h3>
                    <p>Yes! All plans include a 14-day free trial. No credit card required to start. Cancel anytime.</p>
                </div>
                <div class="faq-item">
                    <h3>Can I cancel anytime?</h3>
                    <p>Absolutely. You can cancel your subscription at any time with no cancellation fees. Your data remains accessible for 30 days.</p>
                </div>
                <div class="faq-item">
                    <h3>Do you offer discounts?</h3>
                    <p>Yes! We offer 20% off for annual billing and special pricing for nonprofits and educational institutions.</p>
                </div>
                <div class="faq-item">
                    <h3>What happens after I subscribe?</h3>
                    <p>You'll receive immediate access to the dashboard, setup instructions, and can start building agents right away.</p>
                </div>
            </div>
        </div>
    </section>

    <section class="cta-section">
        <div class="container">
            <h2>Ready to Automate Your Business?</h2>
            <p>Join hundreds of businesses using Botwave to save time and scale operations.</p>
            <a href="onboarding.html" class="btn-checkout primary" style="display: inline-block; width: auto; padding: 1rem 3rem;">Start Free Trial</a>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 Botwave. All rights reserved.</p>
            <div class="footer-links">
                <a href="https://github.com/LyferGang/Botwave">GitHub</a>
                <a href="/docs">Documentation</a>
                <a href="contact.html">Contact</a>
                <a href="privacy.html">Privacy</a>
                <a href="terms.html">Terms</a>
            </div>
        </div>
    </footer>

    <script>
        // Stripe checkout handler
        async function checkout(plan, button) {
            // Show loading state
            const originalText = button.textContent;
            button.innerHTML = '<span class="spinner"></span> Loading...';
            button.classList.add('loading');
            button.disabled = true;

            try {
                // For enterprise, redirect to contact form
                if (plan === 'enterprise') {
                    window.location.href = 'contact.html?plan=enterprise';
                    return;
                }

                // Call the API to create a checkout session
                const response = await fetch('/api/stripe/create-checkout-session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan })
                });

                const session = await response.json();

                if (session.error) {
                    throw new Error(session.error);
                }

                if (session.url) {
                    // Redirect to Stripe Checkout
                    window.location.href = session.url;
                } else {
                    throw new Error('No checkout URL returned');
                }
            } catch (error) {
                console.error('Checkout error:', error);
                alert('Unable to start checkout: ' + error.message + '. Please try again or contact support.');

                // Reset button
                button.textContent = originalText;
                button.classList.remove('loading');
                button.disabled = false;
            }
        }

        // Add smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({ behavior: 'smooth' });
            });
        });
    </script>
</body>
</html>'''

        pricing_path.write_text(pricing_html)
        self.log(f"Written: {pricing_path}")
        return True

    def create_checkout_templates(self):
        """Create checkout success and canceled templates."""
        templates_dir = self.base_path / "dashboard" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Success template
        success_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Successful | Botwave</title>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --success: #10b981;
            --bg: #0f0f23;
            --bg-card: #1a1a2e;
            --text: #ffffff;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .success-card {
            background: var(--bg-card);
            border-radius: 1.5rem;
            padding: 4rem;
            max-width: 500px;
            margin: 2rem;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .success-icon {
            font-size: 5rem;
            margin-bottom: 1.5rem;
        }
        h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--success), #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: var(--text-muted);
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 2.5rem;
            border-radius: 0.75rem;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="success-icon">✅</div>
        <h1>Payment Successful!</h1>
        <p>Thank you for subscribing to Botwave. Your account has been activated and you now have full access to the platform.</p>
        <a href="/" class="btn">Go to Dashboard</a>
    </div>
</body>
</html>'''

        (templates_dir / "checkout_success.html").write_text(success_html)
        self.log("Created: checkout_success.html")

        # Canceled template
        canceled_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Canceled | Botwave</title>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --bg: #0f0f23;
            --bg-card: #1a1a2e;
            --text: #ffffff;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .canceled-card {
            background: var(--bg-card);
            border-radius: 1.5rem;
            padding: 4rem;
            max-width: 500px;
            margin: 2rem;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .canceled-icon {
            font-size: 5rem;
            margin-bottom: 1.5rem;
        }
        h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #ef4444;
        }
        p {
            color: var(--text-muted);
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 2.5rem;
            border-radius: 0.75rem;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }
    </style>
</head>
<body>
    <div class="canceled-card">
        <div class="canceled-icon">🚫</div>
        <h1>Payment Canceled</h1>
        <p>No worries! Your payment was canceled and you weren't charged. You can try again anytime or contact us if you need help.</p>
        <a href="/pricing" class="btn">Back to Pricing</a>
    </div>
</body>
</html>'''

        (templates_dir / "checkout_canceled.html").write_text(canceled_html)
        self.log("Created: checkout_canceled.html")
        return True

    def run(self):
        """Execute all pricing updates."""
        print("=" * 60)
        print("SCRIPT KEEPER #1: PRICING + STRIPE ORCHESTRATOR")
        print("=" * 60)

        self.update_web_app()
        self.update_pricing_html()
        self.create_checkout_templates()

        print("\n" + "=" * 60)
        print("CHANGES SUMMARY:")
        print("=" * 60)
        for change in self.changes_made:
            print(f"  ✓ {change}")

        print("\n✅ PRICING ORCHESTRATOR COMPLETE")
        print("\nNext steps:")
        print("  1. Set Stripe price IDs in environment variables:")
        print("     - STRIPE_PRICE_ID_STARTER")
        print("     - STRIPE_PRICE_ID_PROFESSIONAL")
        print("     - STRIPE_PRICE_ID_ENTERPRISE")
        print("  2. Test checkout flow at /website/pricing.html")
        return True


if __name__ == "__main__":
    keeper = PricingKeeper()
    keeper.run()
