# Botwave Empire

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)]()

A professional, self-contained multi-agent automation platform for business operations.

## Architecture

Botwave follows a two-layer architecture inspired by modern agent frameworks:

```
┌─────────────────────────────────────────────────────────────────┐
│  EVENT HANDLER (API Server)                                     │
│  ├── REST API / Webhooks                                         │
│  ├── Job Queue Management                                        │
│  ├── Git MCP Server Integration                                 │
│  └── Triggers Docker Agents                                     │
├─────────────────────────────────────────────────────────────────┤
│  DOCKER AGENTS (Isolated Execution)                             │
│  ├── Business Agent - Financial/operational audits               │
│  ├── Intelligence Agent - LLM-powered analysis                 │
│  ├── Plumbing Agent - Service business automation                │
│  └── Task Executor - Generic task runner                       │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.20+
- Git 2.40+

### Installation

```bash
# Clone the repository
git clone https://github.com/LyferGang/BotwaveEmpire.git
cd BotwaveEmpire

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with your settings

# Start the system
docker-compose up -d

# Verify health
curl http://localhost:8080/health
```

## Directory Structure

```
.
├── config/              # Configuration files
│   ├── agents/          # Agent-specific settings
│   ├── skills/          # Skill configurations
│   └── .env.example     # Environment template
├── docker/              # Docker configurations
│   ├── agent/           # Agent container
│   └── api/             # API server container
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   ├── core/            # Core framework
│   ├── skills/          # Agent skills
│   └── api/             # REST API
├── .github/workflows/   # CI/CD pipelines
├── tests/               # Test suite
└── docs/                # Documentation
```

## Agents

| Agent | Purpose | Trigger |
|-------|---------|---------|
| `business` | Financial audits, compliance reports | API / Schedule |
| `plumbing` | Service quotes, customer management | API / Webhook |
| `intelligence` | LLM analysis, data processing | API / Event |
| `executor` | Generic task runner | All triggers |

## Skills

Skills extend agent capabilities:

- `database` - SQLite/PostgreSQL operations
- `llm` - Local LLM integration (LM Studio/Ollama)
- `web` - HTTP requests, webhooks
- `files` - File processing, archiving

## Configuration

All configuration is environment-driven:

```bash
# Required
LLM_API_URL=http://localhost:1234/v1
LLM_API_KEY=your-key
DATABASE_URL=sqlite:///data/botwave.db

# Optional
LOG_LEVEL=INFO
AGENT_TIMEOUT=300
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/agents` | GET | List agents |
| `/agents/{name}/run` | POST | Trigger agent |
| `/jobs` | GET | List jobs |
| `/jobs/{id}` | GET | Job status |

## Development

```bash
# Run tests
docker-compose -f docker-compose.test.yml run --rm test

# Lint code
flake8 src/
black src/

# Type check
mypy src/
```

## Security

- All secrets via environment variables
- No hardcoded credentials
- Container isolation
- Secret filtering in logs

## License

MIT License - See [LICENSE](LICENSE)
