# Botwave

> Professional AI automation platform for service businesses.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Local LLM](https://img.shields.io/badge/LLM-LM%20Studio-green.svg)](https://lmstudio.ai)

## Overview

Botwave is a production-ready multi-agent automation platform designed for service businesses that need intelligent systems running 24/7.

**What it demonstrates:**
- Enterprise-grade agent architecture
- Real-time web dashboard with live updates
- Local LLM integration (zero API costs)
- Professional secrets management
- Docker-native deployment

## Quick Look

```bash
# Start the platform
./start.sh

# Dashboard: http://localhost:5000
# API: http://localhost:8080/docs
```

## Features

| Feature | Description |
|---------|-------------|
| **Web Dashboard** | Real-time agent monitoring, task execution, live logs |
| **Multi-Agent System** | Specialized agents for different business functions |
| **Local LLM** | Runs on your hardware with LM Studio - no data leaves your network |
| **Secrets Vault** | Professional credential management with access control |
| **REST API** | Full API for integrations, webhooks, and automation |
| **Docker Ready** | Containerized for easy deployment and scaling |

## Architecture

```
┌─────────────────────────────────────────────┐
│           WEB DASHBOARD                     │
│     Real-time monitoring & control          │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│             API SERVER                      │
│         REST endpoints & webhooks           │
└─────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│Business │   │ Service  │   │Intelligence│
│ Agent   │   │  Agent   │   │   Agent   │
└─────────┘   └──────────┘   └──────────┘
```

## Installation

```bash
# Clone
git clone https://github.com/LyferGang/Botwave.git
cd Botwave

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp vault/secrets.json.example vault/secrets.json
# Edit vault/secrets.json with your LM Studio URL

# Start
./start.sh
```

## Configuration

All secrets stored in `vault/secrets.json` (gitignored):

```json
{
  "llm": {
    "local": {
      "api_url": "http://your-lm-studio:1234/v1",
      "model": "qwen3.5-4b-uncensored-hauhaucs-aggressive"
    }
  }
}
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Flask, SocketIO
- **Frontend:** Modern HTML5/CSS3, JavaScript
- **AI:** LM Studio (local), OpenRouter, Gemini, xAI
- **Database:** SQLite (portable), PostgreSQL-ready
- **Deployment:** Docker, Docker Compose

## Security

- Secrets never committed to git
- Agent-specific access control
- Non-root Docker containers
- Fail-closed validation

## License

MIT License

---

**Botwave** - Professional AI Automation
*Built for businesses that need reliable, private automation.*
