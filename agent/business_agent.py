import typing as t
from agent.base_agent import BaseAgent

class BusinessAgent(BaseAgent):
    def __init__(self, model_id="qwen3.5-4b-claude-4b-os-auto-variable-heretic-uncensored-thinking"):
        super().__init__(model_id=model_id)

    def display_audit(self) -> t.Dict[str, str]:
        """Display business audit report"""
        
        try:
            # Get the audit data
            audit_data = self.get_audit_data()
            
            return {
                "status": "success",
                "message": f"Audit report generated successfully. Data: {audit_data}",
                "data": {"report": audit_data}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to generate audit report: {str(e)}"
            }

    def get_audit_data(self) -> t.Dict[str, str]:
        """Get the business audit data"""
        
        try:
            # Get the required data
            data = self.get_required_data()
            
            return {
                "status": "success",
                "message": f"Audit data retrieved successfully. Data: {data}",
                "data": {"report": data}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to retrieve audit data: {str(e)}"
            }

    def get_required_data(self) -> t.Dict[str, str]:
        """Get the required business data"""
        
        try:
            # Get the data from database
            data = self.db.get_business_data()
            
            return {
                "status": "success",
                "message": f"Data retrieved successfully. Data: {data}",
                "data": {"report": data}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to retrieve business data: {str(e)}"
            }

    def process_data(self, data: t.Dict[str, str]) -> t.Dict[str, str]:
        """Process the business data"""
        
        try:
            # Process the data
            processed_data = self.process_business_data(data)
            
            return {
                "status": "success",
                "message": f"Data processed successfully. Data: {processed_data}",
                "data": {"report": processed_data}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to process business data: {str(e)}"
            }

    def process_business_data(self, data: t.Dict[str, str]) -> t.Dict[str, str]:
        """Process the business data"""
        
        try:
            # Process the data
            processed_data = self.db.process_business_data(data)
            
            return {
                "status": "success",
                "message": f"Data processed successfully. Data: {processed_data}",
                "data": {"report": processed_data}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to process business data: {str(e)}"
            }

    def save_report(self, report: t.Dict[str, str]) -> t.Dict[str, str]:
        """Save the business report"""
        
        try:
            # Save the report
            self.db.save_business_report(report)
            
            return {
                "status": "success",
                "message": f"Report saved successfully. Report: {report}",
                "data": {"report": report}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to save business report: {str(e)}"
            }

    def get_report(self, report_id: str) -> t.Dict[str, str]:
        """Get the business report"""
        
        try:
            # Get the report
            report = self.db.get_business_report(report_id)
            
            return {
                "status": "success",
                "message": f"Report retrieved successfully. Report: {report}",
                "data": {"report": report}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to retrieve business report: {str(e)}"
            }

    def delete_report(self, report_id: str) -> t.Dict[str, str]:
        """Delete the business report"""
        
        try:
            # Delete the report
            self.db.delete_business_report(report_id)
            
            return {
                "status": "success",
                "message": f"Report deleted successfully. Report ID: {report_id}",
                "data": {"report_id": report_id}
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to delete business report: {str(e)}"
            }

    def __del__(self):
        """Destructor for cleanup"""
        
        try:
            self.db.close_connection()
        except Exception:
            pass
