#!/usr/bin/env python3
"""
Botwave Command Dashboard
Interactive CLI dashboard to command your agents
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.secrets import secrets
from agents.janitor_squad import JanitorSquad
from agents.system_organizer_agent import SystemOrganizerAgent


class BotwaveDashboard:
    """
    Interactive dashboard for commanding Botwave agents.
    """

    def __init__(self):
        self.agents = {
            "openclaw": {
                "name": "OpenClaw",
                "description": "Master orchestrator - coordinates all agents",
                "status": "ONLINE",
                "capabilities": ["orchestrate", "deploy", "monitor"]
            },
            "janitor_squad": {
                "name": "Janitor Squad",
                "description": "System overhaul team - 5 specialized agents",
                "status": "READY",
                "capabilities": ["system_cleanup", "organization", "security_scan"]
            },
            "plumbing": {
                "name": "Plumbing Agent",
                "description": "Business automation for plumbing services",
                "status": "READY",
                "capabilities": ["quotes", "scheduling", "customer_mgmt"]
            },
            "intelligence": {
                "name": "Intelligence Agent",
                "description": "LLM-powered analysis and reasoning",
                "status": "READY",
                "capabilities": ["analysis", "review", "generation"]
            }
        }
        self.command_history = []

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_banner(self):
        self.clear_screen()
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗  ██████╗ ████████╗██╗    ██╗ █████╗ ██╗   ██╗███████╗            ║
║   ██╔══██╗██╔═══██╗╚══██╔══╝██║    ██║██╔══██╗██║   ██║██╔════╝            ║
║   ██████╔╝██║   ██║   ██║   ██║ █╗ ██║███████║██║   ██║█████╗              ║
║   ██╔══██╗██║   ██║   ██║   ██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝              ║
║   ██████╔╝╚██████╔╝   ██║   ╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗            ║
║   ╚═════╝  ╚═════╝    ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝            ║
║                                                                           ║
║                    COMMAND DASHBOARD v1.0                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def show_status(self):
        print("\n📊 AGENT STATUS")
        print("-" * 80)
        for agent_id, agent_info in self.agents.items():
            status_icon = "🟢" if agent_info["status"] == "ONLINE" or agent_info["status"] == "READY" else "🔴"
            print(f"{status_icon} {agent_info['name']:<20} [{agent_info['status']:<10}] {agent_info['description']}")
        print("-" * 80)

    def show_commands(self):
        print("\n⌨️  AVAILABLE COMMANDS")
        print("-" * 80)
        print("  deploy janitor_squad <host> [business_type] - Deploy cleanup team")
        print("  organize system <host> [username]           - System organization")
        print("  scan security <host>                      - Security audit")
        print("  status                                    - Show agent status")
        print("  mcp status                                - MCP server status")
        print("  chat <agent> <message>                     - Message an agent")
        print("  help                                      - Show this help")
        print("  exit                                      - Exit dashboard")
        print("-" * 80)

    def deploy_janitor_squad(self, host: str, business_type: str = "general"):
        """Deploy the Janitor Squad to a remote system."""
        print(f"\n🚀 Deploying Janitor Squad to {host}...")
        print("Business type:", business_type)
        print()

        try:
            squad = JanitorSquad(host=host, user="admin")
            result = squad.deploy(business_type=business_type)

            if result["status"] == "success":
                print("\n✅ DEPLOYMENT SUCCESSFUL")
                print(f"\n📄 Report: {result['report']['agents'].get('polish', {}).get('data', {}).get('output_location', 'Desktop')}")
                print(f"💰 Invoice: ${result['report'].get('invoice', {}).get('total', 187.50)}")
            else:
                print(f"\n❌ Deployment failed: {result.get('message')}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    def organize_system(self, host: str, username: str = "admin"):
        """Run system organizer on remote system."""
        print(f"\n🧹 Running System Organizer on {host}...")

        try:
            agent = SystemOrganizerAgent()
            result = agent.run({
                "host": host,
                "user": username,
                "action": "full_cleanup"
            })

            if result["status"] == "success":
                print("\n✅ Organization complete!")
                data = result.get("data", {})
                if "report" in data:
                    print(f"\n📄 Report generated and saved to target Desktop")
            else:
                print(f"\n❌ Error: {result.get('message')}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    def chat_with_agent(self, agent_name: str, message: str):
        """Chat with a specific agent."""
        if agent_name not in self.agents:
            print(f"❌ Agent '{agent_name}' not found. Available: {', '.join(self.agents.keys())}")
            return

        agent_info = self.agents[agent_name]
        print(f"\n🤖 Chatting with {agent_info['name']}...")
        print(f"\nYou: {message}")

        # Simple responses based on agent capabilities
        responses = {
            "openclaw": "OpenClaw here. I'm coordinating all agents. What system needs attention?",
            "janitor_squad": "Janitor Squad ready. Send us to clean up any messy system. We charge $187.50 per overhaul.",
            "plumbing": "Plumbing Agent online. I can handle quotes, scheduling, and customer management for your dad's business.",
            "intelligence": "Intelligence Agent active. I can analyze data, review code, or process documents with LLM power."
        }

        print(f"{agent_info['name']}: {responses.get(agent_name, 'Ready to assist.')}")

    def process_command(self, command: str):
        """Process user command."""
        parts = command.strip().split()
        if not parts:
            return True

        cmd = parts[0].lower()
        self.command_history.append(command)

        if cmd == "exit" or cmd == "quit":
            print("\n👋 Goodbye!")
            return False

        elif cmd == "help":
            self.show_commands()

        elif cmd == "status":
            self.show_status()

        elif cmd == "clear":
            self.show_banner()
            self.show_status()
            self.show_commands()

        elif cmd == "deploy" and len(parts) >= 2:
            if parts[1] == "janitor_squad" and len(parts) >= 3:
                host = parts[2]
                business_type = parts[3] if len(parts) > 3 else "general"
                self.deploy_janitor_squad(host, business_type)
            else:
                print("❌ Usage: deploy janitor_squad <host> [business_type]")

        elif cmd == "organize" and len(parts) >= 2:
            if parts[1] == "system" and len(parts) >= 3:
                host = parts[2]
                username = parts[3] if len(parts) > 3 else "admin"
                self.organize_system(host, username)
            else:
                print("❌ Usage: organize system <host> [username]")

        elif cmd == "chat" and len(parts) >= 3:
            agent_name = parts[1]
            message = " ".join(parts[2:])
            self.chat_with_agent(agent_name, message)

        elif cmd == "mcp" and len(parts) > 1:
            if parts[1] == "status":
                self.check_mcp_status()
            else:
                print("❌ Unknown MCP command")

        else:
            print(f"❌ Unknown command: {cmd}")
            print("Type 'help' for available commands")

        return True

    def check_mcp_status(self):
        """Check MCP server status."""
        print("\n🔌 MCP Server Status")
        print("-" * 80)

        mcp_dir = os.path.join(os.path.dirname(__file__), '..', '.mcp')
        context_file = os.path.join(mcp_dir, 'context.json')

        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    context = json.load(f)
                print(f"✅ MCP Context: {context.get('status', 'unknown')}")
                print(f"   Repository: {context.get('repository', 'N/A')}")
                print(f"   Agents: {', '.join(context.get('agents', []))}")
                print(f"   Last Update: {context.get('timestamp', 'N/A')}")
            except Exception as e:
                print(f"⚠️  MCP context error: {e}")
        else:
            print("⚠️  MCP not initialized")
            print("   Run: python -m src.core.mcp_server")

        print("-" * 80)

    def run(self):
        """Main dashboard loop."""
        self.show_banner()
        self.show_status()
        self.show_commands()

        running = True
        while running:
            try:
                print()
                command = input("Botwave> ").strip()
                running = self.process_command(command)
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Entry point."""
    dashboard = BotwaveDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
