"""
Botwave API Server
FastAPI-based REST API for agent management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from core.config import Config
from agents.business_agent import BusinessAgent
from agents.plumbing_agent import PlumbingAgent
from agents.intelligence_agent import IntelligenceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Botwave Empire API",
    description="Professional multi-agent automation platform",
    version="1.0.0"
)

# Request/Response models
class TaskRequest(BaseModel):
    action: str
    data: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = {}

# Agent registry
AGENTS = {
    "business": BusinessAgent,
    "plumbing": PlumbingAgent,
    "intelligence": IntelligenceAgent
}

@app.on_event("startup")
async def startup():
    """Initialize application."""
    Config.ensure_directories()
    logger.info("Botwave API started")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents_available": list(AGENTS.keys())
    }

@app.get("/agents")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            {
                "name": name,
                "description": agent_class.__doc__.split("\n")[0] if agent_class.__doc__ else "No description"
            }
            for name, agent_class in AGENTS.items()
        ]
    }

@app.post("/agents/{agent_name}/run")
async def run_agent(agent_name: str, request: TaskRequest):
    """Execute an agent task."""
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    try:
        agent_class = AGENTS[agent_name]
        agent = agent_class()

        # Execute task
        result = agent.run({"action": request.action, **request.data})

        return TaskResponse(
            status=result.get("status", "unknown"),
            message=result.get("message", ""),
            data=result.get("data", {})
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_name}/health")
async def agent_health(agent_name: str):
    """Check agent health."""
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    try:
        agent_class = AGENTS[agent_name]
        agent = agent_class()
        return agent.health_check()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
