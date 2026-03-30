#!/usr/bin/env python3
"""
Dad's Plumbing Business Laptop Cleanup
One-click script to organize and secure the business computer
"""

import os
import sys
import subprocess
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.system_organizer_agent import SystemOrganizerAgent


def main():
    print("=" * 80)
    print("     BOTWAVE SYSTEM ORGANIZER - Plumbing Business Edition")
    print("=" * 80)
    print()
    print("This will remotely clean and organize your dad's business laptop.")
    print("No files will be permanently deleted - everything goes to review folders.")
    print()

    # Get Tailscale IP
    tailscale_ip = input("Enter the laptop's Tailscale IP (e.g., 100.x.x.x): ").strip()

    if not tailscale_ip:
        print("Error: No IP provided. Find it with: tailscale status")
        sys.exit(1)

    # Get username
    username = input("Enter the laptop username [default: dad]: ").strip() or "dad"

    print()
    print("Select action:")
    print("  1. Full Cleanup (scan + quarantine + organize)")
    print("  2. Scan Only (see what's there first)")
    print("  3. Quarantine Suspicious Files only")
    print("  4. Organize Files only")
    print()

    choice = input("Choice [1-4]: ").strip() or "1"

    actions = {
        "1": "full_cleanup",
        "2": "scan",
        "3": "quarantine",
        "4": "organize"
    }

    action = actions.get(choice, "full_cleanup")

    print()
    print(f"Connecting to {tailscale_ip} via Tailscale...")
    print(f"Running: {action}")
    print()
    print("-" * 80)

    # Run the agent
    agent = SystemOrganizerAgent()
    result = agent.run({
        "host": tailscale_ip,
        "user": username,
        "action": action
    })

    print("-" * 80)
    print()

    if result['status'] == 'success':
        print("✅ SUCCESS!")
        print()

        data = result.get('data', {})

        if action == "full_cleanup":
            print("📋 WHAT WAS DONE:")
            print()
            print("1. System scanned for inventory")
            print("2. Suspicious files moved to Desktop/For_Review/")
            print("3. Files organized into Desktop/Organized_[date]/")
            print("4. Report generated on Desktop")
            print()
            print("⚠️  IMPORTANT:")
            print("   - NOTHING WAS DELETED")
            print("   - Everything is in review folders")
            print("   - Show your dad the report on his Desktop")
            print("   - Review quarantined files together before deleting")
            print()

        elif action == "scan":
            print("📊 SCAN RESULTS:")
            print(data.get('scan', {}).get('raw_output', 'No output'))

        elif action == "quarantine":
            print("🔒 QUARANTINE COMPLETE:")
            print(f"   Location: {data.get('quarantine_location', 'Desktop/For_Review/')}")
            print()
            print("   Quarantined items moved there for review.")

        elif action == "organize":
            print("📁 ORGANIZATION COMPLETE:")
            print(f"   Location: {data.get('organized_location', 'N/A')}")
            print()
            print("   Files sorted by type. Originals still in place.")

        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("1. SSH into the laptop to see the results")
        print(f"   ssh {username}@{tailscale_ip}")
        print()
        print("2. Check the Desktop for:")
        print("   - For_Review/ folder (suspicious files)")
        print("   - Organized_[date]/ folder (sorted files)")
        print("   - CLEANUP_REPORT_[date].txt (full report for dad)")
        print()
        print("3. Show your dad the report and review quarantined files together")
        print()
        print("4. After approval, delete organized copies (originals are safe)")
        print()

    else:
        print("❌ ERROR:")
        print(f"   {result.get('message', 'Unknown error')}")
        print()
        print("Troubleshooting:")
        print("   - Is Tailscale connected? Run: tailscale status")
        print("   - Is the IP correct? Check Tailscale admin panel")
        print("   - Is SSH enabled on the laptop?")
        print("   - Is the username correct?")

    print("=" * 80)


if __name__ == "__main__":
    main()
