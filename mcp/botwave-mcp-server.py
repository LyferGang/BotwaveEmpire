#!/usr/bin/env python3
"""
BOTWAVE MCP SERVER
Gives Claude Code access to local Botwave agents via LM Studio

Usage:
  python3 botwave-mcp-server.py

Add to Claude settings.json:
  "mcpServers": {
    "botwave": {
      "command": "python3",
      "args": ["/home/gringo/BotwaveEmpire/mcp/botwave-mcp-server.py"]
    }
  }
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

# MCP imports - using stdio transport
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, Resource, Prompt
except ImportError:
    print("Installing mcp package...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp", "-q"])
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, Resource, Prompt

# Botwave paths
BASE_DIR = Path(__file__).parent.parent
AGENT_RUNNER = BASE_DIR / "lib" / "agent_runner.py"
EVENT_HANDLER = BASE_DIR / "lib" / "event_handler.py"
SKILLS_DIR = BASE_DIR / "skills" / "active"

app = Server("botwave")


@app.list_tools()
async def list_tools():
    """List available Botwave tools."""
    return [
        Tool(
            name="botwave_agent_run",
            description="Run a coding agent task using aider + LM Studio. Breaks large tasks into smaller parallel jobs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Job name"},
                    "task": {"type": "string", "description": "Task description"},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "Files to modify"},
                    "auto_approve": {"type": "boolean", "description": "Auto-approve aider changes"}
                },
                "required": ["name", "task"]
            }
        ),
        Tool(
            name="botwave_agent_status",
            description="Check status of all agent jobs",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Optional job ID to check"}
                }
            }
        ),
        Tool(
            name="botwave_skill_list",
            description="List available skills that agents can use",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="botwave_skill_run",
            description="Run a specific skill with custom parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "Skill name (e.g., 'self-audit', 'get-secret')"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments to pass"}
                },
                "required": ["skill"]
            }
        ),
        Tool(
            name="botwave_dashboard_status",
            description="Check if Botwave dashboard is running and get URL",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="botwave_lm_studio_status",
            description="Check LM Studio server status and loaded models",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="botwave_create_parallel_jobs",
            description="Break a large task into multiple parallel agent jobs (SCRYPT KEEPER style)",
            inputSchema={
                "type": "object",
                "properties": {
                    "large_task": {"type": "string", "description": "The large task to break down"},
                    "num_agents": {"type": "integer", "description": "Number of parallel agents to spawn (2-5)"}
                },
                "required": ["large_task"]
            }
        ),
        Tool(
            name="media_generate_image",
            description="Generate AI images via Nano Banana Pro (requires KIE_API_KEY)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text description of the image"},
                    "output_name": {"type": "string", "description": "Output filename without extension"},
                    "aspect_ratio": {"type": "string", "description": "1:1, 2:3, 3:2, 16:9, etc"},
                    "resolution": {"type": "string", "description": "1K, 2K, or 4K"}
                },
                "required": ["prompt", "output_name"]
            }
        ),
        Tool(
            name="media_generate_video",
            description="Generate video from text or image via Veo 3.1 (requires KIE_API_KEY)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text description of the video"},
                    "output_name": {"type": "string", "description": "Output filename without extension"},
                    "image_urls": {"type": "array", "items": {"type": "string"}, "description": "Optional image URLs to animate"},
                    "model": {"type": "string", "description": "veo3 or veo3_fast"}
                },
                "required": ["prompt", "output_name"]
            }
        ),
        Tool(
            name="media_generate_speech",
            description="Text-to-speech via ElevenLabs (requires KIE_API_KEY)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert to speech"},
                    "output_name": {"type": "string", "description": "Output filename without extension"},
                    "voice": {"type": "string", "description": "Voice: Eric, Rachel, Aria, etc"}
                },
                "required": ["text", "output_name"]
            }
        ),
        Tool(
            name="media_transcribe",
            description="Transcribe media to text using Whisper (NCA Toolkit)",
            inputSchema={
                "type": "object",
                "properties": {
                    "media_url": {"type": "string", "description": "URL of media file to transcribe"},
                    "language": {"type": "string", "description": "Language code (en, es, etc)"}
                },
                "required": ["media_url"]
            }
        ),
        Tool(
            name="media_caption_video",
            description="Add captions to video (NCA Toolkit)",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "description": "URL of video file"},
                    "font_size": {"type": "integer", "description": "Caption font size"},
                    "font_color": {"type": "string", "description": "Caption color"}
                },
                "required": ["video_url"]
            }
        ),
        Tool(
            name="media_screenshot_webpage",
            description="Capture webpage screenshot (NCA Toolkit)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to screenshot"},
                    "viewport_width": {"type": "integer", "default": 1920},
                    "viewport_height": {"type": "integer", "default": 1080},
                    "full_page": {"type": "boolean", "default": False}
                },
                "required": ["url"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute a Botwave tool."""

    if name == "botwave_agent_run":
        return await run_agent_job(arguments)

    elif name == "botwave_agent_status":
        return await get_agent_status(arguments.get("job_id"))

    elif name == "botwave_skill_list":
        return await list_skills()

    elif name == "botwave_skill_run":
        return await run_skill(arguments["skill"], arguments.get("args", []))

    elif name == "botwave_dashboard_status":
        return await check_dashboard()

    elif name == "botwave_lm_studio_status":
        return await check_lm_studio()

    elif name == "botwave_create_parallel_jobs":
        return await create_parallel_jobs(arguments["large_task"], arguments.get("num_agents", 3))

    elif name == "media_generate_image":
        return await media_generate_image(arguments)

    elif name == "media_generate_video":
        return await media_generate_video(arguments)

    elif name == "media_generate_speech":
        return await media_generate_speech(arguments)

    elif name == "media_transcribe":
        return await media_transcribe(arguments)

    elif name == "media_caption_video":
        return await media_caption_video(arguments)

    elif name == "media_screenshot_webpage":
        return await media_screenshot_webpage(arguments)

    return {"error": f"Unknown tool: {name}"}


# Media MCP tool handlers
async def media_generate_image(args: dict) -> dict:
    """Generate AI image."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "generate-image",
        "--prompt", args["prompt"],
        "--output", args["output_name"]
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

async def media_generate_video(args: dict) -> dict:
    """Generate AI video."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "generate-video",
        "--prompt", args["prompt"],
        "--output", args["output_name"]
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

async def media_generate_speech(args: dict) -> dict:
    """Generate speech from text."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "generate-speech",
        "--text", args["text"],
        "--output", args["output_name"],
        "--voice", args.get("voice", "Eric")
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

async def media_transcribe(args: dict) -> dict:
    """Transcribe media."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "transcribe",
        "--url", args["media_url"]
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

async def media_caption_video(args: dict) -> dict:
    """Add captions to video."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "caption",
        "--url", args["video_url"]
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

async def media_screenshot_webpage(args: dict) -> dict:
    """Screenshot a webpage."""
    cmd = [
        "python3", str(BASE_DIR / "mcp" / "integrations" / "media_mcp.py"),
        "screenshot",
        "--url", args["url"]
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}


async def run_agent_job(args: dict) -> dict:
    """Run an agent job using aider."""
    cmd = [
        "python3", str(AGENT_RUNNER),
        "create",
        "--name", args["name"],
        "--task", args["task"]
    ]

    if args.get("files"):
        cmd.extend(["--files"] + args["files"])

    if args.get("auto_approve"):
        # Run the job with auto-approve
        cmd = [
            "python3", str(AGENT_RUNNER),
            "run", "--job-id", "PLACEHOLDER",  # Will be replaced
            "--auto-approve"
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_agent_status(job_id: Optional[str] = None) -> dict:
    """Get agent job status."""
    cmd = ["python3", str(AGENT_RUNNER), "list"]
    if job_id:
        cmd = ["python3", str(AGENT_RUNNER), "status", "--job-id", job_id]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}


async def list_skills() -> dict:
    """List available skills."""
    skills = []
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                skills.append({
                    "name": skill_dir.name,
                    "has_instructions": skill_md.exists()
                })
    return {"skills": skills}


async def run_skill(skill: str, args: list) -> dict:
    """Run a skill."""
    skill_path = SKILLS_DIR / skill / "audit.py"
    if not skill_path.exists():
        skill_path = SKILLS_DIR / skill / "run.py"

    if not skill_path.exists():
        return {"error": f"Skill '{skill}' not found"}

    cmd = ["python3", str(skill_path)] + args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}


async def check_dashboard() -> dict:
    """Check dashboard status."""
    import requests
    try:
        resp = requests.get("http://localhost:5000", timeout=5)
        return {
            "running": resp.status_code == 200,
            "url": "http://localhost:5000",
            "status_code": resp.status_code
        }
    except:
        return {"running": False, "error": "Dashboard not responding"}


async def check_lm_studio() -> dict:
    """Check LM Studio status."""
    import requests
    try:
        resp = requests.get("http://localhost:1234/v1/models", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("data", [])
            return {
                "running": True,
                "models": [m["id"] for m in models],
                "model_count": len(models)
            }
    except:
        pass
    return {"running": False, "error": "LM Studio not responding"}


async def create_parallel_jobs(large_task: str, num_agents: int = 3) -> dict:
    """Break large task into parallel agent jobs (SCRYPT KEEPER style)."""

    # Subtasks based on task type
    subtasks = []

    if "build" in large_task.lower() or "create" in large_task.lower():
        subtasks = [
            ("setup", "Set up project structure, config files, and dependencies"),
            ("core", "Implement core functionality and business logic"),
            ("interface", "Create user interface (web/CLI) and integrations"),
            ("test", "Add tests, error handling, and documentation"),
        ]
    elif "fix" in large_task.lower() or "debug" in large_task.lower():
        subtasks = [
            ("diagnose", "Analyze code and identify root cause of issues"),
            ("fix_core", "Fix the main bug/error"),
            ("fix_related", "Fix related issues and edge cases"),
            ("verify", "Add tests and verify the fix works"),
        ]
    else:
        # Generic breakdown
        subtasks = [
            ("analyze", "Analyze requirements and existing code"),
            ("implement", "Implement the main functionality"),
            ("integrate", "Integrate with existing systems"),
            ("document", "Add documentation and tests"),
        ]

    # Limit to requested number
    subtasks = subtasks[:num_agents]

    jobs_created = []
    for subtask_name, subtask_desc in subtasks:
        job_name = f"{large_task.split()[0:3]}_{subtask_name}"
        cmd = [
            "python3", str(AGENT_RUNNER),
            "create",
            "--name", job_name[:50],
            "--task", f"{subtask_desc} for: {large_task}"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                jobs_created.append({"name": job_name, "output": result.stdout.strip()})
        except:
            pass

    return {
        "parallel_jobs_created": len(jobs_created),
        "jobs": jobs_created,
        "message": f"SCRYPT KEEPER STYLE: Broke '{large_task}' into {len(jobs_created)} parallel agent jobs"
    }


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
