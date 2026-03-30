#!/usr/bin/env python3
"""
Get Secret Skill - Retrieve secrets securely
"""

import os
import sys
from pathlib import Path


def get_secret(name: str) -> str:
    """Get a secret from environment or vault."""
    # First check environment
    value = os.getenv(name)
    if value:
        return value

    # Check vault file
    vault_path = Path.home() / "BotwaveEmpire" / "credentials" / f"{name}.txt"
    if vault_path.exists():
        return vault_path.read_text().strip()

    return None


def run(args: dict) -> dict:
    """Execute the skill."""
    secret_name = args.get("name")

    if not secret_name:
        return {"error": "Secret name required"}

    # Mask the secret name in logs
    masked_name = secret_name[:3] + "***" if len(secret_name) > 3 else "***"

    value = get_secret(secret_name)

    if not value:
        return {"error": f"Secret '{masked_name}' not found"}

    # Return masked value for security
    masked_value = value[:4] + "***" if len(value) > 4 else "***"

    return {
        "status": "success",
        "secret": masked_value,
        "message": f"Retrieved secret '{masked_name}'"
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = run({"name": sys.argv[1]})
        print(result)
