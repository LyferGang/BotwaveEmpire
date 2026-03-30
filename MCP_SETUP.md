# Botwave MCP Server Setup

## What This Is

MCP (Model Context Protocol) server that gives **you** (the developer) access to Botwave agents directly inside Claude Code - just like you use Claude Code now, but with your local LM Studio model.

## Configuration Added

Your `~/.claude/settings.json` now has:

```json
{
  "mcpServers": {
    "botwave": {
      "command": "python3",
      "args": ["/home/gringo/BotwaveEmpire/mcp/botwave-mcp-server.py"]
    }
  }
}
```

## Available Tools

Once Claude Code restarts, you can use these tools:

| Tool | Description |
|------|-------------|
| `botwave_agent_run` | Run a coding task with aider + LM Studio |
| `botwave_agent_status` | Check status of agent jobs |
| `botwave_skill_list` | List available skills |
| `botwave_skill_run` | Run a specific skill |
| `botwave_dashboard_status` | Check if dashboard is running |
| `botwave_lm_studio_status` | Check LM Studio status |
| `botwave_create_parallel_jobs` | **SCRYPT KEEPER STYLE**: Break large task into parallel agent jobs |

## How to Use

### 1. Restart Claude Code
```bash
# Exit and restart Claude Code
/exit
# Then start again
claude
```

### 2. Use Botwave Agents

**Example: Create parallel agent jobs (SCRYPT KEEPER style)**
```
Use botwave_create_parallel_jobs to break down "Build customer portal with Stripe integration" into 4 parallel tasks
```

**Example: Run an agent job**
```
Use botwave_agent_run to create a job that adds error handling to scrypt_keeper_api.py
```

**Example: Check status**
```
Use botwave_agent_status to see all running jobs
```

**Example: Run a skill**
```
Use botwave_skill_run with skill="self-audit" and args=["--list-issues"]
```

## SCRYPT KEEPER Style Parallel Execution

The `botwave_create_parallel_jobs` tool implements your vision:

```
Large Task → Orchestrator → 4 Parallel Agent Jobs → Pipeline → Complete
```

Example breakdown for "Build customer portal":
1. **Setup Agent**: Config, dependencies, project structure
2. **Core Agent**: Business logic, database models
3. **Interface Agent**: Web UI, API endpoints
4. **Test Agent**: Tests, docs, error handling

All run in parallel via aider + LM Studio.

## For Your Customers (Non-Technical Users)

This MCP setup is for **YOU** (development). Your customers use:

- **Botwave CLI**: `botwave status`, `botwave run-agent`
- **Dashboard**: http://localhost:5000
- **Telegram Bot**: Automated customer notifications

They don't need to know about MCP, aider, or LM Studio. It just works.

## Troubleshooting

### MCP Server Not Loading
```bash
# Test manually
python3 /home/gringo/BotwaveEmpire/mcp/botwave-mcp-server.py
```

### Check LM Studio Connection
```bash
curl http://localhost:1234/v1/models
```

### Restart MCP
In Claude Code settings, remove and re-add the botwave server, then restart.
