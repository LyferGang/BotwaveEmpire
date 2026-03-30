# CLAUDE HANDOFF - Botwave SCRYPT KEEPER Project

## Current Status
**Date:** 2026-03-30
**Session Goal:** Build Botwave AI automation platform with SCRYPT KEEPER orchestration system

## What Was Built

### 1. SCRYPT KEEPER System (5 Python Orchestrators)
| File | Purpose | Status |
|------|---------|--------|
| `scrypt_keeper_pricing.py` | $299/$499/$1499 pricing + Stripe checkout | ✅ Complete |
| `scrypt_keeper_portal.py` | Client onboarding + digital signatures | ✅ Complete |
| `scrypt_keeper_api.py` | Customer API wiring + auth | ✅ Complete |
| `scrypt_keeper_landing.py` | Landing page + lead capture | ✅ Complete |
| `scrypt_keeper_pdf.py` | PDF report generator | ✅ Complete |
| `scrypt_keeper_master.py` | Master orchestrator | ✅ Complete |

### 2. Aider Integration
- **Command:** `aid` (auto-detects LM Studio model)
- **Location:** `~/.local/bin/aid`
- **Config:** Auto-detects context length, sets map-tokens to half
- **Issue:** Models failing to load (VRAM exhausted)

### 3. LM Studio Status
```
Server: ON (port: 1234)
Loaded: qwen3.5-4b-uncensored-hauhaucs-aggressive (3.38 GB)
Context: 32K / Max: 262K
Parallel: 4
```

**Available Models:**
- llama-3.1-8b-instruct-abliterated-obliteratus (8B) - HERETIC
- meta-llama-3-8b-instruct (8B)
- qwen3.5-4b-uncensored-hauhaucs-aggressive (4B) - CURRENTLY LOADED
- qwen3vl-8b-uncensored-hauhaucs-balanced (8B) - VISION

### 4. VRAM Crisis
**Current:** 7.5GB / 8GB (92% used)
- Cosmic desktop: ~2.6GB VRAM
- LM Studio: ~4.7GB VRAM
- **Action Taken:** Installing XFCE to free VRAM

### 5. Files Created/Modified
```
website/
├── pricing.html (21KB) - Stripe integration
├── onboarding.html (36KB) - Multi-step form
├── agreement_template.html (12KB) - Digital signatures
├── onboarding_status.html (11KB) - Status tracking
└── customer_portal.html (23KB) - Client dashboard

dashboard/
└── web_app.py - Flask app with Stripe API

scrypt_keeper_*.py (6 files) - Orchestration scripts
```

### 6. Next Steps for New Claude
1. **Complete XFCE switch** - Desktop needs restart
2. **Load heretic model** - Try llama-3.1-8b-abliterated
3. **Test aider parallel** - Run `aid scrypt_keeper_*.py`
4. **Build remaining features** - API wiring, PDF generator code
5. **Integration** - Botwave agents → Claude Code → Aider loop

## Commands to Know
```bash
# LM Studio
lms server start    # Start server
lms status          # Check status
lms ps              # List loaded models
lms load <model>    # Load model

# Aider
aid                 # Launch with auto-detected model
aid --help          # Show options

# Botwave
python scrypt_keeper_master.py --run-all    # Run all scripts
python dashboard/web_app.py                  # Start dashboard
```

## Key URLs
- Dashboard: http://localhost:5000
- LM Studio API: http://localhost:1234/v1

## Business Model Reminder
- SaaS: $299-$1,499/mo
- White-label: $5K-$50K
- DFY Setup: $2K-$10K
- Total market: $200B+ AI automation

## Technical Notes
- Model context: 32K tokens
- Quantization: Q4_K_M
- Aider version: 0.86.2
- Python: 3.12.3
- GPU: RTX 5060 8GB

## Critical Issues
1. VRAM exhausted - XFCE switch in progress
2. Some models failing to load
3. Dashboard needs testing after XFCE

---
**Continue by:** Switching to XFCE, loading heretic model, testing aider
