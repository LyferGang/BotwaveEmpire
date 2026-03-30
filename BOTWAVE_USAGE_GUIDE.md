# Botwave Empire - Usage Guide

**Last Updated:** 2026-03-30
**Status:** ALL SYSTEMS OPERATIONAL

---

## System Summary

| Component | Status | Details |
|-----------|--------|---------|
| **LM Studio** | RUNNING | llama-3.1-8b-instruct-abliterated-obliteratus |
| **VRAM Usage** | 5.8GB / 8GB | 2.3GB FREE - healthy headroom |
| **Dashboard** | WORKING | http://localhost:5000 |
| **Aider** | WORKING | v0.86.2 |
| **Botwave CLI** | WORKING | All commands functional |
| **Context Window** | 8192 tokens | Sufficient for chat/coding |

---

## Quick Start

### 1. Check System Status
```bash
botwave status
```

### 2. Start Dashboard
```bash
cd dashboard && python3 web_app.py
# Access at http://localhost:5000
```

### 3. Run All SCRYPT KEEPER Scripts
```bash
python3 scrypt_keeper_master.py --run-all
```

### 4. Chat with AI (Local LLM)
```bash
python3 bin/botwave-tui
```

### 5. Use Aider for Coding
```bash
aid <file.py>
```

---

## LM Studio - Model Management

### Current Setup (OPTIMIZED)
```
Loaded: llama-3.1-8b-instruct-abliterated-obliteratus (4.69 GB)
Context: 8192 tokens
VRAM: ~4.7GB used, leaving 2.3GB free for other tasks
```

### Commands
```bash
# Check status
lms status

# List available models
lms ls

# Load a model
lms load <model-name>

# Unload a model
lms unload <model-name>

# Start server
lms server start

# Stop server
lms server stop
```

### Available Models (Disk Space)
| Model | Size | Type |
|-------|------|------|
| llama-3.1-8b-instruct-abliterated-obliteratus | 4.69 GB | LOADED |
| meta-llama-3-8b-instruct | 4.92 GB | Available |
| qwen3.5-4b-uncensored-hauhaucs-aggressive | 3.38 GB | Available |
| qwen3vl-8b-uncensored-hauhaucs-balanced | 6.19 GB | Available |
| text-embedding-nomic-embed-text-v1.5 | 84 MB | Available |

---

## Botwave CLI Commands

```bash
botwave init      # Initialize new project
botwave setup     # Setup wizard
botwave status    # System status check
botwave run-agent <job.json>  # Run agent job
```

---

## Aider (AI Coding Assistant)

### Basic Usage
```bash
# Edit a file with AI
aid path/to/file.py

# With a specific request
aid file.py --message "Add error handling"

# Multiple files
aid file1.py file2.py

# Auto-accept suggestions
aid --yes file.py
```

### Self-Audit Workflow
```bash
# 1. Find issues in codebase
python3 skills/active/self-audit/audit.py --list-issues

# 2. Fix with aider
aid --yes <files>
```

---

## SCRYPT KEEPER Scripts

These scripts implement the business automation platform:

| Script | Purpose | Command |
|--------|---------|---------|
| **Pricing Keeper** | Stripe checkout, pricing tiers | `python3 scrypt_keeper_pricing.py` |
| **API Keeper** | Lead capture, customer API | `python3 scrypt_keeper_api.py` |
| **Landing Keeper** | Landing page, lead forms | `python3 scrypt_keeper_landing.py` |
| **PDF Keeper** | Report generation | `python3 scrypt_keeper_pdf.py` |
| **Master** | Run all scripts | `python3 scrypt_keeper_master.py --run-all` |

---

## Dashboard Features

Access at **http://localhost:5000**

- Lead management
- Customer portal
- Stripe checkout integration
- PDF report generation
- Real-time analytics
- Telegram notifications

---

## Telegram Integration

### Configured Bots
| Bot | Purpose | Token |
|-----|---------|-------|
| Boti1904 | Main bot | 8747407183:AAH... |
| Bot-Wave Business | Plumbing inquiries | 8611028472:AAE... |
| Captain Obvious | Foreman/internal | 8249528887:AAG... |

### Your Chat ID: 8711428786

Notifications are sent here for:
- New leads captured
- Agent job completions
- System alerts

---

## Configuration Files

### Main Config: `.env`
```bash
# LLM (Single model optimized)
LLM_API_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL=llama-3.1-8b-instruct-abliterated-obliteratus
LLM_CONTEXT_WINDOW=8192

# Telegram
TG_FOREMAN_TOKEN=8249528887:AAGjc386QGaG_-TJLkj3WOS03CYMqF0LOsc
TELEGRAM_CHAT_ID=8711428786
```

### Docker Compose: `docker-compose.yml`
```yaml
# API connects to LM Studio on host
services:
  api:
    environment:
      - LLM_API_URL=http://host.docker.internal:1234/v1
```

---

## File Structure

```
BotwaveEmpire/
├── bin/                    # CLI tools
│   ├── cli.py             # botwave command
│   ├── botwave-tui        # Chat interface
│   └── aider-audit        # Self-audit wrapper
├── dashboard/              # Web dashboard (port 5000)
│   ├── web_app.py
│   └── templates/
├── lib/                    # Core libraries
│   ├── event_handler.py   # Cron/webhook processor
│   └── agent_runner.py    # Aider runner
├── skills/active/          # Reusable skills
│   └── self-audit/        # Code audit skill
├── agent-jobs/             # Agent job queue
├── data/                   # SQLite databases
│   └── plumbing_customers.db
├── config/                 # JSON configs
│   ├── CRONS.json
│   ├── TRIGGERS.json
│   └── AGENT.md
├── *.py                    # Main scripts
└── BOTWAVE_USAGE_GUIDE.md  # This file
```

---

## Troubleshooting

### LM Studio Not Responding
```bash
# Check server
lms status

# Restart server
lms server stop
lms server start
```

### Dashboard Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process
kill $(lsof -t -i:5000)
```

### Aider Fails
```bash
# Verify LM Studio
curl http://localhost:1234/v1/models

# Check model loaded
lms status
```

### VRAM Running Low
```bash
# Check usage
nvidia-smi

# Unload models if needed
lms unload <model-name>
```

---

## Business Model (SCRYPT KEEPER)

| Plan | Price | Features |
|------|-------|----------|
| Starter | $299/mo | AI Chat, Lead Capture, Basic Reports |
| Professional | $499/mo | Multi-Agent, Portal, PDF Reports |
| Enterprise | $1,499/mo | Unlimited Agents, White-Label, Custom AI |

---

## Daily Operations

### Morning Check
```bash
botwave status
lms status
```

### Running Jobs
```bash
# Check pending jobs
python3 lib/event_handler.py status

# Run agent job
python3 lib/agent_runner.py run <job-id>
```

### Self-Audit (Weekly)
```bash
# Find code issues
python3 skills/active/self-audit/audit.py --list-issues

# Fix automatically
aid --yes <files-from-audit>
```

---

## Performance Notes

- **Single model config** saves ~2GB VRAM vs multi-model
- **8192 context** sufficient for most coding/chat tasks
- **Aider** uses ~500-1000 tokens per edit
- **Dashboard** runs lightweight on Flask
- **Telegram bots** use async to avoid blocking

---

**ALL SYSTEMS OPERATIONAL - READY FOR PRODUCTION**
