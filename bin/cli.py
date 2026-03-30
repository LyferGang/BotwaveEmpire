#!/usr/bin/env python3
"""
BOTWAVE CLI — Your command center for AI automation

Usage:
    botwave init          # Scaffold new project
    botwave setup         # Run setup wizard
    botwave status        # Check system status
    botwave upgrade       # Update to latest version
    botwave run-agent     # Run agent job
    botwave aid <files>   # Launch aider with LM Studio
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

VERSION = "0.1.0"
EMPIRE_DIR = Path(__file__).parent.parent

def print_header():
    print(f"{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  BOTWAVE EMPIRE CLI v{VERSION}{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}→ {msg}{Colors.END}")

def cmd_init():
    """Initialize new Botwave project."""
    print_header()
    print(f"{Colors.BOLD}Initializing Botwave Project...{Colors.END}\n")

    # Check prerequisites
    print_info("Checking prerequisites...")

    # Check Python
    if sys.version_info < (3, 10):
        print_error("Python 3.10+ required")
        return 1
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check LM Studio
    try:
        import requests
        resp = requests.get("http://localhost:1234/v1/models", timeout=2)
        if resp.status_code == 200:
            print_success("LM Studio running")
        else:
            print_error("LM Studio not responding on port 1234")
            return 1
    except:
        print_error("LM Studio not running. Start LM Studio first.")
        return 1

    # Check aider
    try:
        result = subprocess.run(['which', 'aider'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("aider installed")
        else:
            print_error("aider not found. Install with: pip install aider-chat")
            return 1
    except:
        print_error("Could not check aider")
        return 1

    # Create project structure
    print_info("\nCreating project structure...")
    dirs = ['config', 'skills/active', 'data', 'logs', 'agent-jobs', '.github/workflows']
    for d in dirs:
        (EMPIRE_DIR / d).mkdir(parents=True, exist_ok=True)
        print_success(f"Created {d}/")

    # Create config files if they don't exist
    config_files = {
        'config/CRONS.json': '[]',
        'config/TRIGGERS.json': '[]',
        'config/AGENT.md': '# Botwave Agent Configuration\n\n# Add your agent instructions here\n',
    }

    for path, content in config_files.items():
        full_path = EMPIRE_DIR / path
        if not full_path.exists():
            with open(full_path, 'w') as f:
                f.write(content)
            print_success(f"Created {path}")

    print_info("\nBotwave initialized! Run 'botwave setup' to configure.")
    return 0

def cmd_setup():
    """Run setup wizard."""
    print_header()
    print(f"{Colors.BOLD}Botwave Setup Wizard{Colors.END}\n")

    print_info("This wizard will configure your Botwave Empire.\n")

    # Load .env
    env_file = EMPIRE_DIR / ".env"
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key] = val

    # Check LM Studio connection
    print_info("Testing LM Studio connection...")
    try:
        import requests
        resp = requests.get("http://localhost:1234/v1/models", timeout=2)
        models = resp.json().get('data', [])
        if models:
            print_success(f"Connected to LM Studio ({len(models)} models available)")
            print_info(f"Models: {', '.join([m['id'] for m in models[:3]])}")
        else:
            print_error("No models loaded in LM Studio")
    except Exception as e:
        print_error(f"Cannot connect to LM Studio: {e}")
        print_info("Make sure LM Studio server is running on port 1234")
        return 1

    # Check .aid alias
    print_info("\nChecking 'aid' alias...")
    result = subprocess.run(['bash', '-c', 'type aid 2>/dev/null'], capture_output=True)
    if result.returncode == 0:
        print_success("'aid' alias configured")
    else:
        print_info("To configure 'aid' alias, add this to your ~/.bashrc or ~/.zshrc:")
        print("""
aid() {
    local PORT=1234
    local MODEL_ID=$(curl -s http://localhost:$PORT/v1/models | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])")
    aider --model "openai/$MODEL_ID" --openai-api-base "http://localhost:$PORT/v1" --openai-api-key "lm-studio" "$@"
}
        """)

    print_info("\n" + "="*60)
    print_success("Setup complete! You can now use Botwave.")
    print_info("\nQuick start:")
    print("  1. Run 'botwave status' to check system")
    print("  2. Run 'aid <file.py>' to edit code with AI")
    print("  3. Run 'python master_control.py' for the control panel")

    return 0

def cmd_status():
    """Show system status."""
    print_header()
    print(f"{Colors.BOLD}System Status{Colors.END}\n")

    # Check services
    services = {
        "LM Studio": "ss -tuln | grep -q ':1234 '",
        "Dashboard": "pgrep -f 'web_app.py'",
        "Plumbing Bot": "pgrep -f 'plumbing_telegram_bot.py'",
    }

    for name, cmd in services.items():
        result = subprocess.run(cmd, shell=True, capture_output=True)
        status = f"{Colors.GREEN}RUNNING{Colors.END}" if result.returncode == 0 else f"{Colors.RED}STOPPED{Colors.END}"
        print(f"  {name:.<35} {status}")

    # Check disk usage
    print(f"\n{Colors.BOLD}Disk Usage{Colors.END}")
    result = subprocess.run(['du', '-sh', str(EMPIRE_DIR)], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  BotwaveEmpire: {result.stdout.strip().split()[0]}")

    # Check GPU
    print(f"\n{Colors.BOLD}GPU Status{Colors.END}")
    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader'],
                          capture_output=True, text=True)
    if result.returncode == 0:
        used, total = result.stdout.strip().split(', ')
        print(f"  VRAM: {used} / {total}")

    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    return 0

def cmd_upgrade():
    """Upgrade Botwave to latest version."""
    print_header()
    print(f"{Colors.BOLD}Checking for upgrades...{Colors.END}\n")

    # For now, just show current version
    print_info(f"Current version: {VERSION}")
    print_info("Auto-upgrade not yet implemented.")
    print_info("Check GitHub for latest version manually.")

    return 0

def cmd_run_agent(job_spec=None):
    """Run an agent job."""
    print_header()
    print(f"{Colors.BOLD}Running Agent Job{Colors.END}\n")

    if not job_spec:
        print_error("No job specified. Usage: botwave run-agent <job.json>")
        return 1

    job_path = Path(job_spec)
    if not job_path.exists():
        print_error(f"Job file not found: {job_spec}")
        return 1

    with open(job_path) as f:
        job = json.load(f)

    print_info(f"Job: {job.get('name', 'Unnamed')}")
    print_info(f"Task: {job.get('task', 'No task specified')}")

    # Launch aider with the job instructions
    print_info("\nLaunching aider with LM Studio...")

    # Create a temporary instruction file
    instruction_file = EMPIRE_DIR / "agent-jobs" / f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(instruction_file, 'w') as f:
        f.write(f"# Agent Job: {job.get('name', 'Unnamed')}\n\n")
        f.write(f"## Task\n{job.get('task', '')}\n\n")
        f.write(f"## Files to Modify\n{', '.join(job.get('files', []))}\n\n")
        f.write(f"## Instructions\n{job.get('instructions', '')}\n")

    print_success(f"Created job instructions: {instruction_file}")

    # Launch aider
    cmd = ['aid', str(instruction_file)]
    print_info(f"Running: {' '.join(cmd)}")

    subprocess.run(cmd)

    print_success("Agent job completed!")
    return 0

def cmd_help():
    """Show help."""
    print_header()
    print(f"""{Colors.BOLD}Usage:{Colors.END} botwave <command> [options]

{Colors.BOLD}Commands:{Colors.END}
  init          Initialize new Botwave project
  setup         Run setup wizard
  status        Show system status
  upgrade       Check for upgrades
  run-agent     Run an agent job
  help          Show this help

{Colors.BOLD}Examples:{Colors.END}
  botwave init
  botwave setup
  botwave status
  botwave run-agent job.json
  botwave aid file.py    # Launch aider with LM Studio
""")
    return 0

def main():
    if len(sys.argv) < 2:
        return cmd_help()

    cmd = sys.argv[1]

    commands = {
        'init': cmd_init,
        'setup': cmd_setup,
        'status': cmd_status,
        'upgrade': cmd_upgrade,
        'run-agent': cmd_run_agent,
        'help': cmd_help,
    }

    if cmd in commands:
        return commands[cmd]()
    else:
        print_error(f"Unknown command: {cmd}")
        return cmd_help()

if __name__ == "__main__":
    sys.exit(main())
