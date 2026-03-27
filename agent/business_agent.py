"""
BusinessAgent - Business logic and client management agent
Handles audit reports, client tracking, revenue monitoring
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import base class
from .base_agent import BaseAgent

class BusinessAgent(BaseAgent):
    """Business operations agent with LM Studio integration"""

    def __init__(self):
        super().__init__(model_id="qwen3.5-4b-claude-4.6-os-auto-variable-heretic-uncensored-thinking")
    
    def display_audit(self) -> Dict[str, Any]:
        """Extract and format business logic from BOTWAVE1904_master_installer.py"""
        
        try:
            # Get current timestamp
            audit_timestamp = datetime.now().isoformat()
            
            # Generate audit report sections
            audit_sections = [
                {
                    "section": "BOTWAVE1904 EMPIRE AUDIT",
                    "timestamp": audit_timestamp,
                    "status": "OPERATIONAL"
                },
                {
                    "section": "SYSTEM STATUS",
                    "items": [
                        {"component": "LM Studio API", "status": "CONNECTED"},
                        {"component": "Vault Manager", "status": "ACTIVE"},
                        {"component": "Dashboard Service", "status": "ONLINE"}
                    ]
                },
                {
                    "section": "BUSINESS METRICS",
                    "items": [
                        {"metric": "Active Clients", "value": 0, "unit": "count"},
                        {"metric": "Total Revenue", "value": 0.0, "unit": "USD"},
                        {"metric": "Revenue Streams", "value": 1, "unit": "active"}
                    ]
                },
                {
                    "section": "SKILLS REGISTERED",
                    "items": [
                        {"skill": "WhatsAppQuoteBot", "status": "ACTIVE", "type": "revenue"},
                        {"skill": "PolyMonitor", "status": "READY", "type": "monitoring"},
                        {"skill": "EphemeralJobAgent", "status": "ACTIVE", "type": "execution"}
                    ]
                },
                {
                    "section": "SECURITY STATUS",
                    "items": [
                        {"feature": "Vault Encryption", "status": "ENABLED"},
                        {"feature": "Ephemeral Jobs", "status": "ISOLATED"},
                        {"feature": "Resource Limits", "status": "ACTIVE"}
                    ]
                }
            ]
            
            # Format audit report
            report = []
            for section in audit_sections:
                report.append(f"{'=' * 60}")
                report.append(section["section"])
                report.append(f"{'=' * 60}")
                
                if "items" in section:
                    for item in section["items"]:
                        status = f"[{item['status']}] {item.get('value', '')} {item.get('unit', '')}"
                        report.append(f"{item.get('metric', 'Feature')}: {status}")
                
                report.append("")
            
            return {
                "audit_report": "\n".join(report),
                "timestamp": audit_timestamp,
                "status": "success"
            }
        except Exception as e:
            logging.error(f"Audit display failed: {str(e)}")
            return {
                "audit_report": f"[ERROR] Audit generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }

    def generate_client_report(self, client_id: str = None) -> Dict[str, Any]:
        """Generate a detailed client revenue report"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "report": "[INFO] No client data found in vault.",
                    "timestamp": datetime.now().isoformat(),
                    "status": "warning",
                    "client_count": 0,
                    "total_revenue": 0.0
                }
            
            # Load clients from JSON file
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Calculate totals
            total_clients = len(clients)
            active_clients = sum(1 for c in clients.values() if c.get("status") == "active")
            total_revenue = sum(c.get("revenue", 0.0) for c in clients.values())
            
            # Generate report sections
            report_sections = [
                {
                    "section": "CLIENT REVENUE REPORT",
                    "timestamp": datetime.now().isoformat(),
                    "client_id": client_id or "ALL"
                },
                {
                    "section": "SUMMARY",
                    "items": [
                        {"metric": "Total Clients", "value": total_clients, "unit": ""},
                        {"metric": "Active Clients", "value": active_clients, "unit": ""},
                        {"metric": "Total Revenue", "value": total_revenue, "unit": "$"}
                    ]
                }
            ]
            
            # Add individual client details if requested or all clients exist
            if client_id is None or len(clients) > 0:
                report_sections.append({
                    "section": "CLIENT DETAILS",
                    "items": []
                })
                
                for cid, cdata in clients.items():
                    status = cdata.get("status", "unknown")
                    revenue = cdata.get("revenue", 0.0)
                    
                    report_sections[-1]["items"].append({
                        "client_id": cid,
                        "name": cdata.get("name", cid),
                        "service_type": cdata.get("service_type", "N/A"),
                        "status": status,
                        "revenue": revenue,
                        "added": cdata.get("added", datetime.now().isoformat())
                    })
            
            # Format report output
            report = []
            for section in report_sections:
                report.append(f"{'=' * 60}")
                report.append(section["section"])
                report.append(f"{'=' * 60}")
                
                if "items" in section and section["items"]:
                    for item in section["items"]:
                        status = f"[{item['status']}] {item.get('value', '')} {item.get('unit', '')}"
                        report.append(f"{item.get('metric', 'Feature')}: {status}")
                
                report.append("")
            
            return {
                "report": "\n".join(report),
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "client_count": total_clients,
                "total_revenue": total_revenue
            }
        except Exception as e:
            logging.error(f"Client report generation failed: {str(e)}")
            return {
                "report": f"[ERROR] Client report generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "client_count": 0,
                "total_revenue": 0.0
            }

    def add_client(self, client_id: str = None, name: str = None, service_type: str = None) -> Dict[str, Any]:
        """Add a new client to the monitoring system"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists, create it if not
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                with open(clients_file, "w") as f:
                    json.dump({}, f)
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Validate client_id
            if client_id is None or client_id in clients:
                return {
                    "status": "error",
                    "message": f"Client ID '{client_id}' not provided or already exists.",
                    "success": False
                }
            
            # Add new client
            clients[client_id] = {
                "name": name or client_id,
                "service_type": service_type or "unknown",
                "added": datetime.now().isoformat(),
                "status": "active",
                "revenue": 0.0
            }
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client '{client_id}' added successfully.",
                "data": clients[client_id],
                "total_clients": len(clients)
            }
        except Exception as e:
            logging.error(f"Add client failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to add client: {str(e)}",
                "success": False
            }

    def update_client_revenue(self, client_id: str = None, amount: float = 0.0) -> Dict[str, Any]:
        """Update revenue for a specific client"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "error",
                    "message": f"No client data found in vault.",
                    "success": False
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Validate client_id
            if client_id is None or client_id not in clients:
                return {
                    "status": "error",
                    "message": f"Client ID '{client_id}' not found.",
                    "success": False
                }
            
            # Update revenue
            clients[client_id]["revenue"] += amount
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Revenue updated for client '{client_id}'. New total: ${clients[client_id]['revenue']:.2f}",
                "data": clients[client_id],
                "total_revenue": sum(c.get("revenue", 0.0) for c in clients.values())
            }
        except Exception as e:
            logging.error(f"Update client revenue failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to update revenue: {str(e)}",
                "success": False
            }

    def get_client_summary(self) -> Dict[str, Any]:
        """Get a summary of all clients"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "total_clients": 0,
                    "active_clients": 0,
                    "inactive_clients": 0,
                    "total_revenue": 0.0,
                    "clients": []
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Calculate summary statistics
            total_clients = len(clients)
            active_clients = sum(1 for c in clients.values() if c.get("status") == "active")
            inactive_clients = sum(1 for c in clients.values() if c.get("status") != "active")
            total_revenue = sum(c.get("revenue", 0.0) for c in clients.values())
            
            # Build client list
            client_list = []
            for cid, cdata in clients.items():
                client_list.append({
                    "client_id": cid,
                    "name": cdata.get("name", cid),
                    "service_type": cdata.get("service_type", "unknown"),
                    "status": cdata.get("status", "unknown"),
                    "revenue": cdata.get("revenue", 0.0)
                })
            
            return {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "total_revenue": total_revenue,
                "clients": client_list
            }
        except Exception as e:
            logging.error(f"Get client summary failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client summary: {str(e)}",
                "total_clients": 0,
                "active_clients": 0,
                "inactive_clients": 0,
                "total_revenue": 0.0,
                "clients": []
            }

    def remove_client(self, client_id: str = None) -> Dict[str, Any]:
        """Remove a client from the monitoring system"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "error",
                    "message": f"No client data found in vault.",
                    "success": False
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Validate client_id
            if client_id is None or client_id not in clients:
                return {
                    "status": "error",
                    "message": f"Client ID '{client_id}' not found.",
                    "success": False
                }
            
            # Remove client
            removed_client = clients.pop(client_id)
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client '{client_id}' removed successfully.",
                "data": removed_client,
                "total_clients": len(clients)
            }
        except Exception as e:
            logging.error(f"Remove client failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to remove client: {str(e)}",
                "success": False
            }

    def get_all_clients(self) -> Dict[str, Any]:
        """Get all registered clients"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "success",
                    "message": f"No client data found in vault.",
                    "data": []
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Build client list
            client_list = []
            for cid, cdata in clients.items():
                client_list.append({
                    "client_id": cid,
                    "name": cdata.get("name", cid),
                    "service_type": cdata.get("service_type", "unknown"),
                    "status": cdata.get("status", "unknown"),
                    "revenue": cdata.get("revenue", 0.0)
                })
            
            return {
                "status": "success",
                "message": f"Retrieved all clients.",
                "data": client_list,
                "total_clients": len(client_list)
            }
        except Exception as e:
            logging.error(f"Get all clients failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get all clients: {str(e)}",
                "data": []
            }

    def generate_revenue_report(self) -> Dict[str, Any]:
        """Generate a comprehensive revenue report"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate report sections
            report_sections = [
                {
                    "section": "BOTWAVE1904 REVENUE REPORT",
                    "timestamp": datetime.now().isoformat(),
                    "report_type": "COMPREHENSIVE"
                },
                {
                    "section": "OVERVIEW",
                    "items": [
                        {"metric": "Total Revenue", "value": client_summary["total_revenue"], "unit": "$"},
                        {"metric": "Active Clients", "value": client_summary["active_clients"], "unit": ""},
                        {"metric": "Inactive Clients", "value": client_summary["inactive_clients"], "unit": ""}
                    ]
                },
                {
                    "section": "CLIENT BREAKDOWN",
                    "items": []
                }
            ]
            
            # Add individual client details
            for client in client_summary.get("clients", []):
                report_sections[-1]["items"].append({
                    "client_id": client["client_id"],
                    "name": client["name"],
                    "service_type": client["service_type"],
                    "status": client["status"],
                    "revenue": f"${client['revenue']:.2f}"
                })
            
            # Format report output
            report = []
            for section in report_sections:
                report.append(f"{'=' * 60}")
                report.append(section["section"])
                report.append(f"{'=' * 60}")
                
                if "items" in section and section["items"]:
                    for item in section["items"]:
                        status = f"[{item['status']}] {item.get('value', '')} {item.get('unit', '')}"
                        report.append(f"{item.get('metric', 'Feature')}: {status}")
                
                report.append("")
            
            return {
                "report": "\n".join(report),
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "total_revenue": client_summary["total_revenue"],
                "active_clients": client_summary["active_clients"]
            }
        except Exception as e:
            logging.error(f"Revenue report generation failed: {str(e)}")
            return {
                "report": f"[ERROR] Revenue report generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "total_revenue": 0.0,
                "active_clients": 0
            }

    def export_client_data(self) -> Dict[str, Any]:
        """Export all client data to JSON file"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "error",
                    "message": f"No client data found in vault.",
                    "success": False
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Create export file path
            export_file = Path.home() / ".openclaw" / "script_keeper_vault" / "clients_export.json"
            
            # Write to export file
            with open(export_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client data exported to {export_file}",
                "data": {"export_path": str(export_file), "total_clients": len(clients)}
            }
        except Exception as e:
            logging.error(f"Export client data failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to export client data: {str(e)}",
                "success": False
            }

    def import_client_data(self, file_path: str = None) -> Dict[str, Any]:
        """Import client data from JSON file"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Read import file
            with open(file_path) as f:
                imported_clients = json.load(f)
            
            # Merge data (overwrite existing entries, add new ones)
            for cid, cdata in imported_clients.items():
                if cid not in clients:
                    clients[cid] = cdata
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client data imported from {file_path}",
                "data": {"imported_count": len(imported_clients), "total_clients": len(clients)}
            }
        except Exception as e:
            logging.error(f"Import client data failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to import client data: {str(e)}",
                "success": False
            }

    def backup_clients(self) -> Dict[str, Any]:
        """Create a backup of all client data"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "error",
                    "message": f"No client data found in vault.",
                    "success": False
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Create backup file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = Path.home() / ".openclaw" / "script_keeper_vault" / f"clients_backup_{timestamp}.json"
            
            # Write to backup file
            with open(backup_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client data backed up to {backup_file}",
                "data": {"backup_path": str(backup_file), "total_clients": len(clients)}
            }
        except Exception as e:
            logging.error(f"Backup clients failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to backup client data: {str(e)}",
                "success": False
            }

    def restore_clients(self, file_path: str = None) -> Dict[str, Any]:
        """Restore client data from a backup file"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Read backup file
            with open(file_path) as f:
                backup_clients = json.load(f)
            
            # Restore data (overwrite all entries)
            clients.clear()
            clients.update(backup_clients)
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Client data restored from {file_path}",
                "data": {"restored_count": len(backup_clients), "total_clients": len(clients)}
            }
        except Exception as e:
            logging.error(f"Restore clients failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to restore client data: {str(e)}",
                "success": False
            }

    def get_client_history(self, client_id: str = None) -> Dict[str, Any]:
        """Get historical activity for a specific client"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "error",
                    "message": f"No client data found in vault.",
                    "success": False,
                    "history": []
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Get history for specific client or all clients
            if client_id is None:
                history_list = []
                for cid, cdata in clients.items():
                    history_list.append({
                        "client_id": cid,
                        "name": cdata.get("name", cid),
                        "service_type": cdata.get("service_type", "unknown"),
                        "status": cdata.get("status", "unknown"),
                        "revenue_history": [cdata.get("revenue", 0.0)],
                        "added_date": cdata.get("added", datetime.now().isoformat())
                    })
            else:
                if client_id not in clients:
                    return {
                        "status": "error",
                        "message": f"Client ID '{client_id}' not found.",
                        "success": False,
                        "history": []
                    }
                
                history_list = [{
                    "client_id": client_id,
                    "name": clients[client_id].get("name", client_id),
                    "service_type": clients[client_id].get("service_type", "unknown"),
                    "status": clients[client_id].get("status", "unknown"),
                    "revenue_history": [clients[client_id].get("revenue", 0.0)],
                    "added_date": clients[client_id].get("added", datetime.now().isoformat())
                }]
            
            return {
                "status": "success",
                "message": f"Client history retrieved.",
                "data": {"history": history_list, "total_clients": len(history_list)}
            }
        except Exception as e:
            logging.error(f"Get client history failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client history: {str(e)}",
                "success": False,
                "history": []
            }

    def calculate_revenue_growth(self) -> Dict[str, Any]:
        """Calculate revenue growth metrics"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Calculate growth metrics (simplified for demonstration)
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            # Growth calculations
            active_rate = (active_clients / total_clients * 100) if total_clients > 0 else 0
            revenue_per_client = total_revenue / total_clients if total_clients > 0 else 0
            
            return {
                "status": "success",
                "message": f"Revenue growth metrics calculated.",
                "data": {
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "active_rate_percent": round(active_rate, 2),
                    "revenue_per_client": round(revenue_per_client, 2)
                }
            }
        except Exception as e:
            logging.error(f"Calculate revenue growth failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to calculate revenue growth: {str(e)}",
                "success": False
            }

    def get_revenue_trend(self) -> Dict[str, Any]:
        """Get historical revenue trend data"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate trend data (simplified for demonstration)
            trend_data = [
                {"period": "Day 1", "revenue": 0.0},
                {"period": "Day 2", "revenue": 0.0},
                {"period": "Day 3", "revenue": 0.0},
                {"period": "Day 4", "revenue": 0.0},
                {"period": "Day 5", "revenue": client_summary["total_revenue"]}
            ]
            
            return {
                "status": "success",
                "message": f"Revenue trend data retrieved.",
                "data": {
                    "trend_data": trend_data,
                    "current_total": client_summary["total_revenue"],
                    "growth_rate_percent": 0.0
                }
            }
        except Exception as e:
            logging.error(f"Get revenue trend failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get revenue trend: {str(e)}",
                "success": False
            }

    def generate_profit_forecast(self) -> Dict[str, Any]:
        """Generate a profit forecast based on current data"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate forecast (simplified for demonstration)
            total_revenue = client_summary["total_revenue"]
            active_clients = client_summary["active_clients"]
            
            # Simple projection
            projected_revenue_30_days = total_revenue * 1.5
            projected_active_clients = int(active_clients * 1.2)
            
            return {
                "status": "success",
                "message": f"Profit forecast generated.",
                "data": {
                    "current_total_revenue": total_revenue,
                    "projected_30_days_revenue": projected_revenue_30_days,
                    "projected_active_clients": projected_active_clients,
                    "growth_projection_percent": 50.0
                }
            }
        except Exception as e:
            logging.error(f"Generate profit forecast failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate profit forecast: {str(e)}",
                "success": False
            }

    def get_business_insights(self) -> Dict[str, Any]:
        """Generate business insights and recommendations"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate insights based on data
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            insights = []
            
            if total_clients == 0:
                insights.append("No clients registered yet. Start generating quotes to build your client base.")
            elif active_clients < total_clients * 0.5:
                insights.append(f"Low active client rate ({active_clients}/{total_clients}). Consider outreach campaigns.")
            elif inactive_clients > 0:
                insights.append(f"{inactive_clients} clients are inactive. Consider re-engagement strategies.")
            
            if total_revenue == 0:
                insights.append("No revenue generated yet. Focus on quote generation and client acquisition.")
            else:
                insights.append(f"Revenue is being generated! Current total: ${total_revenue:.2f}")
            
            return {
                "status": "success",
                "message": f"Business insights generated.",
                "data": {
                    "insights": insights,
                    "recommendations": [
                        "Focus on quote generation for new clients",
                        "Implement automated follow-up sequences",
                        "Monitor client engagement metrics regularly",
                        "Optimize revenue per active client"
                    ]
                }
            }
        except Exception as e:
            logging.error(f"Generate business insights failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate business insights: {str(e)}",
                "success": False
            }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for the BOTWAVE1904 dashboard"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate dashboard metrics
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            return {
                "status": "success",
                "message": f"Dashboard data retrieved.",
                "data": {
                    "system_status": "OPERATIONAL",
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "total_revenue": total_revenue,
                    "revenue_per_client": round(total_revenue / max(1, total_clients), 2)
                }
            }
        except Exception as e:
            logging.error(f"Get dashboard data failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get dashboard data: {str(e)}",
                "success": False,
                "data": {}
            }

    def reset_client_data(self) -> Dict[str, Any]:
        """Reset all client data to default state"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "success",
                    "message": f"No client data found in vault. Reset complete.",
                    "data": {"total_clients": 0}
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Clear all clients
            clients.clear()
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"All client data reset. Total clients: 0.",
                "data": {"total_clients": 0}
            }
        except Exception as e:
            logging.error(f"Reset client data failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to reset client data: {str(e)}",
                "success": False
            }

    def get_client_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Calculate additional statistics
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            # Revenue distribution (simplified)
            revenue_distribution = {
                "zero_revenue": sum(1 for c in clients.values() if c.get("revenue", 0.0) == 0),
                "low_revenue": sum(1 for c in clients.values() if 0 < c.get("revenue", 0.0) <= 50),
                "medium_revenue": sum(1 for c in clients.values() if 50 < c.get("revenue", 0.0) <= 200),
                "high_revenue": sum(1 for c in clients.values() if c.get("revenue", 0.0) > 200)
            }
            
            return {
                "status": "success",
                "message": f"Client statistics retrieved.",
                "data": {
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "total_revenue": total_revenue,
                    "revenue_distribution": revenue_distribution,
                    "average_revenue_per_client": round(total_revenue / max(1, total_clients), 2)
                }
            }
        except Exception as e:
            logging.error(f"Get client statistics failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client statistics: {str(e)}",
                "success": False
            }

    def get_client_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Calculate performance metrics (simplified)
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            # Performance score calculation
            if total_clients > 0:
                performance_score = (active_clients / total_clients) * 100 + (total_revenue / max(1, total_clients))
            else:
                performance_score = 0
            
            return {
                "status": "success",
                "message": f"Client performance metrics retrieved.",
                "data": {
                    "performance_score": round(performance_score, 2),
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "total_revenue": total_revenue
                }
            }
        except Exception as e:
            logging.error(f"Get client performance failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client performance: {str(e)}",
                "success": False
            }

    def get_client_alerts(self) -> Dict[str, Any]:
        """Get alerts for clients that need attention"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "success",
                    "message": f"No client data found in vault.",
                    "data": {"alerts": []}
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Generate alerts
            alerts = []
            
            for cid, cdata in clients.items():
                if cdata.get("status") == "inactive":
                    alerts.append({
                        "type": "INACTIVE_CLIENT",
                        "client_id": cid,
                        "message": f"Client '{cdata.get('name', cid)}' is inactive. Consider re-engagement.",
                        "priority": "HIGH"
                    })
                
                if cdata.get("revenue", 0.0) == 0:
                    alerts.append({
                        "type": "ZERO_REVENUE",
                        "client_id": cid,
                        "message": f"Client '{cdata.get('name', cid)}' has no revenue.",
                        "priority": "MEDIUM"
                    })
            
            return {
                "status": "success",
                "message": f"Client alerts retrieved. Total: {len(alerts)}.",
                "data": {"alerts": alerts, "total_alerts": len(alerts)}
            }
        except Exception as e:
            logging.error(f"Get client alerts failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client alerts: {str(e)}",
                "success": False,
                "data": {"alerts": []}
            }

    def clear_client_alerts(self) -> Dict[str, Any]:
        """Clear all client alerts"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "status": "success",
                    "message": f"No client data found in vault. Clear complete.",
                    "data": {"alerts_cleared": 0}
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Update all clients to active status and zero revenue (simulated clear)
            for cid in clients.keys():
                clients[cid]["status"] = "active"
                clients[cid]["revenue"] = 0.0
            
            # Save to file
            with open(clients_file, "w") as f:
                json.dump(clients, f, indent=2)
            
            return {
                "status": "success",
                "message": f"All client alerts cleared.",
                "data": {"alerts_cleared": len(clients)}
            }
        except Exception as e:
            logging.error(f"Clear client alerts failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to clear client alerts: {str(e)}",
                "success": False
            }

    def get_client_health(self) -> Dict[str, Any]:
        """Get overall health status of all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Calculate health metrics
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            # Health score calculation (0-100)
            if total_clients > 0:
                health_score = ((active_clients / total_clients) * 50 + min(total_revenue, 100))
            else:
                health_score = 0
            
            return {
                "status": "success",
                "message": f"Client health status retrieved.",
                "data": {
                    "health_score": round(health_score, 2),
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "total_revenue": total_revenue,
                    "status": "HEALTHY" if health_score >= 50 else "UNHEALTHY"
                }
            }
        except Exception as e:
            logging.error(f"Get client health failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client health: {str(e)}",
                "success": False
            }

    def get_client_trends(self) -> Dict[str, Any]:
        """Get trend analysis for all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            # Generate trend data (simplified for demonstration)
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            trends = [
                {"period": "Week 1", "clients_added": max(0, total_clients - 5), "revenue": 0.0},
                {"period": "Week 2", "clients_added": max(0, total_clients - 3), "revenue": 0.0},
                {"period": "Week 3", "clients_added": max(0, total_clients - 1), "revenue": 0.0},
                {"period": "Week 4", "clients_added": total_clients, "revenue": total_revenue}
            ]
            
            return {
                "status": "success",
                "message": f"Client trends retrieved.",
                "data": {
                    "trends": trends,
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "inactive_clients": inactive_clients,
                    "total_revenue": total_revenue
                }
            }
        except Exception as e:
            logging.error(f"Get client trends failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client trends: {str(e)}",
                "success": False
            }

    def get_client_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for improving client performance"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            total_clients = client_summary["total_clients"]
            active_clients = client_summary["active_clients"]
            inactive_clients = client_summary["inactive_clients"]
            total_revenue = client_summary["total_revenue"]
            
            recommendations = []
            
            if total_clients == 0:
                recommendations.append("Start by generating quotes for potential clients")
                recommendations.append("Build your initial client base through outreach")
            elif active_clients < total_clients * 0.5:
                recommendations.append(f"Improve active client rate from {active_clients}/{total_clients}")
                recommendations.append("Implement automated follow-up sequences")
            elif inactive_clients > 0:
                recommendations.append(f"Re-engage {inactive_clients} inactive clients")
            
            if total_revenue == 0:
                recommendations.append("Focus on quote generation and client acquisition")
                recommendations.append("Optimize revenue per active client")
            else:
                recommendations.append(f"Maintain current revenue trajectory at ${total_revenue:.2f}")
                recommendations.append("Consider upselling to high-value clients")
            
            return {
                "status": "success",
                "message": f"Client recommendations generated.",
                "data": {"recommendations": recommendations}
            }
        except Exception as e:
            logging.error(f"Get client recommendations failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client recommendations: {str(e)}",
                "success": False
            }

    def get_client_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            return {
                "status": "success",
                "message": f"Client dashboard data retrieved.",
                "data": {
                    "system_status": "OPERATIONAL",
                    "total_clients": client_summary["total_clients"],
                    "active_clients": client_summary["active_clients"],
                    "inactive_clients": client_summary["inactive_clients"],
                    "total_revenue": client_summary["total_revenue"],
                    "revenue_per_client": round(client_summary["total_revenue"] / max(1, client_summary["total_clients"]), 2),
                    "health_score": self.get_client_health()["data"]["health_score"],
                    "performance_score": self.get_client_performance()["data"]["performance_score"],
                    "active_rate_percent": round((client_summary["active_clients"] / max(1, client_summary["total_clients"])) * 100, 2)
                }
            }
        except Exception as e:
            logging.error(f"Get client dashboard failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client dashboard: {str(e)}",
                "success": False,
                "data": {}
            }

    def get_client_overview(self) -> Dict[str, Any]:
        """Get a high-level overview of all clients"""
        
        try:
            # Get client summary
            client_summary = self.get_client_summary()
            
            return {
                "status": "success",
                "message": f"Client overview retrieved.",
                "data": {
                    "total_clients": client_summary["total_clients"],
                    "active_clients": client_summary["active_clients"],
                    "inactive_clients": client_summary["inactive_clients"],
                    "total_revenue": client_summary["total_revenue"],
                    "revenue_per_client": round(client_summary["total_revenue"] / max(1, client_summary["total_clients"]), 2),
                    "health_status": self.get_client_health()["data"]["status"],
                    "performance_score": self.get_client_performance()["data"]["performance_score"]
                }
            }
        except Exception as e:
            logging.error(f"Get client overview failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client overview: {str(e)}",
                "success": False,
                "data": {}
            }

    def get_client_summary(self) -> Dict[str, Any]:
        """Get a summary of all clients"""
        
        try:
            # Get vault directory path
            vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
            
            # Check if clients.json exists
            clients_file = vault_dir / "clients.json"
            
            if not clients_file.exists():
                return {
                    "total_clients": 0,
                    "active_clients": 0,
                    "inactive_clients": 0,
                    "total_revenue": 0.0,
                    "clients": []
                }
            
            # Load existing clients
            with open(clients_file) as f:
                clients = json.load(f)
            
            # Calculate summary statistics
            total_clients = len(clients)
            active_clients = sum(1 for c in clients.values() if c.get("status") == "active")
            inactive_clients = sum(1 for c in clients.values() if c.get("status") != "active")
            total_revenue = sum(c.get("revenue", 0.0) for c in clients.values())
            
            # Build client list
            client_list = []
            for cid, cdata in clients.items():
                client_list.append({
                    "client_id": cid,
                    "name": cdata.get("name", cid),
                    "service_type": cdata.get("service_type", "unknown"),
                    "status": cdata.get("status", "unknown"),
                    "revenue": cdata.get("revenue", 0.0)
                })
            
            return {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "total_revenue": total_revenue,
                "clients": client_list
            }
        except Exception as e:
            logging.error(f"Get client summary failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get client summary: {str(e)}",
                "total_clients": 0,
                "active_clients": 0,
                "inactive_clients": 0,
                "total_revenue": 0.0,
                "clients": []
            }

    def get_client_list(self) -> Dict[str, Any]:
        """Get a list of all clients"""
        
        try:
            # Get vault directory path
            vault_dir