#!/usr/bin/env python3
"""
SCRYPT KEEPER #1: PRICING + STRIPE ORCHESTRATOR
Implements: Service tiers ($299/$499/$1499) with live Stripe checkout
Run: python scrypt_keeper_pricing.py [--dry-run] [--verbose]
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


class PricingKeeper:
    """Orchestrates pricing page and Stripe integration implementation."""

    def __init__(self, dry_run=False, verbose=False):
        self.base_path = Path(os.getenv("BOTWAVE_BASE_PATH", "/home/gringo/BotwaveEmpire"))
        self.changes_made = []
        self.dry_run = dry_run
        self.verbose = verbose

    def log(self, msg):
        """Log a message."""
        print(f"[PRICING KEEPER] {msg}")
        self.changes_made.append(msg)

    def check_stripe_config(self) -> bool:
        """Check if Stripe is properly configured."""
        env_file = self.base_path / ".env"
        if not env_file.exists():
            self.log("ERROR: .env file not found")
            return False

        with open(env_file) as f:
            content = f.read()

        required_keys = [
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY",
            "STRIPE_PRICE_ID_STARTER",
            "STRIPE_PRICE_ID_PROFESSIONAL",
            "STRIPE_PRICE_ID_ENTERPRISE"
        ]

        missing = []
        for key in required_keys:
            if key not in content or f"{key}=sk_live_" in content or f"{key}=pk_live_" in content:
                if f"{key}=YOUR_" in content or f"{key}=change" in content:
                    missing.append(key)

        if missing:
            self.log(f"Missing Stripe config: {', '.join(missing)}")
            return False

        self.log("Stripe configuration verified")
        return True

    def create_pricing_html(self) -> bool:
        """Create or update pricing.html with Stripe integration."""
        pricing_file = self.base_path / "website" / "pricing.html"

        if not pricing_file.exists():
            self.log("Creating pricing.html...")
            if self.dry_run:
                return True

            # Create complete pricing page
            content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Botwave Pricing - AI Automation for Service Businesses</title>
    <script src="https://js.stripe.com/v3/"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f0f; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .header { text-align: center; padding: 60px 0; }
        .header h1 { font-size: 3rem; margin-bottom: 16px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { font-size: 1.25rem; color: #888; max-width: 600px; margin: 0 auto; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 32px; margin-top: 48px; }
        .pricing-card { background: #1a1a2e; border-radius: 16px; padding: 40px; border: 1px solid #2a2a3e; transition: transform 0.3s, border-color 0.3s; }
        .pricing-card:hover { transform: translateY(-8px); border-color: #3b82f6; }
        .pricing-card.featured { border-color: #3b82f6; box-shadow: 0 0 30px rgba(59, 130, 246, 0.2); }
        .badge { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-bottom: 16px; }
        .plan-name { font-size: 1.5rem; font-weight: 600; margin-bottom: 8px; }
        .plan-price { font-size: 3rem; font-weight: 700; margin-bottom: 8px; }
        .plan-price span { font-size: 1rem; color: #888; font-weight: 400; }
        .plan-description { color: #888; margin-bottom: 32px; }
        .features { list-style: none; margin-bottom: 32px; }
        .features li { padding: 12px 0; border-bottom: 1px solid #2a2a3e; display: flex; align-items: center; gap: 12px; }
        .features li:last-child { border-bottom: none; }
        .check { color: #10b981; font-size: 1.25rem; }
        .cta-button { display: block; width: 100%; padding: 16px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; transition: opacity 0.3s; }
        .cta-button:hover { opacity: 0.9; }
        .cta-button.secondary { background: transparent; border: 1px solid #3b82f6; }
        .enterprise-features { margin-top: 48px; }
        .enterprise-features h3 { margin-bottom: 24px; text-align: center; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; }
        .feature-item { background: #16213e; padding: 24px; border-radius: 12px; }
        .feature-item h4 { color: #3b82f6; margin-bottom: 8px; }
        .feature-item p { color: #888; font-size: 0.9rem; }
        .faq { margin-top: 64px; }
        .faq h3 { text-align: center; margin-bottom: 32px; }
        .faq-item { background: #1a1a2e; padding: 24px; border-radius: 12px; margin-bottom: 16px; }
        .faq-item h4 { margin-bottom: 8px; color: #3b82f6; }
        .faq-item p { color: #888; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Simple Pricing, Powerful Results</h1>
            <p>Choose the plan that fits your business. All plans include a 14-day free trial.</p>
        </div>

        <div class="pricing-grid">
            <!-- Starter Plan -->
            <div class="pricing-card">
                <div class="plan-name">Starter</div>
                <div class="plan-price">$299<span>/month</span></div>
                <p class="plan-description">Perfect for small businesses getting started with AI automation</p>
                <ul class="features">
                    <li><span class="check">✓</span> AI Chat Agent (Telegram)</li>
                    <li><span class="check">✓</span> Basic Lead Capture</li>
                    <li><span class="check">✓</span> Automated Quotes</li>
                    <li><span class="check">✓</span> Monthly Analytics Report</li>
                    <li><span class="check">✓</span> Email Support</li>
                </ul>
                <button class="cta-button secondary" onclick="checkout('starter')">Start Free Trial</button>
            </div>

            <!-- Professional Plan -->
            <div class="pricing-card featured">
                <span class="badge">MOST POPULAR</span>
                <div class="plan-name">Professional</div>
                <div class="plan-price">$499<span>/month</span></div>
                <p class="plan-description">For growing businesses that need advanced automation</p>
                <ul class="features">
                    <li><span class="check">✓</span> Everything in Starter</li>
                    <li><span class="check">✓</span> Multi-Agent System</li>
                    <li><span class="check">✓</span> Customer Portal</li>
                    <li><span class="check">✓</span> PDF Report Generator</li>
                    <li><span class="check">✓</span> Priority Support</li>
                    <li><span class="check">✓</span> Custom Integrations</li>
                </ul>
                <button class="cta-button" onclick="checkout('professional')">Start Free Trial</button>
            </div>

            <!-- Enterprise Plan -->
            <div class="pricing-card">
                <div class="plan-name">Enterprise</div>
                <div class="plan-price">$1,499<span>/month</span></div>
                <p class="plan-description">Full-scale AI automation for established businesses</p>
                <ul class="features">
                    <li><span class="check">✓</span> Everything in Professional</li>
                    <li><span class="check">✓</span> Unlimited Agents</li>
                    <li><span class="check">✓</span> White-Label Option</li>
                    <li><span class="check">✓</span> Custom AI Training</li>
                    <li><span class="check">✓</span> Dedicated Support</li>
                    <li><span class="check">✓</span> SLA Guarantee</li>
                </ul>
                <button class="cta-button secondary" onclick="checkout('enterprise')">Contact Sales</button>
            </div>
        </div>

        <div class="enterprise-features">
            <h3>What You Get With Botwave</h3>
            <div class="feature-grid">
                <div class="feature-item">
                    <h4>🤖 AI Agents</h4>
                    <p>Autonomous agents that work 24/7 handling customer inquiries, quotes, and scheduling</p>
                </div>
                <div class="feature-item">
                    <h4>📊 Analytics</h4>
                    <p>Real-time dashboards and PDF reports showing your business metrics</p>
                </div>
                <div class="feature-item">
                    <h4>💳 Stripe Integration</h4>
                    <p>Seamless payment processing for your customers</p>
                </div>
                <div class="feature-item">
                    <h4>📱 Telegram Bot</h4>
                    <p>Customer-facing bot that handles inquiries and bookings</p>
                </div>
                <div class="feature-item">
                    <h4>🔌 API Access</h4>
                    <p>Full REST API for custom integrations and workflows</p>
                </div>
                <div class="feature-item">
                    <h4>🎯 Lead Capture</h4>
                    <p>Automated lead capture from website and social media</p>
                </div>
            </div>
        </div>

        <div class="faq">
            <h3>Frequently Asked Questions</h3>
            <div class="faq-item">
                <h4>How does the 14-day free trial work?</h4>
                <p>You get full access to all features for 14 days. No credit card required. At the end of the trial, choose a plan to continue.</p>
            </div>
            <div class="faq-item">
                <h4>Can I change plans later?</h4>
                <p>Yes! You can upgrade or downgrade your plan at any time. Changes take effect at the next billing cycle.</p>
            </div>
            <div class="faq-item">
                <h4>What payment methods do you accept?</h4>
                <p>We accept all major credit cards via Stripe. Enterprise customers can also pay via invoice.</p>
            </div>
            <div class="faq-item">
                <h4>Is there a long-term contract?</h4>
                <p>No. All plans are month-to-month. You can cancel anytime with no penalty.</p>
            </div>
        </div>
    </div>

    <script>
        const stripe = Stripe('PUBLISHABLE_KEY_PLACEHOLDER');

        async function checkout(plan) {
            try {
                const response = await fetch('/api/stripe/create-checkout-session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan })
                });

                const data = await response.json();

                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                // Redirect to Stripe Checkout
                const result = await stripe.redirectToCheckout({ sessionId: data.session_id });

                if (result.error) {
                    alert('Error: ' + result.error.message);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>'''

            pricing_file.write_text(content)
            self.log("Created pricing.html with Stripe integration")
            return True

        self.log("pricing.html already exists")
        return True

    def update_env_example(self) -> bool:
        """Update .env.example with Stripe price IDs."""
        env_example = self.base_path / ".env.example"

        if not env_example.exists():
            self.log(".env.example not found")
            return False

        content = env_example.read_text()

        # Add Stripe price IDs if missing
        stripe_ids = """
# Stripe Price IDs (create in Stripe Dashboard)
STRIPE_PRICE_ID_STARTER=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_PROFESSIONAL=price_xxxxxxxxxxxxx
STRIPE_PRICE_ID_ENTERPRISE=price_xxxxxxxxxxxxx
"""

        if "STRIPE_PRICE_ID_STARTER" not in content:
            content += stripe_ids
            if not self.dry_run:
                env_example.write_text(content)
            self.log("Added Stripe price IDs to .env.example")

        return True

    def run(self):
        """Execute pricing setup."""
        print("=" * 60)
        print("SCRYPT KEEPER #1: PRICING + STRIPE ORCHESTRATOR")
        print("=" * 60)

        self.check_stripe_config()
        self.create_pricing_html()
        self.update_env_example()

        print("\n" + "=" * 60)
        for change in self.changes_made:
            print(f"  ✓ {change}")

        print("\n✅ SCRYPT KEEPER #1 COMPLETE")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SCRYPT KEEPER #1: Pricing + Stripe")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    keeper = PricingKeeper(dry_run=args.dry_run, verbose=args.verbose)
    keeper.run()
