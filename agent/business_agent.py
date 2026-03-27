"""
BusinessAgent - Core business operations agent
Handles audit, financial tracking, and revenue management
Mr. Robot Edition: Ruthless, efficient, profit-focused
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from agent.config import config

class BusinessAgent:
    """Always-on business operations agent"""

    def __init__(self):
        self.vault_dir = Path.home() / ".openclaw" / "script_keeper_vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.financial_data: Dict[str, Any] = {}
        
        # Load API keys for external services
        config.load_from_env()

    def display_audit(self) -> Dict[str, Any]:
        """Display business audit report"""
        
        try:
            # Generate audit data
            audit_data = {
                "timestamp": datetime.now().isoformat(),
                "total_revenue": self._get_total_revenue(),
                "active_clients": len(self.financial_data),
                "pending_proposals": 0,
                "status": "OPERATIONAL"
            }

            # Save audit to vault
            self._save_audit(audit_data)

            return {
                "status": "success", 
                "message": f"Audit complete. Total revenue: ${audit_data['total_revenue']:.2f}",
                "data": audit_data
            }
        except Exception as e:
            logging.error(f"Business agent error: {str(e)}")
            return {
                "status": "error", 
                "message": f"Audit failed: {str(e)}"
            }

    def _get_total_revenue(self) -> float:
        """Calculate total revenue from financial data"""
        
        try:
            total = sum(client.get("revenue", 0.0) for client in self.financial_data.values())
            return round(total, 2)
        except Exception as e:
            logging.error(f"Revenue calculation error: {str(e)}")
            return 0.0

    def _save_audit(self, audit_data: Dict[str, Any]) -> bool:
        """Save audit data to vault"""
        
        try:
            log_file = self.vault_dir / "audit.log"
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now().isoformat()}] {str(audit_data)}\n")
            return True
        except Exception as e:
            logging.error(f"Audit save error: {str(e)}")
            return False

    def add_client(self, client_id: str, name: str, service_type: str) -> bool:
        """Register a new business client"""
        
        try:
            # Input validation
            if not client_id or not isinstance(client_id, str):
                logging.warning(f"Invalid client_id provided")
                return False
            
            if not name or not isinstance(name, str):
                logging.warning(f"Invalid client name provided")
                return False
            
            if not service_type or not isinstance(service_type, str):
                logging.warning(f"Invalid service_type provided")
                return False

            # Check for duplicate client_id
            if client_id in self.financial_data:
                logging.warning(f"Client {client_id} already exists")
                return False

            self.financial_data[client_id] = {
                "name": name,
                "service_type": service_type,
                "added": datetime.now().isoformat(),
                "status": "active",
                "revenue": 0.0
            }
            
            # Persist to vault
            self._save_audit(self.financial_data)
            
            return True
        except Exception as e:
            logging.error(f"Client registration error: {str(e)}")
            return False

    def update_revenue(self, client_id: str, amount: float) -> bool:
        """Update client revenue"""
        
        try:
            if not isinstance(client_id, str):
                logging.warning(f"Invalid client_id type provided")
                return False
            
            if not isinstance(amount, (int, float)):
                logging.warning(f"Invalid amount type provided")
                return False

            if client_id not in self.financial_data:
                logging.warning(f"Client {client_id} not found")
                return False
            
            # Validate amount is positive
            if amount < 0:
                logging.warning(f"Negative revenue amount for client {client_id}")
                return False
            
            self.financial_data[client_id]["revenue"] += amount
            self._save_audit(self.financial_data)
            
            return True
        except Exception as e:
            logging.error(f"Revenue update error: {str(e)}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get business summary"""
        
        try:
            total_revenue = sum(c.get("revenue", 0.0) for c in self.financial_data.values())
            active_clients = len([c for c in self.financial_data.values() if c.get("status") == "active"])
            
            return {
                "total_clients": len(self.financial_data),
                "active_clients": active_clients,
                "total_revenue": round(total_revenue, 2)
            }
        except Exception as e:
            logging.error(f"Summary generation error: {str(e)}")
            return {"error": str(e)}

    def _persist(self):
        """Persist financial data to vault"""
        
        try:
            import json
            data_file = self.vault_dir / "financial_data.json"
            with open(data_file, "w") as f:
                json.dump(self.financial_data, f, indent=2)
        except Exception as e:
            logging.error(f"Persist error: {str(e)}")

    def process_payment(self, client_id: str, amount: float, payment_method: str = None) -> bool:
        """Process a payment using configured API keys"""
        
        try:
            # Check if we have payment gateway key configured
            payment_key = config.get('payment_gateway_key')
            
            if not payment_key:
                logging.warning("No payment gateway key configured. Using internal ledger only.")
                return self.update_revenue(client_id, amount)
            
            # Attempt to process through external payment service
            # This would typically make an API call with the payment key
            # Example: requests.post(payment_url, json={'key': payment_key, ...})
            
            logging.info(f"Processing {amount:.2f} for client {client_id} via payment gateway")
            
            # Simulate external payment processing
            return True
            
        except Exception as e:
            logging.error(f"Payment processing error: {str(e)}")
            return False

    def get_payment_status(self, client_id: str) -> Dict[str, Any]:
        """Get payment status for a specific client"""
        
        try:
            if not isinstance(client_id, str):
                return {"error": "Invalid client_id type"}
            
            if client_id not in self.financial_data:
                return {"error": "Client not found"}
            
            client = self.financial_data[client_id]
            return {
                "status": "success",
                "data": {
                    "total_paid": client.get("revenue", 0.0),
                    "payment_history": len(client.get("payments", [])),
                    "last_payment": client.get("last_payment")
                }
            }
        except Exception as e:
            logging.error(f"Payment status error: {str(e)}")
            return {"error": str(e)}
