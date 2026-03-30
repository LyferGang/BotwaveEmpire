#!/usr/bin/env python3
"""
BOTWAVE AGENT RUNNER
Uses aider + LM Studio to execute coding jobs autonomously.

This is the core of the Botwave self-improving system.
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class AgentRunner:
    """Runs coding agents using aider + LM Studio."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.jobs_dir = self.base_dir / "agent-jobs"
        self.logs_dir = self.base_dir / "logs"
        self.skills_dir = self.base_dir / "skills" / "active"

        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def check_lm_studio(self) -> bool:
        """Check if LM Studio is running and has a model loaded."""
        try:
            import requests
            resp = requests.get("http://localhost:1234/v1/models", timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                if models:
                    return True
        except:
            pass
        return False

    def create_job(self, name: str, task: str, files: List[str] = None,
                   instructions: str = "", skill: str = None) -> str:
        """
        Create an agent job.

        Args:
            name: Job name
            task: Task description
            files: List of files to modify
            instructions: Detailed instructions for the agent
            skill: Optional skill to use

        Returns:
            Job ID
        """
        job_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Load skill instructions if specified
        skill_instructions = ""
        if skill:
            skill_path = self.skills_dir / skill / "SKILL.md"
            if skill_path.exists():
                skill_instructions = skill_path.read_text()

        job = {
            "id": job_id,
            "name": name,
            "task": task,
            "files": files or [],
            "instructions": instructions,
            "skill": skill,
            "skill_instructions": skill_instructions,
            "created_at": timestamp,
            "status": "pending"
        }

        # Save job file
        job_file = self.jobs_dir / f"{timestamp}_{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        print(f"Created job: {job_id} ({name})")
        return job_id

    def run_job(self, job_id: str, auto_approve: bool = False) -> bool:
        """
        Run an agent job using aider.

        Args:
            job_id: Job ID to run
            auto_approve: If True, run aider with --yes flag

        Returns:
            True if successful
        """
        # Find job file
        job_files = list(self.jobs_dir.glob(f"*_{job_id}.json"))
        if not job_files:
            print(f"Job not found: {job_id}")
            return False

        job_file = job_files[0]
        with open(job_file) as f:
            job = json.load(f)

        print(f"\n{'='*60}")
        print(f"Running Agent Job: {job['name']}")
        print(f"{'='*60}")
        print(f"Task: {job['task']}")
        print(f"Files: {', '.join(job['files']) if job['files'] else 'None specified'}")
        print(f"{'='*60}\n")

        # Update job status
        job['status'] = 'running'
        job['started_at'] = datetime.now().isoformat()
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        # Check LM Studio
        if not self.check_lm_studio():
            print("ERROR: LM Studio not running or no model loaded")
            job['status'] = 'failed'
            job['error'] = 'LM Studio not available'
            with open(job_file, 'w') as f:
                json.dump(job, f, indent=2)
            return False

        # Create instruction file for aider
        instruction_file = self.jobs_dir / f"{job['created_at']}_{job_id}.md"
        with open(instruction_file, 'w') as f:
            f.write(f"# Agent Job: {job['name']}\n\n")
            f.write(f"## Task\n{job['task']}\n\n")
            if job.get('skill'):
                f.write(f"## Skill: {job['skill']}\n")
                f.write(job.get('skill_instructions', '') + "\n\n")
            if job.get('files'):
                f.write(f"## Files to Modify\n{', '.join(job['files'])}\n\n")
            f.write(f"## Instructions\n{job['instructions']}\n")

        # Create log directory
        log_dir = self.logs_dir / f"job_{job_id}"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "aider.log"

        # Build aider command
        # Use the 'aid' alias which is configured for LM Studio
        files_arg = ' '.join(job['files']) if job['files'] else ''
        auto_flag = '--yes' if auto_approve else ''

        cmd = f"cd {self.base_dir} && aid {auto_flag} {files_arg} {instruction_file}"

        print(f"Running: {cmd}\n")

        with open(log_file, 'w') as log:
            log.write(f"Job: {job['name']}\n")
            log.write(f"Started: {job['started_at']}\n")
            log.write(f"Command: {cmd}\n\n")
            log.write("="*60 + "\n\n")

            try:
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
                    print(f"\n✅ Job completed: {job_id}")
                else:
                    job['status'] = 'failed'
                    job['error'] = result.stderr[:500] if result.stderr else "Unknown error"
                    print(f"\n❌ Job failed: {job_id}")

            except subprocess.TimeoutExpired:
                job['status'] = 'timeout'
                job['error'] = 'Job timed out after 1 hour'
                log.write(f"\nTIMEOUT: Job exceeded 1 hour limit\n")
                print(f"\n⏱ Job timed out: {job_id}")

            except Exception as e:
                job['status'] = 'failed'
                job['error'] = str(e)
                log.write(f"\nERROR: {e}\n")
                print(f"\n❌ Job error: {e}")

        # Save final job state
        with open(job_file, 'w') as f:
            json.dump(job, f, indent=2)

        return job['status'] == 'completed'

    def list_jobs(self, status: str = None) -> List[Dict]:
        """List all jobs, optionally filtered by status."""
        jobs = []
        for job_file in sorted(self.jobs_dir.glob("*.json")):
            if '_trigger' not in job_file.name:
                with open(job_file) as f:
                    job = json.load(f)
                    if status is None or job.get('status') == status:
                        jobs.append(job)

        # Sort by created_at descending
        jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return jobs

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a specific job."""
        job_files = list(self.jobs_dir.glob(f"*_{job_id}.json"))
        if not job_files:
            return None

        with open(job_files[0]) as f:
            return json.load(f)

    def get_logs(self, job_id: str) -> Optional[str]:
        """Get logs for a specific job."""
        log_file = self.logs_dir / f"job_{job_id}" / "aider.log"
        if log_file.exists():
            return log_file.read_text()
        return None


# Global instance
agent_runner = AgentRunner()


def run_agent_job(name: str, task: str, files: List[str] = None,
                  instructions: str = "", auto_approve: bool = False) -> str:
    """
    Convenience function to create and run a job.

    Returns job ID.
    """
    runner = AgentRunner()
    job_id = runner.create_job(name, task, files, instructions)
    success = runner.run_job(job_id, auto_approve)
    return job_id if success else None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Botwave Agent Runner')
    parser.add_argument('command', choices=['create', 'run', 'list', 'status', 'logs'])
    parser.add_argument('--job-id', help='Job ID')
    parser.add_argument('--name', help='Job name')
    parser.add_argument('--task', help='Job task')
    parser.add_argument('--files', nargs='*', help='Files to modify')
    parser.add_argument('--instructions', help='Job instructions')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--auto-approve', action='store_true', help='Auto-approve aider changes')

    args = parser.parse_args()

    runner = AgentRunner()

    if args.command == 'create':
        if args.name and args.task:
            job_id = runner.create_job(
                name=args.name,
                task=args.task,
                files=args.files,
                instructions=args.instructions
            )
            print(f"Created job: {job_id}")
        else:
            print("Error: --name and --task required")

    elif args.command == 'run':
        if args.job_id:
            runner.run_job(args.job_id, args.auto_approve)
        else:
            print("Error: --job-id required")

    elif args.command == 'list':
        jobs = runner.list_jobs(args.status)
        print(f"\n{'ID':<14} {'Name':<30} {'Status':<12} {'Created'}")
        print("-"*70)
        for job in jobs:
            print(f"{job['id']:<14} {job['name']:<30} {job['status']:<12} {job['created_at']}")
        print(f"\nTotal: {len(jobs)} jobs")

    elif args.command == 'status':
        if args.job_id:
            job = runner.get_job_status(args.job_id)
            if job:
                print(json.dumps(job, indent=2))
            else:
                print("Job not found")
        else:
            print("Error: --job-id required")

    elif args.command == 'logs':
        if args.job_id:
            logs = runner.get_logs(args.job_id)
            if logs:
                print(logs)
            else:
                print("No logs found")
        else:
            print("Error: --job-id required")
