#!/usr/bin/env python3
"""
BOTWAVE EVENT HANDLER
Processes cron jobs and webhook triggers to create agent jobs.

Modeled after thepopebot's lib/actions.js and lib/cron.js
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class EventHandler:
    """Handles cron jobs and webhook triggers."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        self.jobs_dir = self.base_dir / "agent-jobs"
        self.logs_dir = self.base_dir / "logs"

        # Ensure directories exist
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        self.crons_file = self.config_dir / "CRONS.json"
        self.triggers_file = self.config_dir / "TRIGGERS.json"
        self.agent_md = self.config_dir / "AGENT.md"

    def load_crons(self) -> List[Dict]:
        """Load cron jobs from config."""
        if not self.crons_file.exists():
            return []
        with open(self.crons_file) as f:
            return json.load(f)

    def load_triggers(self) -> List[Dict]:
        """Load webhook triggers from config."""
        if not self.triggers_file.exists():
            return []
        with open(self.triggers_file) as f:
            return json.load(f)

    def load_agent_instructions(self) -> str:
        """Load agent instructions from AGENT.md."""
        if not self.agent_md.exists():
            return "You are Botwave, an AI assistant for business automation."
        with open(self.agent_md) as f:
            return f.read()

    def create_job(self, name: str, task: str, files: List[str] = None,
                   instructions: str = None, trigger_type: str = "manual") -> str:
        """
        Create an agent job.

        Returns job ID.
        """
        job_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        job = {
            "id": job_id,
            "name": name,
            "task": task,
            "files": files or [],
            "instructions": instructions or self.load_agent_instructions(),
            "trigger_type": trigger_type,
            "created_at": timestamp,
            "status": "pending"
        }

        # Save job file
        job_file = self.jobs_dir / f"{timestamp}_{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        # Create job log directory
        log_dir = self.logs_dir / f"job_{job_id}"
        log_dir.mkdir(parents=True, exist_ok=True)

        print(f"Created job: {job_id} ({name})")
        return job_id

    def run_job(self, job_id: str) -> bool:
        """
        Run an agent job using aider + LM Studio.

        Returns True if successful.
        """
        # Find job file
        job_files = list(self.jobs_dir.glob(f"*_{job_id}.json"))
        if not job_files:
            print(f"Job not found: {job_id}")
            return False

        job_file = job_files[0]
        with open(job_file) as f:
            job = json.load(f)

        print(f"Running job: {job['name']}")

        # Create instruction file for aider
        instruction_file = self.jobs_dir / f"{job['created_at']}_{job_id}.md"
        with open(instruction_file, 'w') as f:
            f.write(f"# Agent Job: {job['name']}\n\n")
            f.write(f"## Task\n{job['task']}\n\n")
            if job.get('files'):
                f.write(f"## Files to Modify\n{', '.join(job['files'])}\n\n")
            f.write(f"## Instructions\n{job['instructions']}\n")

        # Update job status
        job['status'] = 'running'
        job['started_at'] = datetime.now().isoformat()
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        # Launch aider
        log_file = self.logs_dir / f"job_{job_id}" / "aider.log"

        try:
            # Check if LM Studio is running
            import requests
            resp = requests.get("http://localhost:1234/v1/models", timeout=2)
            if resp.status_code != 200:
                raise Exception("LM Studio not responding")
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = f"LM Studio not available: {e}"
            with open(job_file, 'w') as f:
                json.dump(job, f, indent=2)
            return False

        # Run aider via the 'aid' alias
        # Note: We need to run this in a shell to get the alias
        cmd = f"cd {self.base_dir} && aid {instruction_file}"

        with open(log_file, 'w') as log:
            log.write(f"Starting job at {datetime.now().isoformat()}\n")
            log.write(f"Command: {cmd}\n\n")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            log.write(f"STDOUT:\n{result.stdout}\n\n")
            log.write(f"STDERR:\n{result.stderr}\n\n")
            log.write(f"Return code: {result.returncode}\n")

        # Update job status
        if result.returncode == 0:
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            print(f"Job completed: {job_id}")
        else:
            job['status'] = 'failed'
            job['error'] = result.stderr[:500] if result.stderr else "Unknown error"
            print(f"Job failed: {job_id}")

        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        return result.returncode == 0

    def process_webhook(self, payload: Dict, secret: str = None) -> Dict:
        """
        Process a webhook trigger.

        Returns job info if created.
        """
        triggers = self.load_triggers()

        for trigger in triggers:
            # Check if this webhook matches
            if trigger.get('path') == payload.get('path'):
                if secret and trigger.get('secret') != secret:
                    return {"error": "Invalid secret"}

                # Create job from trigger
                job_id = self.create_job(
                    name=trigger.get('name', 'Webhook Job'),
                    task=trigger.get('task', ''),
                    files=trigger.get('files', []),
                    instructions=trigger.get('instructions', ''),
                    trigger_type='webhook'
                )

                # Run the job
                self.run_job(job_id)

                return {"job_id": job_id, "status": "created"}

        return {"error": "No matching trigger found"}

    def run_all_crons(self):
        """Run all cron jobs (for testing)."""
        crons = self.load_crons()
        print(f"Found {len(crons)} cron jobs")

        for cron in crons:
            job_id = self.create_job(
                name=cron.get('name', 'Cron Job'),
                task=cron.get('task', ''),
                files=cron.get('files', []),
                instructions=cron.get('instructions', ''),
                trigger_type='cron'
            )
            self.run_job(job_id)

    def status(self) -> Dict:
        """Get status of all jobs."""
        jobs = []
        for job_file in sorted(self.jobs_dir.glob("*.json")):
            if '_trigger' not in job_file.name:  # Skip trigger config files
                with open(job_file) as f:
                    jobs.append(json.load(f))

        # Sort by created_at
        jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return {
            "total_jobs": len(jobs),
            "pending": len([j for j in jobs if j.get('status') == 'pending']),
            "running": len([j for j in jobs if j.get('status') == 'running']),
            "completed": len([j for j in jobs if j.get('status') == 'completed']),
            "failed": len([j for j in jobs if j.get('status') == 'failed']),
            "recent_jobs": jobs[:10]
        }


def main():
    """CLI for event handler."""
    import argparse

    parser = argparse.ArgumentParser(description='Botwave Event Handler')
    parser.add_argument('command', choices=['status', 'run-cron', 'webhook', 'create-job', 'run-job'])
    parser.add_argument('--job-id', help='Job ID to run')
    parser.add_argument('--name', help='Job name')
    parser.add_argument('--task', help='Job task')
    parser.add_argument('--payload', help='Webhook payload (JSON)')
    parser.add_argument('--secret', help='Webhook secret')

    args = parser.parse_args()

    handler = EventHandler()

    if args.command == 'status':
        status = handler.status()
        print(f"\nBotwave Event Handler Status")
        print(f"  Total jobs: {status['total_jobs']}")
        print(f"  Pending: {status['pending']}")
        print(f"  Running: {status['running']}")
        print(f"  Completed: {status['completed']}")
        print(f"  Failed: {status['failed']}")

    elif args.command == 'run-cron':
        handler.run_all_crons()

    elif args.command == 'webhook':
        if args.payload:
            payload = json.loads(args.payload)
            result = handler.process_webhook(payload, args.secret)
            print(f"Webhook result: {result}")
        else:
            print("Error: --payload required")

    elif args.command == 'create-job':
        if args.name and args.task:
            job_id = handler.create_job(
                name=args.name,
                task=args.task
            )
            print(f"Created job: {job_id}")
        else:
            print("Error: --name and --task required")

    elif args.command == 'run-job':
        if args.job_id:
            handler.run_job(args.job_id)
        else:
            print("Error: --job-id required")


if __name__ == "__main__":
    main()
