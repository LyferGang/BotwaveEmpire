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
from core.secrets_vault import vault
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
        "starter": {"price_id": os.getenv("STRIPE_PRICE_ID_STARTER"), "amount": 4900},
        "professional": {"price_id": os.getenv("STRIPE_PRICE_ID_PROFESSIONAL"), "amount": 14900}
    }

    if plan not in PLANS:
        return jsonify({"error": "Invalid plan"}), 400

    try:
        session_data = stripe_service.create_checkout_session(
            success_url=f"{request.host_url}checkout/success",
            cancel_url=f"{request.host_url}checkout/canceled",
            line_items=[{"price": PLANS[plan]["price_id"], "quantity": 1}]
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


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('initial_state', {
        'agents': DashboardState.agents,
        'recent_tasks': DashboardState.recent_tasks,
        'system_stats': DashboardState.system_stats,
        'stripe_enabled': DashboardState.stripe_enabled
    })


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
