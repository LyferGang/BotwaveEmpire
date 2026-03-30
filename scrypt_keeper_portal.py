#!/usr/bin/env python3
"""
SCRIPT KEEPER #2: CLIENT ONBOARDING PORTAL ORCHESTRATOR
Implements: Multi-step intake form + service agreement generator + digital signatures
Run: python script_keeper_portal.py
"""

import os
from pathlib import Path


class PortalKeeper:
    """Orchestrates client onboarding portal implementation."""

    def __init__(self):
        self.base_path = Path("/home/gringo/BotwaveEmpire")
        self.changes_made = []

    def log(self, msg):
        print(f"[SCRIPT KEEPER] {msg}")
        self.changes_made.append(msg)

    def create_onboarding_html(self):
        """Create website/onboarding.html - Multi-step intake form."""
        onboarding_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get Started | Botwave</title>
    <meta name="description" content="Start your AI automation journey with Botwave">
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
            --error: #ef4444;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }

        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }

        /* Header */
        .header {
            text-align: center;
            padding: 3rem 0 2rem;
            background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 60%);
        }

        .logo {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            margin-bottom: 1.5rem;
            text-decoration: none;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #fff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p { color: var(--text-muted); font-size: 1.1rem; }

        /* Progress Bar */
        .progress-container {
            margin: 2rem 0 3rem;
        }

        .progress-bar {
            display: flex;
            justify-content: space-between;
            position: relative;
            margin-bottom: 2rem;
        }

        .progress-bar::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--border);
            z-index: 0;
        }

        .progress-fill {
            position: absolute;
            top: 20px;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            z-index: 0;
            transition: width 0.5s ease;
        }

        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 1;
            cursor: pointer;
            transition: all 0.3s;
        }

        .step-circle {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--bg-card);
            border: 2px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            transition: all 0.3s;
        }

        .step.active .step-circle {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
        }

        .step.completed .step-circle {
            background: var(--accent);
            border-color: var(--accent);
        }

        .step-label {
            margin-top: 0.75rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }

        .step.active .step-label { color: var(--primary); }
        .step.completed .step-label { color: var(--accent); }

        /* Form Card */
        .form-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 1.5rem;
            padding: 2.5rem;
            margin-bottom: 2rem;
        }

        .step-content { display: none; }
        .step-content.active { display: block; animation: fadeIn 0.4s ease; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .step-title {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }

        .step-description {
            color: var(--text-muted);
            margin-bottom: 2rem;
        }

        /* Form Elements */
        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text);
        }

        .form-group label span {
            color: var(--error);
            margin-left: 2px;
        }

        .form-control {
            width: 100%;
            padding: 0.875rem 1rem;
            background: var(--bg);
            border: 2px solid var(--border);
            border-radius: 0.75rem;
            color: var(--text);
            font-size: 1rem;
            transition: all 0.3s;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }

        .form-control::placeholder { color: #64748b; }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }

        select.form-control {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394a3b8' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 1rem center;
            padding-right: 2.5rem;
        }

        textarea.form-control {
            min-height: 120px;
            resize: vertical;
        }

        /* Checkboxes */
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        @media (max-width: 600px) { .checkbox-group { grid-template-columns: 1fr; } }

        .checkbox-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 1rem;
            background: var(--bg);
            border: 2px solid var(--border);
            border-radius: 0.75rem;
            cursor: pointer;
            transition: all 0.3s;
        }

        .checkbox-item:hover {
            border-color: var(--primary);
            background: var(--bg-hover);
        }

        .checkbox-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-top: 2px;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .checkbox-content h4 {
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }

        .checkbox-content p {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        /* Budget Slider */
        .budget-display {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
            border-radius: 1rem;
            margin: 1.5rem 0;
        }

        .budget-amount {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .budget-label {
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        .budget-slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: var(--border);
            outline: none;
            -webkit-appearance: none;
            margin: 1.5rem 0;
        }

        .budget-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            cursor: pointer;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        }

        /* Radio Cards */
        .radio-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }

        @media (max-width: 600px) { .radio-cards { grid-template-columns: 1fr; } }

        .radio-card {
            position: relative;
            padding: 1.5rem;
            background: var(--bg);
            border: 2px solid var(--border);
            border-radius: 1rem;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }

        .radio-card:hover { border-color: var(--primary); }

        .radio-card input {
            position: absolute;
            opacity: 0;
        }

        .radio-card.selected {
            border-color: var(--primary);
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        }

        .radio-card .icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
        }

        .radio-card h4 { font-size: 1rem; margin-bottom: 0.25rem; }
        .radio-card p { font-size: 0.85rem; color: var(--text-muted); }

        /* Buttons */
        .btn-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }

        .btn {
            flex: 1;
            padding: 1rem 2rem;
            border-radius: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            text-align: center;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }

        .btn-secondary {
            background: transparent;
            color: var(--text);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            background: var(--bg-hover);
            border-color: var(--primary);
        }

        /* Summary */
        .summary-section {
            background: var(--bg);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .summary-section h4 {
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .summary-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
        }

        .summary-row:last-child { border-bottom: none; }

        .summary-label { color: var(--text-muted); }
        .summary-value { font-weight: 500; }

        /* Success State */
        .success-state {
            text-align: center;
            padding: 3rem 2rem;
        }

        .success-icon {
            font-size: 5rem;
            margin-bottom: 1.5rem;
        }

        .success-state h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--accent), #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .success-state p {
            color: var(--text-muted);
            margin-bottom: 2rem;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }

        .next-steps {
            text-align: left;
            background: var(--bg);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-top: 2rem;
        }

        .next-steps h4 {
            margin-bottom: 1rem;
            color: var(--text);
        }

        .next-steps ol {
            margin-left: 1.5rem;
            color: var(--text-muted);
        }

        .next-steps li {
            margin-bottom: 0.75rem;
        }

        /* Error Message */
        .error-message {
            color: var(--error);
            font-size: 0.875rem;
            margin-top: 0.5rem;
            display: none;
        }

        .form-group.has-error .form-control { border-color: var(--error); }
        .form-group.has-error .error-message { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <a href="index.html" class="logo">Botwave</a>
        <h1>Get Started</h1>
        <p>Complete the form below and we'll create your custom AI automation plan</p>
    </div>

    <div class="container">
        <!-- Progress Bar -->
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                <div class="step active" data-step="1">
                    <div class="step-circle">1</div>
                    <span class="step-label">Business</span>
                </div>
                <div class="step" data-step="2">
                    <div class="step-circle">2</div>
                    <span class="step-label">Services</span>
                </div>
                <div class="step" data-step="3">
                    <div class="step-circle">3</div>
                    <span class="step-label">Budget</span>
                </div>
                <div class="step" data-step="4">
                    <div class="step-circle">4</div>
                    <span class="step-label">Timeline</span>
                </div>
                <div class="step" data-step="5">
                    <div class="step-circle">5</div>
                    <span class="step-label">Review</span>
                </div>
            </div>
        </div>

        <!-- Form -->
        <form id="onboardingForm" class="form-card">
            <!-- Step 1: Business Information -->
            <div class="step-content active" data-step="1">
                <h2 class="step-title">Business Information</h2>
                <p class="step-description">Tell us about your company so we can customize your experience.</p>

                <div class="form-row">
                    <div class="form-group">
                        <label>Company Name <span>*</span></label>
                        <input type="text" class="form-control" id="companyName" placeholder="Acme Inc." required>
                        <span class="error-message">Please enter your company name</span>
                    </div>
                    <div class="form-group">
                        <label>Industry <span>*</span></label>
                        <select class="form-control" id="industry" required>
                            <option value="">Select industry</option>
                            <option value="technology">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                            <option value="retail">Retail</option>
                            <option value="manufacturing">Manufacturing</option>
                            <option value="services">Professional Services</option>
                            <option value="other">Other</option>
                        </select>
                        <span class="error-message">Please select an industry</span>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Contact Name <span>*</span></label>
                        <input type="text" class="form-control" id="contactName" placeholder="John Doe" required>
                        <span class="error-message">Please enter your name</span>
                    </div>
                    <div class="form-group">
                        <label>Company Size</label>
                        <select class="form-control" id="companySize">
                            <option value="">Select size</option>
                            <option value="1-10">1-10 employees</option>
                            <option value="11-50">11-50 employees</option>
                            <option value="51-200">51-200 employees</option>
                            <option value="201-500">201-500 employees</option>
                            <option value="500+">500+ employees</option>
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Email <span>*</span></label>
                        <input type="email" class="form-control" id="email" placeholder="john@company.com" required>
                        <span class="error-message">Please enter a valid email</span>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" class="form-control" id="phone" placeholder="(555) 123-4567">
                    </div>
                </div>

                <div class="form-group">
                    <label>Current Challenges</label>
                    <textarea class="form-control" id="challenges" placeholder="What challenges are you facing that AI automation could help solve?"></textarea>
                </div>

                <div class="btn-group">
                    <div></div>
                    <button type="button" class="btn btn-primary" onclick="nextStep()">Next Step →</button>
                </div>
            </div>

            <!-- Step 2: Service Needs -->
            <div class="step-content" data-step="2">
                <h2 class="step-title">Service Needs</h2>
                <p class="step-description">Select the AI automation services you're interested in.</p>

                <div class="form-group">
                    <label>Which services do you need? <span>*</span></label>
                    <div class="checkbox-group">
                        <label class="checkbox-item">
                            <input type="checkbox" name="services" value="business_automation">
                            <div class="checkbox-content">
                                <h4>Business Process Automation</h4>
                                <p>Automate workflows, reports, and compliance</p>
                            </div>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" name="services" value="customer_service">
                            <div class="checkbox-content">
                                <h4>Customer Service Automation</h4>
                                <p>AI chatbots, ticket routing, response automation</p>
                            </div>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" name="services" value="intelligence">
                            <div class="checkbox-content">
                                <h4>Intelligence & Analytics</h4>
                                <p>Data analysis, predictive insights, dashboards</p>
                            </div>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" name="services" value="system_optimization">
                            <div class="checkbox-content">
                                <h4>System Optimization</h4>
                                <p>Performance tuning, cleanup, maintenance</p>
                            </div>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Specific Requirements</label>
                    <textarea class="form-control" id="requirements" placeholder="Describe any specific requirements or integrations you need..."></textarea>
                </div>

                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="prevStep()">← Back</button>
                    <button type="button" class="btn btn-primary" onclick="nextStep()">Next Step →</button>
                </div>
            </div>

            <!-- Step 3: Budget -->
            <div class="step-content" data-step="3">
                <h2 class="step-title">Budget</h2>
                <p class="step-description">Help us understand your investment range.</p>

                <div class="budget-display">
                    <div class="budget-amount" id="budgetDisplay">$5,000</div>
                    <div class="budget-label">Monthly Budget</div>
                </div>

                <div class="form-group">
                    <input type="range" class="budget-slider" id="budgetSlider" min="1000" max="50000" step="1000" value="5000">
                </div>

                <div class="form-group">
                    <label>Billing Cycle</label>
                    <div class="radio-cards">
                        <label class="radio-card" onclick="selectBilling(this, 'monthly')">
                            <input type="radio" name="billing" value="monthly" checked>
                            <div class="icon">📅</div>
                            <h4>Monthly</h4>
                            <p>Pay as you go</p>
                        </label>
                        <label class="radio-card selected" onclick="selectBilling(this, 'annual')">
                            <input type="radio" name="billing" value="annual" checked>
                            <div class="icon">🎉</div>
                            <h4>Annual</h4>
                            <p>Save 20%</p>
                        </label>
                        <label class="radio-card" onclick="selectBilling(this, 'enterprise')">
                            <input type="radio" name="billing" value="enterprise">
                            <div class="icon">🏢</div>
                            <h4>Enterprise</h4>
                            <p>Custom pricing</p>
                        </label>
                    </div>
                </div>

                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="prevStep()">← Back</button>
                    <button type="button" class="btn btn-primary" onclick="nextStep()">Next Step →</button>
                </div>
            </div>

            <!-- Step 4: Timeline -->
            <div class="step-content" data-step="4">
                <h2 class="step-title">Timeline</h2>
                <p class="step-description">When would you like to get started?</p>

                <div class="form-group">
                    <label>Desired Timeline</label>
                    <div class="radio-cards">
                        <label class="radio-card" onclick="selectTimeline(this, 'immediate')">
                            <input type="radio" name="timeline" value="immediate">
                            <div class="icon">⚡</div>
                            <h4>Immediate</h4>
                            <p>ASAP</p>
                        </label>
                        <label class="radio-card selected" onclick="selectTimeline(this, '1month')">
                            <input type="radio" name="timeline" value="1month" checked>
                            <div class="icon">📅</div>
                            <h4>1 Month</h4>
                            <p>Standard onboarding</p>
                        </label>
                        <label class="radio-card" onclick="selectTimeline(this, 'flexible')">
                            <input type="radio" name="timeline" value="flexible">
                            <div class="icon">🤝</div>
                            <h4>Flexible</h4>
                            <p>When ready</p>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Additional Notes</label>
                    <textarea class="form-control" id="notes" placeholder="Any other details you'd like to share..."></textarea>
                </div>

                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="prevStep()">← Back</button>
                    <button type="button" class="btn btn-primary" onclick="nextStep()">Review →</button>
                </div>
            </div>

            <!-- Step 5: Review -->
            <div class="step-content" data-step="5">
                <h2 class="step-title">Review Your Information</h2>
                <p class="step-description">Please review your details before submitting.</p>

                <div class="summary-section">
                    <h4>🏢 Business Information</h4>
                    <div class="summary-row">
                        <span class="summary-label">Company</span>
                        <span class="summary-value" id="summaryCompany">-</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Industry</span>
                        <span class="summary-value" id="summaryIndustry">-</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Contact</span>
                        <span class="summary-value" id="summaryContact">-</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Email</span>
                        <span class="summary-value" id="summaryEmail">-</span>
                    </div>
                </div>

                <div class="summary-section">
                    <h4>🔧 Services</h4>
                    <div class="summary-row">
                        <span class="summary-label">Selected</span>
                        <span class="summary-value" id="summaryServices">-</span>
                    </div>
                </div>

                <div class="summary-section">
                    <h4>💰 Budget & Timeline</h4>
                    <div class="summary-row">
                        <span class="summary-label">Budget</span>
                        <span class="summary-value" id="summaryBudget">-</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Billing</span>
                        <span class="summary-value" id="summaryBilling">-</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Timeline</span>
                        <span class="summary-value" id="summaryTimeline">-</span>
                    </div>
                </div>

                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="prevStep()">← Back</button>
                    <button type="submit" class="btn btn-primary" onclick="submitForm(event)">Submit Application ✓</button>
                </div>
            </div>

            <!-- Success State -->
            <div class="step-content" data-step="success" style="display: none;">
                <div class="success-state">
                    <div class="success-icon">🎉</div>
                    <h2>Application Submitted!</h2>
                    <p>Thank you for your interest in Botwave. Our team will review your application and get back to you within 24 hours with a customized proposal.</p>

                    <a href="agreement_template.html" class="btn btn-primary">Preview Service Agreement</a>

                    <div class="next-steps">
                        <h4>What happens next?</h4>
                        <ol>
                            <li>Our team reviews your requirements (within 24 hours)</li>
                            <li>You'll receive a customized proposal via email</li>
                            <li>Review and sign the service agreement</li>
                            <li>We schedule your kickoff call</li>
                            <li>Your AI agents go live!</li>
                        </ol>
                    </div>
                </div>
            </div>
        </form>
    </div>

    <script>
        let currentStep = 1;
        const totalSteps = 5;

        // Budget slider
        const budgetSlider = document.getElementById('budgetSlider');
        const budgetDisplay = document.getElementById('budgetDisplay');

        budgetSlider.addEventListener('input', function() {
            budgetDisplay.textContent = '$' + parseInt(this.value).toLocaleString();
        });

        // Step navigation
        function updateProgress() {
            const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
            document.getElementById('progressFill').style.width = progress + '%';

            document.querySelectorAll('.step').forEach((step, index) => {
                const stepNum = index + 1;
                step.classList.remove('active', 'completed');

                if (stepNum === currentStep) {
                    step.classList.add('active');
                } else if (stepNum < currentStep) {
                    step.classList.add('completed');
                    step.querySelector('.step-circle').textContent = '✓';
                } else {
                    step.querySelector('.step-circle').textContent = stepNum;
                }
            });

            document.querySelectorAll('.step-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelector(`.step-content[data-step="${currentStep}"]`).classList.add('active');
        }

        function nextStep() {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    if (currentStep === 5) updateSummary();
                    updateProgress();
                }
            }
        }

        function prevStep() {
            if (currentStep > 1) {
                currentStep--;
                updateProgress();
            }
        }

        function validateStep(step) {
            let valid = true;
            const currentContent = document.querySelector(`.step-content[data-step="${step}"]`);

            currentContent.querySelectorAll('[required]').forEach(field => {
                const group = field.closest('.form-group');
                if (!field.value.trim()) {
                    group.classList.add('has-error');
                    valid = false;
                } else {
                    group.classList.remove('has-error');
                }
            });

            return valid;
        }

        // Click on completed steps
        document.querySelectorAll('.step').forEach(step => {
            step.addEventListener('click', function() {
                const stepNum = parseInt(this.dataset.step);
                if (this.classList.contains('completed')) {
                    currentStep = stepNum;
                    updateProgress();
                }
            });
        });

        // Radio card selection
        function selectBilling(card, value) {
            card.closest('.form-group').querySelectorAll('.radio-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            card.querySelector('input').checked = true;
        }

        function selectTimeline(card, value) {
            card.closest('.form-group').querySelectorAll('.radio-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            card.querySelector('input').checked = true;
        }

        // Update summary
        function updateSummary() {
            document.getElementById('summaryCompany').textContent = document.getElementById('companyName').value || '-';
            document.getElementById('summaryIndustry').textContent = document.getElementById('industry').value || '-';
            document.getElementById('summaryContact').textContent = document.getElementById('contactName').value || '-';
            document.getElementById('summaryEmail').textContent = document.getElementById('email').value || '-';

            const services = Array.from(document.querySelectorAll('input[name="services"]:checked'))
                .map(cb => cb.closest('.checkbox-content').querySelector('h4').textContent)
                .join(', ') || '-';
            document.getElementById('summaryServices').textContent = services;

            document.getElementById('summaryBudget').textContent = '$' + parseInt(budgetSlider.value).toLocaleString() + '/month';

            const billing = document.querySelector('input[name="billing"]:checked').value;
            document.getElementById('summaryBilling').textContent = billing.charAt(0).toUpperCase() + billing.slice(1);

            const timeline = document.querySelector('input[name="timeline"]:checked').value;
            document.getElementById('summaryTimeline').textContent = timeline === '1month' ? '1 Month' :
                timeline.charAt(0).toUpperCase() + timeline.slice(1);
        }

        // Form submission
        async function submitForm(e) {
            e.preventDefault();

            const formData = {
                companyName: document.getElementById('companyName').value,
                industry: document.getElementById('industry').value,
                contactName: document.getElementById('contactName').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                companySize: document.getElementById('companySize').value,
                challenges: document.getElementById('challenges').value,
                services: Array.from(document.querySelectorAll('input[name="services"]:checked')).map(cb => cb.value),
                requirements: document.getElementById('requirements').value,
                budget: budgetSlider.value,
                billing: document.querySelector('input[name="billing"]:checked').value,
                timeline: document.querySelector('input[name="timeline"]:checked').value,
                notes: document.getElementById('notes').value
            };

            // Save to localStorage
            localStorage.setItem('onboardingData', JSON.stringify(formData));

            // Show success
            document.querySelectorAll('.step-content').forEach(c => c.classList.remove('active'));
            document.querySelector('.step-content[data-step="success"]').style.display = 'block';

            // In production, send to API
            // await fetch('/api/onboarding/submit', { method: 'POST', body: JSON.stringify(formData) });
        }

        // Load saved data
        const savedData = localStorage.getItem('onboardingData');
        if (savedData) {
            const data = JSON.parse(savedData);
            document.getElementById('companyName').value = data.companyName || '';
            document.getElementById('industry').value = data.industry || '';
            document.getElementById('contactName').value = data.contactName || '';
            document.getElementById('email').value = data.email || '';
        }
    </script>
</body>
</html>'''

        onboarding_path = self.base_path / "website" / "onboarding.html"
        onboarding_path.write_text(onboarding_html)
        self.log(f"Created: {onboarding_path}")
        return True

    def create_agreement_template(self):
        """Create website/agreement_template.html - Service agreement with digital signature."""
        agreement_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Agreement | Botwave</title>
    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.1.7/dist/signature_pad.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --bg: #0f0f23;
            --bg-card: #1a1a2e;
            --text: #ffffff;
            --text-muted: #94a3b8;
            --border: #333355;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        .agreement-header {
            text-align: center;
            padding: 2rem 0;
            border-bottom: 2px solid var(--border);
            margin-bottom: 2rem;
        }

        .logo {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .agreement-title {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }

        .agreement-date {
            color: var(--text-muted);
        }

        .agreement-content {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .section {
            margin-bottom: 1.5rem;
        }

        .section h3 {
            color: var(--primary);
            margin-bottom: 0.75rem;
            font-size: 1.1rem;
        }

        .section p {
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .client-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            background: var(--bg);
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
        }

        .info-label {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .info-value {
            font-weight: 500;
        }

        /* Signature */
        .signature-section {
            margin-top: 2rem;
        }

        .signature-pad-container {
            background: white;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }

        #signature-pad {
            width: 100%;
            height: 200px;
            border-radius: 0.5rem;
            cursor: crosshair;
        }

        .signature-actions {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-secondary {
            background: var(--bg-hover);
            color: var(--text);
            border: 1px solid var(--border);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        }

        .btn-success {
            background: #10b981;
            color: white;
        }

        /* Terms */
        .terms-list {
            list-style: none;
            margin: 1rem 0;
        }

        .terms-list li {
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: var(--text-muted);
        }

        .terms-list li::before {
            content: '•';
            position: absolute;
            left: 0;
            color: var(--primary);
        }

        .checkbox-confirm {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin: 1.5rem 0;
            padding: 1rem;
            background: var(--bg);
            border-radius: 0.5rem;
            cursor: pointer;
        }

        .checkbox-confirm input {
            margin-top: 4px;
            accent-color: var(--primary);
        }

        .checkbox-confirm label {
            cursor: pointer;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="agreement-header">
            <div class="logo">Botwave</div>
            <h1 class="agreement-title">Service Agreement</h1>
            <p class="agreement-date">Effective Date: <span id="effectiveDate"></span></p>
        </div>

        <div class="agreement-content">
            <div class="section">
                <h3>1. Parties</h3>
                <p>This Service Agreement is entered into between:</p>
                <div class="client-info">
                    <div>
                        <div class="info-row">
                            <span class="info-label">Company:</span>
                            <span class="info-value" id="clientCompany">Client Company</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Contact:</span>
                            <span class="info-value" id="clientName">Contact Name</span>
                        </div>
                    </div>
                    <div>
                        <div class="info-row">
                            <span class="info-label">Email:</span>
                            <span class="info-value" id="clientEmail">email@company.com</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Date:</span>
                            <span class="info-value" id="agreementDate"></span>
                        </div>
                    </div>
                </div>
                <p>And <strong>Botwave</strong>, an AI automation services provider.</p>
            </div>

            <div class="section">
                <h3>2. Services</h3>
                <p>Botwave agrees to provide the following AI automation services:</p>
                <ul class="terms-list" id="servicesList">
                    <li>Business process automation and optimization</li>
                    <li>AI agent development and deployment</li>
                    <li>System monitoring and maintenance</li>
                    <li>Technical support and consulting</li>
                </ul>
            </div>

            <div class="section">
                <h3>3. Terms & Conditions</h3>
                <ul class="terms-list">
                    <li>Service term: Monthly/Annual subscription as selected</li>
                    <li>Payment terms: Due upon invoice receipt</li>
                    <li>Cancellation: 30 days written notice required</li>
                    <li>Data ownership: Client retains all data ownership</li>
                    <li>Confidentiality: Both parties agree to NDA terms</li>
                    <li>Limitation of liability: As per standard commercial terms</li>
                </ul>
            </div>

            <div class="section">
                <h3>4. Signatures</h3>
                <p>By signing below, both parties agree to the terms of this agreement.</p>

                <div class="signature-section">
                    <p><strong>Client Signature:</strong></p>
                    <div class="signature-pad-container">
                        <canvas id="signature-pad"></canvas>
                    </div>
                    <div class="signature-actions">
                        <button class="btn btn-secondary" onclick="clearSignature()">Clear</button>
                        <button class="btn btn-primary" onclick="downloadPDF()">Download PDF</button>
                    </div>
                </div>

                <label class="checkbox-confirm">
                    <input type="checkbox" id="agreeTerms">
                    <label for="agreeTerms">I have read and agree to the terms of this Service Agreement</label>
                </label>

                <button class="btn btn-success" style="width: 100%; margin-top: 1rem;" onclick="submitAgreement()">
                    Sign Agreement ✓
                </button>
            </div>
        </div>
    </div>

    <script>
        // Set dates
        const today = new Date();
        document.getElementById('effectiveDate').textContent = today.toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });
        document.getElementById('agreementDate').textContent = today.toLocaleDateString();

        // Load client data from localStorage
        const onboardingData = localStorage.getItem('onboardingData');
        if (onboardingData) {
            const data = JSON.parse(onboardingData);
            document.getElementById('clientCompany').textContent = data.companyName || 'Client Company';
            document.getElementById('clientName').textContent = data.contactName || 'Contact Name';
            document.getElementById('clientEmail').textContent = data.email || 'email@company.com';
        }

        // Initialize signature pad
        const canvas = document.getElementById('signature-pad');
        const signaturePad = new SignaturePad(canvas, {
            backgroundColor: 'rgb(255, 255, 255)',
            penColor: 'rgb(0, 0, 0)'
        });

        // Resize canvas
        function resizeCanvas() {
            const ratio = Math.max(window.devicePixelRatio || 1, 1);
            canvas.width = canvas.offsetWidth * ratio;
            canvas.height = canvas.offsetHeight * ratio;
            canvas.getContext('2d').scale(ratio, ratio);
            signaturePad.clear();
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function clearSignature() {
            signaturePad.clear();
        }

        function downloadPDF() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // Add content
            doc.setFontSize(20);
            doc.text('Botwave Service Agreement', 20, 30);

            doc.setFontSize(12);
            doc.text(`Client: ${document.getElementById('clientCompany').textContent}`, 20, 50);
            doc.text(`Date: ${document.getElementById('agreementDate').textContent}`, 20, 60);

            // Add signature if exists
            if (!signaturePad.isEmpty()) {
                const signatureData = signaturePad.toDataURL();
                doc.addImage(signatureData, 'PNG', 20, 100, 80, 40);
            }

            doc.save('Botwave_Service_Agreement.pdf');
        }

        function submitAgreement() {
            if (!document.getElementById('agreeTerms').checked) {
                alert('Please agree to the terms before signing');
                return;
            }

            if (signaturePad.isEmpty()) {
                alert('Please sign the agreement');
                return;
            }

            // Save signature
            const signatureData = signaturePad.toDataURL();
            localStorage.setItem('agreementSignature', signatureData);

            alert('Agreement signed successfully! Redirecting to status page...');
            window.location.href = 'onboarding_status.html';
        }
    </script>
</body>
</html>'''

        agreement_path = self.base_path / "website" / "agreement_template.html"
        agreement_path.write_text(agreement_html)
        self.log(f"Created: {agreement_path}")
        return True

    def create_status_page(self):
        """Create website/onboarding_status.html - Status tracking page."""
        status_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Status | Botwave</title>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --accent: #10b981;
            --bg: #0f0f23;
            --bg-card: #1a1a2e;
            --text: #ffffff;
            --text-muted: #94a3b8;
            --border: #333355;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }

        .container {
            max-width: 700px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            padding: 2rem 0;
        }

        .logo {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 1.5rem;
        }

        .status-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 1.5rem;
            padding: 2.5rem;
            margin-bottom: 2rem;
        }

        .application-id {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 2rem;
            font-weight: 600;
            font-size: 0.95rem;
        }

        .status-review {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }

        .status-proposal {
            background: rgba(99, 102, 241, 0.2);
            color: var(--primary);
        }

        .status-signed {
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent);
        }

        .status-complete {
            background: rgba(16, 185, 129, 0.3);
            color: var(--accent);
        }

        /* Timeline */
        .timeline {
            margin: 2rem 0;
        }

        .timeline-item {
            display: flex;
            gap: 1.5rem;
            padding: 1.5rem 0;
            border-bottom: 1px solid var(--border);
            position: relative;
        }

        .timeline-item:last-child {
            border-bottom: none;
        }

        .timeline-icon {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }

        .timeline-icon.completed {
            background: var(--accent);
        }

        .timeline-icon.active {
            background: var(--primary);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
        }

        .timeline-icon.pending {
            background: var(--bg);
            border: 2px solid var(--border);
        }

        .timeline-content h4 {
            margin-bottom: 0.25rem;
        }

        .timeline-content p {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .timeline-date {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-left: auto;
        }

        /* Action Items */
        .actions-section {
            margin-top: 2rem;
        }

        .actions-section h3 {
            margin-bottom: 1rem;
        }

        .action-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .btn {
            padding: 0.875rem 1.5rem;
            border-radius: 0.75rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        }

        .btn-secondary {
            background: var(--bg);
            color: var(--text);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--primary);
        }

        /* Contact */
        .contact-section {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
        }

        .contact-section a {
            color: var(--primary);
            text-decoration: none;
        }

        .contact-section a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="index.html" class="logo">Botwave</a>
        </div>

        <div class="status-card">
            <div class="application-id">Application ID: <strong id="appId">BW-2026-0001</strong></div>

            <div style="text-align: center; margin-bottom: 2rem;">
                <span class="status-badge status-review" id="statusBadge">🕐 Under Review</span>
            </div>

            <div class="timeline" id="timeline">
                <div class="timeline-item">
                    <div class="timeline-icon completed">✓</div>
                    <div class="timeline-content">
                        <h4>Application Submitted</h4>
                        <p>Your onboarding form has been received</p>
                    </div>
                    <div class="timeline-date" id="submitDate">Today</div>
                </div>

                <div class="timeline-item">
                    <div class="timeline-icon active">🔄</div>
                    <div class="timeline-content">
                        <h4>Under Review</h4>
                        <p>Our team is reviewing your requirements</p>
                    </div>
                    <div class="timeline-date">In progress</div>
                </div>

                <div class="timeline-item">
                    <div class="timeline-icon pending">📋</div>
                    <div class="timeline-content">
                        <h4>Proposal Sent</h4>
                        <p>Custom proposal with pricing and timeline</p>
                    </div>
                    <div class="timeline-date">Pending</div>
                </div>

                <div class="timeline-item">
                    <div class="timeline-icon pending">✍️</div>
                    <div class="timeline-content">
                        <h4>Agreement Signed</h4>
                        <p>Service agreement executed</p>
                    </div>
                    <div class="timeline-date">Pending</div>
                </div>

                <div class="timeline-item">
                    <div class="timeline-icon pending">🚀</div>
                    <div class="timeline-content">
                        <h4>Onboarding Complete</h4>
                        <p>Your AI agents are live!</p>
                    </div>
                    <div class="timeline-date">Pending</div>
                </div>
            </div>

            <div class="actions-section">
                <h3>Actions Required</h3>
                <div class="action-buttons">
                    <a href="agreement_template.html" class="btn btn-primary" id="signAgreementBtn" style="display: none;">
                        Sign Agreement
                    </a>
                    <a href="onboarding.html" class="btn btn-secondary">Edit Application</a>
                    <a href="contact.html" class="btn btn-secondary">Contact Support</a>
                </div>
            </div>
        </div>

        <div class="contact-section">
            <p>Questions? Email us at <a href="mailto:support@botwave.ai">support@botwave.ai</a></p>
        </div>
    </div>

    <script>
        // Set submit date
        const today = new Date();
        document.getElementById('submitDate').textContent = today.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric'
        });

        // Generate application ID
        const appId = 'BW-' + today.getFullYear() + '-' + Math.random().toString(36).substr(2, 6).toUpperCase();
        document.getElementById('appId').textContent = appId;

        // Simulate status updates (in production, fetch from API)
        const urlParams = new URLSearchParams(window.location.search);
        const status = urlParams.get('status') || 'review';

        const statusConfig = {
            review: { badge: 'Under Review', class: 'status-review', icon: '🔄' },
            proposal: { badge: 'Proposal Sent', class: 'status-proposal', icon: '📋' },
            signed: { badge: 'Agreement Signed', class: 'status-signed', icon: '✍️' },
            complete: { badge: 'Complete', class: 'status-complete', icon: '✅' }
        };

        if (statusConfig[status]) {
            const badge = document.getElementById('statusBadge');
            badge.textContent = statusConfig[status].icon + ' ' + statusConfig[status].badge;
            badge.className = 'status-badge ' + statusConfig[status].class;

            // Show sign button when proposal is sent
            if (status === 'proposal') {
                document.getElementById('signAgreementBtn').style.display = 'inline-flex';
            }
        }

        // Load from localStorage to check if agreement signed
        if (localStorage.getItem('agreementSignature')) {
            document.getElementById('signAgreementBtn').textContent = 'View Signed Agreement';
        }
    </script>
</body>
</html>'''

        status_path = self.base_path / "website" / "onboarding_status.html"
        status_path.write_text(status_html)
        self.log(f"Created: {status_path}")
        return True

    def run(self):
        """Execute all portal creation tasks."""
        print("=" * 60)
        print("SCRIPT KEEPER #2: CLIENT ONBOARDING PORTAL ORCHESTRATOR")
        print("=" * 60)

        self.create_onboarding_html()
        self.create_agreement_template()
        self.create_status_page()

        print("\n" + "=" * 60)
        print("CHANGES SUMMARY:")
        print("=" * 60)
        for change in self.changes_made:
            print(f"  ✓ {change}")

        print("\n✅ PORTAL ORCHESTRATOR COMPLETE")
        print("\nFiles created:")
        print("  - website/onboarding.html (Multi-step intake form)")
        print("  - website/agreement_template.html (Digital signatures)")
        print("  - website/onboarding_status.html (Status tracking)")
        return True


if __name__ == "__main__":
    keeper = PortalKeeper()
    keeper.run()
