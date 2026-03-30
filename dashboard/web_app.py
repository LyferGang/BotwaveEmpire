#!/usr/bin/env python3
"""
Botwave - Web Dashboard
Professional interactive web GUI for agent management with Stripe payments
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
try:
    from core.secrets_vault import vault
except ImportError:
    try:
        from core.secrets import secrets as vault
    except ImportError:
        vault = type('obj', (object,), {'get': lambda self, x: os.getenv(x)})()
from agents.business_agent import BusinessAgent
from agents.service_agent import ServiceAgent
from agents.intelligence_agent import IntelligenceAgent

# Import Stripe integration
try:
    from integrations.stripe_integration import stripe_service
    STRIPE_ENABLED = stripe_service.is_configured()
except Exception as e:
    STRIPE_ENABLED = False
    logging.warning(f"Stripe not configured: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.API_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Task queue for async execution
task_queue = {}
task_results = {}


class DashboardState:
    """Global dashboard state."""
    agents = {
        "business": {"name": "Business Agent", "status": "ready", "description": "Financial audits, compliance reports, business analytics"},
        "service": {"name": "Service Agent", "status": "ready", "description": "Customer quotes, scheduling, issue classification"},
        "intelligence": {"name": "Intelligence Agent", "status": "ready", "description": "LLM-powered analysis, code review, content generation"},
    }
    recent_tasks = []
    system_stats = {
        "cpu": 0,
        "memory": 0,
        "disk": 0,
        "uptime": datetime.now().isoformat()
    }
    stripe_enabled = STRIPE_ENABLED


def get_agent_instance(agent_name: str):
    """Get agent instance by name."""
    agents = {
        "business": BusinessAgent,
        "service": ServiceAgent,
        "intelligence": IntelligenceAgent,
    }
    if agent_name in agents:
        return agents[agent_name]()
    return None


def execute_task_async(task_id: str, agent_name: str, action: str, data: dict):
    """Execute agent task asynchronously."""
    try:
        task_queue[task_id]["status"] = "running"
        socketio.emit('task_update', {'task_id': task_id, 'status': 'running', 'agent': agent_name})

        agent = get_agent_instance(agent_name)
        if agent:
            result = agent.run({"action": action, **data})
        else:
            result = {"status": "error", "message": f"Unknown agent: {agent_name}"}

        task_results[task_id] = result
        task_queue[task_id]["status"] = "completed"
        task_queue[task_id]["completed_at"] = datetime.now().isoformat()

        socketio.emit('task_complete', {'task_id': task_id, 'status': 'completed', 'result': result})

        DashboardState.recent_tasks.insert(0, {
            "id": task_id, "agent": agent_name, "action": action,
            "status": "completed", "timestamp": datetime.now().isoformat()
        })
        DashboardState.recent_tasks = DashboardState.recent_tasks[:50]
        socketio.emit('recent_tasks', {'tasks': DashboardState.recent_tasks})

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_queue[task_id]["status"] = "failed"
        task_queue[task_id]["error"] = str(e)
        socketio.emit('task_complete', {'task_id': task_id, 'status': 'failed', 'error': str(e)})


@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('dashboard.html',
                          agents=DashboardState.agents,
                          stripe_enabled=DashboardState.stripe_enabled,
                          stripe_key=vault.get("stripe.publishable_key") or os.getenv("STRIPE_PUBLISHABLE_KEY"))


@app.route('/pricing')
def pricing():
    """Pricing page."""
    return redirect('/website/pricing.html')


@app.route('/api/agents')
def api_list_agents():
    """List all available agents."""
    return jsonify({"agents": [{"id": k, **v} for k, v in DashboardState.agents.items()]})


@app.route('/api/agents/<agent_name>/health')
def api_agent_health(agent_name):
    """Check agent health."""
    try:
        agent = get_agent_instance(agent_name)
        if agent:
            return jsonify(agent.health_check())
        return jsonify({"status": "unknown", "error": "Agent not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/tasks', methods=['GET'])
def api_list_tasks():
    """List all tasks."""
    return jsonify({"queue": task_queue, "results": task_results, "recent": DashboardState.recent_tasks})


@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """Create and execute a new task."""
    data = request.json or {}
    agent_name = data.get("agent")
    action = data.get("action", "run")

    if not agent_name:
        return jsonify({"error": "agent is required"}), 400

    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{agent_name}"
    task_queue[task_id] = {
        "id": task_id, "agent": agent_name, "action": action, "data": data,
        "status": "pending", "created_at": datetime.now().isoformat()
    }

    threading.Thread(target=execute_task_async, args=(task_id, agent_name, action, data)).start()
    return jsonify({"task_id": task_id, "status": "pending"})


@app.route('/api/system/stats')
def api_system_stats():
    """Get system statistics."""
    try:
        import psutil
        DashboardState.system_stats = {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "uptime": datetime.now().isoformat()
        }
    except:
        pass
    return jsonify(DashboardState.system_stats)


@app.route('/api/stripe/status')
def api_stripe_status():
    """Get Stripe configuration status."""
    return jsonify({
        "enabled": STRIPE_ENABLED,
        "has_secret_key": bool(stripe_service.api_key if STRIPE_ENABLED else False),
        "has_publishable_key": bool(stripe_service.publishable_key if STRIPE_ENABLED else False)
    })


@app.route('/api/stripe/create-checkout-session', methods=['POST'])
def api_create_checkout_session():
    """Create Stripe checkout session."""
    if not STRIPE_ENABLED:
        return jsonify({"error": "Stripe not configured"}), 503

    data = request.json or {}
    plan = data.get("plan", "professional")

    PLANS = {
        "starter": {"price_id": os.getenv("STRIPE_PRICE_ID_STARTER"), "amount": 29900, "name": "Starter"},
        "professional": {"price_id": os.getenv("STRIPE_PRICE_ID_PROFESSIONAL"), "amount": 49900, "name": "Professional"},
        "enterprise": {"price_id": os.getenv("STRIPE_PRICE_ID_ENTERPRISE"), "amount": 149900, "name": "Enterprise"}
    }

    if plan not in PLANS:
        return jsonify({"error": "Invalid plan"}), 400

    try:
        session_data = stripe_service.create_checkout_session(
            success_url=f"{request.host_url}checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}checkout/canceled",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": PLANS[plan]["amount"],
                    "product_data": {"name": f"Botwave {PLANS[plan]['name']} Plan", "description": "AI Automation Platform"}
                },
                "quantity": 1
            }],
            mode="subscription" if plan != "enterprise" else "payment"
        )
        return jsonify({"session_id": session_data["id"], "url": session_data["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/checkout/success')
def checkout_success():
    """Checkout success page."""
    return render_template('checkout_success.html')


@app.route('/checkout/canceled')
def checkout_canceled():
    """Checkout canceled page."""
    return render_template('checkout_canceled.html')


# =============================================================================
# CUSTOMER PORTAL API
# =============================================================================

@app.route('/api/customer/stats/<telegram_id>')
def api_customer_stats(telegram_id):
    """Get customer statistics."""
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path("data/plumbing_customers.db")
        if not db_path.exists():
            return jsonify({"error": "Database not initialized"}), 404

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get customer info
            customer = conn.execute(
                "SELECT * FROM customers WHERE telegram_id = ?",
                (telegram_id,)
            ).fetchone()

            # Get quote count
            quotes = conn.execute(
                "SELECT COUNT(*) FROM quotes WHERE telegram_id = ?",
                (telegram_id,)
            ).fetchone()[0]

            # Get appointment count
            appointments = conn.execute(
                "SELECT COUNT(*) FROM appointments WHERE telegram_id = ? AND status = 'scheduled'",
                (telegram_id,)
            ).fetchone()[0]

            # Get completed services
            completed = conn.execute(
                "SELECT COUNT(*) FROM appointments WHERE telegram_id = ? AND status = 'completed'",
                (telegram_id,)
            ).fetchone()[0]

            return jsonify({
                "telegram_id": telegram_id,
                "name": customer['name'] if customer else "Customer",
                "stats": {
                    "activeQuotes": quotes,
                    "scheduledAppointments": appointments,
                    "completedServices": completed,
                    "totalSpent": 0  # Calculate from actual invoices
                }
            })
    except Exception as e:
        logger.error(f"Error fetching customer stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/customer/quotes/<telegram_id>')
def api_customer_quotes(telegram_id):
    """Get customer quotes."""
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path("data/plumbing_customers.db")
        if not db_path.exists():
            return jsonify({"quotes": []})

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT * FROM quotes
                   WHERE telegram_id = ?
                   ORDER BY created_at DESC""",
                (telegram_id,)
            ).fetchall()

            quotes = [dict(row) for row in rows]
            return jsonify({"quotes": quotes})
    except Exception as e:
        logger.error(f"Error fetching customer quotes: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/customer/appointments/<telegram_id>')
def api_customer_appointments(telegram_id):
    """Get customer appointments."""
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path("data/plumbing_customers.db")
        if not db_path.exists():
            return jsonify({"appointments": []})

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT * FROM appointments
                   WHERE telegram_id = ?
                   ORDER BY scheduled_date DESC""",
                (telegram_id,)
            ).fetchall()

            appointments = [dict(row) for row in rows]
            return jsonify({"appointments": appointments})
    except Exception as e:
        logger.error(f"Error fetching customer appointments: {e}")
        return jsonify({"error": str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('initial_state', {
        'agents': DashboardState.agents,
        'recent_tasks': DashboardState.recent_tasks,
        'system_stats': DashboardState.system_stats,
        'stripe_enabled': DashboardState.stripe_enabled
    })



@app.route('/api/leads', methods=['POST'])
def api_capture_lead():
    """Capture lead from website form."""
    import sqlite3

    data = request.json or {}
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    service_interest = data.get('service_interest')
    message = data.get('message', '')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    lead_id = f"LEAD_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leads (id, name, phone, email, service_interest, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lead_id, name, phone, email, service_interest, message))

        conn.commit()
        conn.close()

        # Send notification to Telegram
        try:
            self._notify_new_lead(name, phone, service_interest)
        except:
            pass  # Non-critical

        return jsonify({
            "status": "success",
            "lead_id": lead_id,
            "message": "Thank you! We'll contact you within 24 hours."
        })

    except Exception as e:
        logger.error(f"Lead capture failed: {e}")
        return jsonify({"error": "Failed to capture lead"}), 500


@app.route('/api/leads', methods=['GET'])
def api_list_leads():
    """List all leads (admin only)."""
    import sqlite3

    try:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
        leads = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({"leads": leads, "count": len(leads)})

    except Exception as e:
        logger.error(f"Failed to list leads: {e}")
        return jsonify({"error": str(e)}), 500


def _notify_new_lead(self, name, phone, service_interest):
    """Send Telegram notification for new lead."""
    token = os.getenv("TG_FOREMAN_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return

    import requests
    message = f"""
🔔 *New Lead Alert*

Name: {name}
Phone: {phone}
Service: {service_interest}

Contact ASAP!
    """

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    )


def main():
    """Run the web dashboard."""
    Config.ensure_directories()
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    logger.info("Starting Botwave Web Dashboard...")
    logger.info("Access at: http://localhost:5000")
    logger.info(f"Stripe Integration: {'Enabled' if STRIPE_ENABLED else 'Disabled'}")

    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()


# =============================================================================
# REPORT GENERATION API
# =============================================================================

from report_generator import report_generator, ReportType

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """Generate a new PDF report."""
    data = request.json or {}
    report_type = data.get('report_type')
    
    if not report_type:
        return jsonify({"error": "report_type is required"}), 400
        
    try:
        if report_type == 'service':
            result = report_generator.generate_service_report(data)
        elif report_type == 'analytics':
            result = report_generator.generate_analytics_report(data)
        elif report_type == 'audit':
            result = report_generator.generate_audit_report(data)
        else:
            return jsonify({"error": f"Invalid report_type: {report_type}"}), 400
            
        return jsonify({
            "status": "success",
            "report_id": result.report_id,
            "report_type": result.report_type,
            "title": result.title,
            "file_path": result.file_path,
            "file_size": result.file_size,
            "generated_at": result.generated_at
        })
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/list', methods=['GET'])
def api_list_reports():
    """List all generated reports."""
    customer_id = request.args.get('customer_id')
    report_type = request.args.get('report_type')
    
    try:
        reports = report_generator.list_reports(
            customer_id=customer_id,
            report_type=report_type
        )
        return jsonify({
            "status": "success",
            "count": len(reports),
            "reports": reports
        })
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/<report_id>', methods=['GET'])
def api_get_report(report_id):
    """Get a specific report by ID."""
    try:
        report = report_generator.get_report(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
        return jsonify({"status": "success", "report": report})
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/download/<report_id>', methods=['GET'])
def api_download_report(report_id):
    """Download a PDF report by ID."""
    from flask import send_file
    
    try:
        report = report_generator.get_report(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
            
        file_path = Path(report['file_path'])
        if not file_path.exists():
            return jsonify({"error": "Report file not found"}), 404
            
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{report_id}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Failed to download report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/<report_id>', methods=['DELETE'])
def api_delete_report(report_id):
    """Delete a report."""
    try:
        success = report_generator.delete_report(report_id)
        if not success:
            return jsonify({"error": "Report not found"}), 404
        return jsonify({"status": "success", "message": "Report deleted"})
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/templates', methods=['GET'])
def api_report_templates():
    """Get available report templates and their schemas."""
    templates = {
        "service": {
            "name": "Service Report",
            "description": "Report for completed service jobs",
            "required_fields": ["customer_name"],
            "optional_fields": [
                "customer_id", "service_date", "service_type", "technician",
                "service_description", "work_items", "materials",
                "labor_cost", "materials_cost", "tax"
            ]
        },
        "analytics": {
            "name": "Analytics Report",
            "description": "Monthly or period-based business analytics",
            "required_fields": [],
            "optional_fields": [
                "business_name", "period", "metrics", "charts",
                "categories", "new_customers", "returning_customers", "summary"
            ]
        },
        "audit": {
            "name": "Audit Report",
            "description": "Compliance and business audit documentation",
            "required_fields": [],
            "optional_fields": [
                "audit_type", "audit_date", "auditor", "overview",
                "scope", "findings", "compliance_score", "recommendations"
            ]
        }
    }
    return jsonify({"status": "success", "templates": templates})
