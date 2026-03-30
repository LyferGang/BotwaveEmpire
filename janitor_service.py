#!/usr/bin/env python3
"""
JANITOR SQUAD SERVICE LAUNCHER
Premium Business System Overhaul
$187.50 per service (2.5 hours @ $75/hour)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.janitor_squad import JanitorSquad


def show_banner():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██╗ █████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗                      ║
║   ██║██╔══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗                     ║
║   ██║███████║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝                     ║
║   ██║██╔══██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗                     ║
║   ██║██║  ██║██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║                     ║
║   ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝                     ║
║                                                                           ║
║          Premium Business System Overhaul Service                        ║
║                    $187.50 / service                                      ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    show_banner()

    print("Welcome to the Janitor Squad!\n")
    print("This premium service will:")
    print("  ✓ Analyze your entire file system")
    print("  ✓ Scan for malware and security threats")
    print("  ✓ Optimize network performance")
    print("  ✓ Remove bloat and improve speed")
    print("  ✓ Generate a professional report")
    print()

    # Get connection details
    print("Enter the target system details:")
    print("(Make sure Tailscale is connected on both machines)\n")

    tailscale_ip = input("Tailscale IP Address: ").strip()
    if not tailscale_ip:
        print("❌ Error: IP address required")
        sys.exit(1)

    username = input("Username [default: dad]: ").strip() or "dad"

    print("\nSelect business type for customized service:")
    print("  1. Plumbing / Trade Service")
    print("  2. Retail / Store")
    print("  3. Office / Professional")
    print("  4. Medical / Healthcare")
    print("  5. General / Other")
    print()

    biz_choice = input("Choice [1-5, default: 5]: ").strip() or "5"

    business_types = {
        "1": "plumbing",
        "2": "retail",
        "3": "office",
        "4": "medical",
        "5": "general"
    }

    business_type = business_types.get(biz_choice, "general")

    print("\n" + "="*80)
    print("READY TO DEPLOY JANITOR SQUAD")
    print("="*80)
    print(f"Target: {tailscale_ip}")
    print(f"User: {username}")
    print(f"Business Type: {business_type}")
    print(f"Estimated Time: 2.5 hours")
    print(f"Service Cost: $187.50")
    print("="*80)

    confirm = input("\nDeploy Janitor Squad? [y/N]: ").strip().lower()

    if confirm != 'y':
        print("\nDeployment cancelled.")
        sys.exit(0)

    # Deploy the squad
    print("\n🚀 DEPLOYING JANITOR SQUAD...\n")

    try:
        squad = JanitorSquad(host=tailscale_ip, user=username)
        result = squad.deploy(business_type=business_type)

        print("\n" + "="*80)

        if result['status'] == 'success':
            print("✅ MISSION ACCOMPLISHED")
            print("="*80)
            print()

            report = result.get('report', {})
            invoice = report.get('invoice', {})

            print("📊 SERVICE SUMMARY:")
            print(f"   Duration: {invoice.get('hours', 2.5)} hours")
            print(f"   Rate: ${invoice.get('rate', 75)}/hour")
            print(f"   Total: ${invoice.get('total', 187.50)}")
            print()

            print("📁 DELIVERABLES:")
            agents = report.get('agents', {})
            for agent_name, agent_result in agents.items():
                status = "✓" if agent_result.get('status') == 'success' else "✗"
                print(f"   {status} {agent_name.upper()} Agent")
            print()

            print("📄 REPORTS GENERATED:")
            polish_data = agents.get('polish', {}).get('data', {})
            report_location = polish_data.get('output_location', 'Desktop')
            print(f"   Professional Report: {report_location}")
            print()

            print("💼 BUSINESS VALUE:")
            print("   • System is now organized and optimized")
            print("   • Security threats identified and quarantined")
            print("   • Performance improved")
            print("   • Professional documentation for records")
            print()

            print("="*80)
            print("Next Steps:")
            print("  1. Review the report on the target system's Desktop")
            print("  2. Discuss findings with the business owner")
            print("  3. Schedule follow-up maintenance (recommended monthly)")
            print("  4. Invoice for services rendered")
            print("="*80)

        else:
            print("❌ DEPLOYMENT FAILED")
            print("="*80)
            print(f"Error: {result.get('message', 'Unknown error')}")
            print()
            print("Troubleshooting:")
            print("  • Is Tailscale connected? (tailscale status)")
            print("  • Is the IP address correct?")
            print("  • Is SSH enabled on the target system?")
            print("  • Is the username correct?")
            print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
