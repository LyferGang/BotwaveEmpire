#!/usr/bin/env python3
"""
BOTWAVE GIT WORKFLOW
Branch-per-job workflow modeled after thepopebot's GitHub Actions
"""

import subprocess
import os
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class GitWorkflow:
    """Handle Git operations for branch-per-job workflow."""

    # Branch naming convention from thepopebot
    BRANCH_PREFIX = "agent-job"
    ALLOWED_PATHS = [
        "*.py",
        "*.js",
        "*.html",
        "*.css",
        "*.md",
        "*.json",
        "*.yml",
        "*.yaml",
        "config/**",
        "website/**",
        "dashboard/**",
        "src/**",
        "scripts/**",
        "skills/**",
        "agent-jobs/**"
    ]

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.git = "git"

    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = [self.git] + args
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repo."""
        try:
            result = self._run_git(["rev-parse", "--git-dir"], check=False)
            return result.returncode == 0
        except:
            return False

    def get_current_branch(self) -> str:
        """Get current git branch."""
        result = self._run_git(["branch", "--show-current"])
        return result.stdout.strip()

    def get_default_branch(self) -> str:
        """Get the default branch (main or master)."""
        for branch in ["main", "master"]:
            result = self._run_git(["rev-parse", "--verify", branch], check=False)
            if result.returncode == 0:
                return branch
        return "main"

    def create_job_branch(self, job_id: str, job_name: str) -> str:
        """
        Create a new branch for an agent job.

        Returns the branch name.
        """
        # Sanitize job name for branch name
        safe_name = re.sub(r'[^\w\-]', '-', job_name.lower())
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"{self.BRANCH_PREFIX}/{timestamp}-{safe_name[:30]}-{job_id[:8]}"

        # Get default branch
        default_branch = self.get_default_branch()

        # Create branch from default
        self._run_git(["checkout", "-b", branch_name, default_branch])

        print(f"Created branch: {branch_name}")
        return branch_name

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Commit changes with a message.

        Returns True if successful.
        """
        try:
            # Check if there are changes
            status = self._run_git(["status", "--porcelain"], check=False)
            if not status.stdout.strip():
                print("No changes to commit")
                return True

            # Add files
            if files:
                for file in files:
                    if Path(file).exists():
                        self._run_git(["add", file])
            else:
                self._run_git(["add", "-A"])

            # Commit
            self._run_git(["commit", "-m", message])
            print(f"Committed: {message[:50]}...")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Commit failed: {e.stderr}")
            return False

    def push_branch(self, branch_name: str, remote: str = "origin") -> bool:
        """
        Push branch to remote.

        Returns True if successful.
        """
        try:
            self._run_git(["push", "-u", remote, branch_name])
            print(f"Pushed branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Push failed: {e.stderr}")
            return False

    def create_pr(self, branch_name: str, title: str, body: str) -> Optional[str]:
        """
        Create a Pull Request using GitHub CLI.

        Returns PR URL if successful.
        """
        try:
            # Check if gh CLI is available
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                check=False
            )
            if result.returncode != 0:
                print("GitHub CLI not available, skipping PR creation")
                return None

            # Create PR
            cmd = [
                "gh", "pr", "create",
                "--title", title,
                "--body", body,
                "--head", branch_name,
                "--base", self.get_default_branch()
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                print(f"Created PR: {pr_url}")
                return pr_url
            else:
                print(f"PR creation failed: {result.stderr}")
                return None

        except FileNotFoundError:
            print("GitHub CLI (gh) not found")
            return None

    def merge_pr(self, branch_name: str, delete_branch: bool = True) -> bool:
        """
        Merge PR for a branch.

        Returns True if successful.
        """
        try:
            # Use gh to merge
            cmd = ["gh", "pr", "merge", branch_name, "--squash", "--auto"]
            if delete_branch:
                cmd.append("--delete-branch")

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"Merged PR for {branch_name}")
                return True
            else:
                print(f"Merge failed: {result.stderr}")
                return False

        except FileNotFoundError:
            print("GitHub CLI not available for merge")
            return False

    def get_changed_files(self) -> List[str]:
        """Get list of changed files."""
        result = self._run_git(["diff", "--name-only", "HEAD"], check=False)
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split('\n') if f]
        return []

    def validate_changes(self, changed_files: List[str]) -> Dict:
        """
        Validate changed files against allowed paths.

        Returns validation result.
        """
        import fnmatch

        violations = []
        allowed = []

        for file in changed_files:
            is_allowed = False
            for pattern in self.ALLOWED_PATHS:
                if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(os.path.basename(file), pattern):
                    is_allowed = True
                    break

            if is_allowed:
                allowed.append(file)
            else:
                violations.append(file)

        return {
            "valid": len(violations) == 0,
            "allowed_files": allowed,
            "violations": violations
        }

    def cleanup_old_branches(self, days: int = 7) -> int:
        """
        Clean up old agent-job branches.

        Returns number of branches deleted.
        """
        deleted = 0

        # Get all branches
        result = self._run_git(["branch", "--list", f"{self.BRANCH_PREFIX}/*", "--format=%(refname:short)%(committerdate:unix)"], check=False)

        if result.returncode != 0:
            return 0

        now = datetime.now().timestamp()
        cutoff = now - (days * 24 * 60 * 60)

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            # Parse branch name and timestamp
            branch = line.rstrip('0123456789')
            try:
                timestamp = int(line[len(branch):])
            except:
                continue

            if timestamp < cutoff:
                try:
                    self._run_git(["branch", "-D", branch])
                    print(f"Deleted old branch: {branch}")
                    deleted += 1
                except:
                    pass

        return deleted


def main():
    """CLI for git workflow."""
    import argparse

    parser = argparse.ArgumentParser(description='Botwave Git Workflow')
    parser.add_argument('command', choices=[
        'create-branch', 'commit', 'push', 'create-pr',
        'merge', 'validate', 'cleanup'
    ])
    parser.add_argument('--job-id', help='Job ID')
    parser.add_argument('--job-name', help='Job name')
    parser.add_argument('--message', help='Commit message')
    parser.add_argument('--title', help='PR title')
    parser.add_argument('--body', help='PR body')
    parser.add_argument('--branch', help='Branch name')
    parser.add_argument('--days', type=int, default=7, help='Days for cleanup')

    args = parser.parse_args()

    workflow = GitWorkflow()

    if not workflow.is_git_repo():
        print("Error: Not a git repository")
        return 1

    if args.command == 'create-branch':
        if args.job_id and args.job_name:
            branch = workflow.create_job_branch(args.job_id, args.job_name)
            print(f"Created: {branch}")
        else:
            print("Error: --job-id and --job-name required")

    elif args.command == 'commit':
        if args.message:
            workflow.commit_changes(args.message)
        else:
            print("Error: --message required")

    elif args.command == 'push':
        if args.branch:
            workflow.push_branch(args.branch)
        else:
            print("Error: --branch required")

    elif args.command == 'create-pr':
        if args.branch and args.title:
            url = workflow.create_pr(args.branch, args.title, args.body or "")
            if url:
                print(f"PR URL: {url}")
        else:
            print("Error: --branch and --title required")

    elif args.command == 'merge':
        if args.branch:
            workflow.merge_pr(args.branch)
        else:
            print("Error: --branch required")

    elif args.command == 'validate':
        files = workflow.get_changed_files()
        result = workflow.validate_changes(files)
        print(json.dumps(result, indent=2))

    elif args.command == 'cleanup':
        count = workflow.cleanup_old_branches(args.days)
        print(f"Cleaned up {count} old branches")


if __name__ == "__main__":
    import json
    main()
