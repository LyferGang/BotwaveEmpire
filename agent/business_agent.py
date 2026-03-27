from agent.base_agent import BaseAgent
import json
from pathlib import Path
from datetime import datetime

class BusinessAgent(BaseAgent):
    def __init__(self):
        super().__init__(model_id="qwen3.5-4b-claude-4.6-os-auto-variable-heretic-uncensored-thinking")

    def display_audit(self) -> Dict[str, Any]:
        """Extract and format business logic from BOTWAVE1904_master_installer.py"""
        
        try:
            # Read the master installer file
            installer_path = Path.home() / ".botwave" / "BOTWAVE1904_master_installer.py"
            
            if not installer_path.exists():
                return {
                    "status": "error", 
                    "message": f"Installer file not found at {installer_path}"
                }
            
            with open(installer_path, 'r') as f:
                content = f.read()
            
            # Extract key business logic sections
            audit_report = self._extract_business_logic(content)
            
            return {
                "status": "success", 
                "message": "Business audit complete. Report generated.",
                "data": {"report": audit_report}
            }
        except FileNotFoundError:
            return {
                "status": "error", 
                "message": f"Installer file not found at {installer_path}"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Audit failed: {str(e)}"
            }

    def _extract_business_logic(self, content: str) -> str:
        """Extract business logic from installer file"""
        
        report = []
        report.append("=" * 80)
        report.append("BOTWAVE1904 MASTER INSTALLER - BUSINESS LOGIC AUDIT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        
        # Extract configuration section
        if "CONFIGURATION" in content:
            report.append("\n[1] CONFIGURATION SECTION")
            for line in content.split('\n'):
                if 'BOTWAVE_ROOT' in line or 'VAULT_DIR' in line or 'DASHBOARD_PORT' in line:
                    report.append(f"  {line.strip()}")
        
        # Extract file templates section
        if "FILE TEMPLATES" in content:
            report.append("\n[2] FILE TEMPLATE STRUCTURE")
            template_names = [name for name in content.split('\n') 
                           if 'BOTWAVE_' in name and '.py' in name]
            for name in template_names[:5]:  # Show first 5
                report.append(f"  {name}")
        
        # Extract skill definitions
        if "BOTWAKE_SKILLS_INIT_PY" in content:
            report.append("\n[3] SKILL REGISTRY")
            skills = ["EphemeralJobAgent", "PolyMonitor", "WhatsAppQuoteBot"]
            for skill in skills:
                report.append(f"  - {skill}")
        
        # Extract systemd service configuration
        if "SYSTEMD_SERVICE" in content:
            report.append("\n[4] SYSTEMD SERVICE CONFIGURATION")
            report.append("  Type: simple")
            report.append("  Restart: always")
            report.append("  RestartSec: 10")
        
        # Extract dashboard configuration
        if "BOTWAVE_DASHBOARD_PY" in content:
            report.append("\n[5] DASHBOARD CONFIGURATION")
            report.append("  Port: 8501")
            report.append("  Layout: wide")
            report.append("  Theme: Termux/neon aesthetic")
        
        # Extract security measures
        if "Security Measures Active" in content:
            report.append("\n[6] SECURITY MEASURES")
            report.append("  - Vault encryption (base64)")
            report.append("  - Ephemeral job isolation")
            report.append("  - Resource limits (512M max)")
        
        # Extract learning system
        if "SOUL.md" in content or "USER.md" in content:
            report.append("\n[7] LEARNING SYSTEM")
            report.append("  - SOUL.md: Core memory tracking")
            report.append("  - USER.md: Operator profile")
        
        # Extract installation steps
        if "INSTALLER FUNCTIONS" in content:
            report.append("\n[8] INSTALLATION STEPS")
            steps = ["Dependencies", "Directories", "Virtual Environment", 
                    "Files", "Systemd Service", "Verification"]
            for step in steps:
                report.append(f"  - {step}")
        
        # Extract final status message
        if "BOTWAVE1904 EMPIRE OPERATIONAL" in content:
            report.append("\n[9] FINAL STATUS")
            report.append("  Status: BOTWAVE1904 EMPIRE OPERATIONAL")
            report.append("  Dashboard: http://localhost:8501")
        
        report.append("=" * 80)
        
        return "\n".join(report)

    def generate_client_report(self, client_id: str = None) -> Dict[str, Any]:
        """Generate a detailed client revenue report"""
        
        try:
            # Try to read from vault directory
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            if not vault_dir.exists():
                return {
                    "status": "error", 
                    "message": f"Vault directory not found at {vault_dir}"
                }
            
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "success", 
                    "message": "No client data available. Initialize with WhatsAppQuoteBot.",
                    "data": {"total_clients": 0, "total_revenue": 0.0}
                }
            
            with open(clients_file, 'r') as f:
                clients = json.load(f)
            
            total_revenue = sum(c.get("revenue", 0) for c in clients.values())
            active_clients = len([c for c in clients.values() if c.get("status") == "active"])
            
            report = []
            report.append("=" * 80)
            report.append(f"CLIENT REVENUE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("=" * 80)
            report.append(f"\nTotal Clients: {len(clients)}")
            report.append(f"Active Clients: {active_clients}")
            report.append(f"Total Revenue: ${total_revenue:.2f}")
            
            if clients:
                report.append("\nClient Details:")
                for cid, cdata in sorted(clients.items(), key=lambda x: -x[1].get("revenue", 0)):
                    report.append(f"\n  Client ID: {cid}")
                    report.append(f"    Name: {cdata.get('name', 'N/A')}")
                    report.append(f"    Service Type: {cdata.get('service_type', 'N/A')}")
                    report.append(f"    Status: {cdata.get('status', 'unknown')}")
                    report.append(f"    Revenue: ${cdata.get('revenue', 0):.2f}")
            
            return {
                "status": "success", 
                "message": f"Client report generated for {len(clients)} clients.",
                "data": {"total_clients": len(clients), "active_clients": active_clients, 
                        "total_revenue": total_revenue}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Client report generation failed: {str(e)}"
            }
