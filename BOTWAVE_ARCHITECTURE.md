# Botwave Architecture

**Botwave = thepopebot architecture × local LLM stack**

## Overview

Botwave is an autonomous AI agent system modeled after [thepopebot](https://github.com/stephengpope/thepopebot), but built for local LLM execution using LM Studio + aider instead of cloud APIs.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌─────────────────┐         ┌─────────────────┐                     │
│  │ Event Handler   │ ──1──►  │  agent-jobs/    │                     │
│  │ (cron/webhook)  │         │  (job branch)   │                     │
│  └────────▲────────┘         └─────────────────┘                     │
│           │                                                          │
│           │  2 (launches aider + LM Studio)                          │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │  aider + LM     │                                                 │
│  │  Studio (local) │                                                 │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           │  3 (commits changes)                                     │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │  Git Repo       │                                                 │
│  │  (PR optional)  │                                                 │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           │  4 (notify complete)                                     │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                 │
│  │  Telegram/Email │                                                 │
│  │  Notification   │                                                 │
│  └─────────────────┘                                                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. CLI (`bin/cli.py`)

Command-line interface for managing Botwave:

```bash
botwave init          # Initialize project
botwave setup         # Setup wizard
botwave status        # System status
botwave run-agent     # Run agent job
```

### 2. Event Handler (`lib/event_handler.py`)

Processes triggers and creates agent jobs:

- **Cron jobs**: Scheduled tasks from `config/CRONS.json`
- **Webhooks**: HTTP triggers from `config/TRIGGERS.json`
- **Manual jobs**: Direct job creation via CLI

### 3. Agent Runner

Uses the `aid` command to execute coding tasks:

- Loads LM Studio model via local API
- Runs aider with job instructions
- Logs all output to `logs/job_<id>/`

### 4. Configuration

| File | Purpose |
|------|---------|
| `config/CRONS.json` | Scheduled jobs |
| `config/TRIGGERS.json` | Webhook triggers |
| `config/AGENT.md` | Agent instructions |
| `.env` | Environment variables |

## Key Differences from thepopebot

| Feature | thepopebot | Botwave |
|---------|------------|---------|
| Language | Node.js/Next.js | Python/Flask |
| LLM | Claude API (remote) | LM Studio (local) |
| Agent | Docker container | aider CLI |
| Auth | NextAuth + sessions | API keys + Telegram |
| Database | SQLite + Drizzle | SQLite native |

## Job Flow

1. **Create**: Event handler creates job file in `agent-jobs/`
2. **Instructions**: Generates markdown instruction file
3. **Execute**: Launches `aid <instructions>` command
4. **Log**: All output goes to `logs/job_<id>/aider.log`
5. **Complete**: Job status updated to `completed` or `failed`

## Example: Creating a Job

```python
from lib.event_handler import EventHandler

handler = EventHandler()

# Create a job
job_id = handler.create_job(
    name="Fix pricing page",
    task="Update the pricing page with new tiers",
    files=["website/pricing.html"]
)

# Run the job
handler.run_job(job_id)
```

## Example: Webhook Trigger

```bash
# Send webhook
curl -X POST http://localhost:8080/webhook/new-lead \
  -H "X-Secret: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone": "555-1234"}'
```

## Security Notes

- Webhook secrets are required for all triggers
- API keys stored in `.env` (never commit)
- Job logs may contain sensitive data
- Run `botwave status` to check running services

## Getting Started

1. **Start LM Studio**: Load a model and start server on port 1234
2. **Initialize**: `botwave init`
3. **Setup**: `botwave setup`
4. **Check status**: `botwave status`
5. **Run a job**: `botwave run-agent job.json`

## Future Enhancements

- [ ] Git branch-per-job workflow (like thepopebot)
- [ ] Auto-PR creation and merge
- [ ] Telegram notifications on job complete
- [ ] Multi-agent clusters
- [ ] Skill system for reusable capabilities
- [ ] Docker container isolation for jobs
