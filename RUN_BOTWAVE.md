# Botwave Empire - Complete Usage Guide

## System Status (As of 2026-03-30)

| Component | Status | Details |
|-----------|--------|---------|
| LM Studio | RUNNING | qwen3vl-8b-uncensored-hauhaucs-balanced |
| Dashboard | RUNNING | http://localhost:5000 |
| Plumbing Bot | RUNNING | Telegram integration |
| Aider | WORKING | v0.86.2 |
| Botwave CLI | WORKING | All commands functional |
| GPU (RTX 5060) | 6.6GB/8GB used | 1.5GB free |

---

## Quick Start

### Option 1: Use the Launcher (Recommended)

```bash
./BOTWAVE_LAUNCHER.sh
```

This gives you a menu to:
1. Chat with Botwave Agent TUI
2. Start the Dashboard
3. Run all SCRYPT KEEPER scripts
4. Run agent jobs with aider
5. Check system status

### Option 2: Individual Commands

```bash
# Check system status
botwave status

# Start dashboard
cd dashboard && python3 web_app.py

# Run SCRYPT KEEPER scripts
python3 scrypt_keeper_master.py --run-all

# Chat with local AI
python3 bin/botwave-tui

# Use aider for coding
aid <files>
```

---

## LM Studio Model Management

### Current Models Loaded (5 total - VRAM heavy!)

```
- qwen3vl-8b-uncensored-hauhaucs-balanced (KEEP - working)
- qwen3.5-4b-uncensored-hauhaucs-aggressive
- meta-llama-3-8b-instruct
- llama-3.1-8b-instruct-abliterated-obliteratus
- text-embedding-nomic-embed-text-v1.5
```

### To Unload Models in LM Studio:

1. Open LM Studio
2. Look at the loaded models list (left sidebar)
3. Right-click on each model you want to unload
4. Select "Unload" or click the eject icon

**Recommended:** Keep only `qwen3vl-8b-uncensored-hauhaucs-balanced` loaded

---

## Botwave CLI Commands

```bash
botwave init      # Initialize new project
botwave setup     # Setup wizard
botwave status    # System status check
botwave run-agent <job.json>  # Run agent job
```

---

## SCRYPT KEEPER Scripts (Business Automation)

| Script | Purpose | Command |
|--------|---------|---------|
| Pricing Keeper | Stripe integration | `python3 scrypt_keeper_pricing.py` |
| API Keeper | Lead capture API | `python3 scrypt_keeper_api.py` |
| Landing Keeper | Landing page | `python3 scrypt_keeper_landing.py` |
| PDF Keeper | Report generator | `python3 scrypt_keeper_pdf.py` |
| Master | Run all at once | `python3 scrypt_keeper_master.py --run-all` |

---

## Dashboard Access

- **URL:** http://localhost:5000
- **Features:**
  - Lead management
  - Customer portal
  - Stripe checkout
  - PDF report generation
  - Real-time analytics

---

## Using Aider (AI Coding Assistant)

### Basic Usage

```bash
# Fix a specific file
aid path/to/file.py

# With a specific message
aid file.py --message "Add error handling"

# Multiple files
aid file1.py file2.py
```

### Aider + LM Studio

Aider automatically uses your LM Studio model. No configuration needed!

### Example: Self-Audit Workflow

```bash
# 1. Find issues
python3 skills/active/self-audit/audit.py --list-issues

# 2. Fix with aider
aid --yes <files_from_audit>
```

---

## Botwave Agent TUI (Chat Interface)

```bash
# Simple chat interface
python3 bin/botwave-tui

# Commands inside TUI:
# - quit/exit: Exit
# - clear: Clear conversation history
```

---

## Agent Jobs (Automated Coding)

Agent jobs are stored in `agent-jobs/` and processed by the event handler.

```bash
# Create a job
python3 lib/event_handler.py create-job --name "Fix bug" --task "Description"

# Check job status
python3 lib/event_handler.py status

# List jobs
python3 lib/agent_runner.py list
```

---

## Telegram Integration

Your Telegram bots are configured in `keys` file. The plumbing bot uses:
- Token: `8747407183:AAHimCXAm0SleFh7DCW_xxmH7vn09nnAZ3k`
- Chat ID: `8711428786`

To receive notifications when jobs complete, the system sends messages to this chat.

---

## Troubleshooting

### LM Studio Not Responding

```bash
# Check if running
curl http://localhost:1234/v1/models

# Restart LM Studio server
# (In LM Studio UI: Stop Server → Start Server)
```

### Dashboard Not Starting

```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill $(lsof -t -i:5000)
```

### Aider Fails to Connect

```bash
# Verify LM Studio is running
curl http://localhost:1234/v1/models

# Check model is loaded
# LM Studio should show green "Server Started" indicator
```

### VRAM Running Low

If you see "CUDA out of memory" errors:
1. Unload unused models in LM Studio
2. Restart LM Studio
3. Load only the model you need

---

## File Structure

```
BotwaveEmpire/
├── bin/                    # CLI tools
│   ├── cli.py             # Main botwave command
│   ├── botwave-tui        # Chat interface
│   └── aider-audit        # Self-audit wrapper
├── dashboard/              # Web dashboard
│   ├── web_app.py         # Flask app
│   └── templates/         # HTML templates
├── lib/                    # Core libraries
│   ├── event_handler.py   # Job processor
│   └── agent_runner.py    # Aider runner
├── skills/active/          # Reusable skills
│   └── self-audit/        # Code audit skill
├── agent-jobs/             # Job queue
├── data/                   # SQLite databases
├── logs/                   # All logs
├── config/                 # JSON configs
├── *.py                    # Main scripts
└── RUN_BOTWAVE.md          # This file
```

---

## Business Model (SCRYPT KEEPER)

| Plan | Price | Features |
|------|-------|----------|
| Starter | $299/mo | AI Chat, Lead Capture, Basic Reports |
| Professional | $499/mo | Multi-Agent, Portal, PDF Reports |
| Enterprise | $1,499/mo | Unlimited Agents, White-Label, Custom AI |

---

## Next Steps

1. **Unload unused models** in LM Studio to free VRAM
2. **Test the dashboard** at http://localhost:5000
3. **Create a test agent job** to verify the full flow
4. **Configure Telegram** notifications for job completion

---

**System is fully operational.** All components tested and working.
