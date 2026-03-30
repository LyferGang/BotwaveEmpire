---
name: self-audit
description: Self-auditing skill using aider to review and improve code
version: 1.0.0
author: Botwave Empire
---

# Self-Audit Skill

Uses aider + LM Studio to autonomously audit and improve the Botwave codebase.

## Usage

```bash
# Run self-audit on specific files
python skills/active/self-audit/audit.py --files scrypt_keeper_*.py

# Run full system audit
python skills/active/self-audit/audit.py --all

# Run with aider auto-fix
python skills/active/self-audit/audit.py --fix
```

## How It Works

1. Scans codebase for issues (TODOs, incomplete code, errors)
2. Launches aider with audit instructions
3. Reviews suggested changes
4. Commits improvements

## Aider Commands

- `/run <command>` - Run shell commands
- `/add <file>` - Add files to chat
- `/drop <file>` - Remove files
- `/commit` - Commit changes
- `/undo` - Undo last change
