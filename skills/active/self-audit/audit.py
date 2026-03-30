#!/usr/bin/env python3
"""
Self-Audit Skill - Uses aider to audit and improve Botwave code
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


class SelfAudit:
    """Self-auditing system using aider."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.audit_log = self.base_dir / "logs" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str):
        """Log message to file and stdout."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {msg}"
        print(log_line)
        with open(self.audit_log, 'a') as f:
            f.write(log_line + "\n")

    def check_prerequisites(self) -> bool:
        """Check if aider and LM Studio are available."""
        # Check LM Studio
        try:
            import requests
            resp = requests.get("http://localhost:1234/v1/models", timeout=2)
            if resp.status_code != 200:
                self.log("ERROR: LM Studio not responding")
                return False
            self.log("LM Studio: OK")
        except Exception as e:
            self.log(f"ERROR: LM Studio check failed: {e}")
            return False

        # Check aider
        result = subprocess.run(['which', 'aider'], capture_output=True)
        if result.returncode != 0:
            self.log("ERROR: aider not found")
            return False
        self.log("aider: OK")

        return True

    def scan_for_issues(self, files: list = None) -> list:
        """Scan codebase for common issues."""
        issues = []

        if files:
            file_patterns = files
        else:
            # Default: scan key Botwave files
            file_patterns = [
                "scrypt_keeper_*.py",
                "lib/*.py",
                "bin/*.py",
                "dashboard/*.py"
            ]

        self.log(f"Scanning files: {file_patterns}")

        for pattern in file_patterns:
            if '*' in pattern:
                # Glob pattern
                for f in self.base_dir.glob(pattern):
                    issues.extend(self._scan_file(f))
            else:
                # Direct file
                f = self.base_dir / pattern
                if f.exists():
                    issues.extend(self._scan_file(f))

        return issues

    def _scan_file(self, file_path: Path) -> list:
        """Scan a single file for issues."""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # Check for TODOs
                if 'TODO' in line or 'FIXME' in line:
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'TODO',
                        'content': line.strip()
                    })

                # Check for incomplete code
                if 'pass  # placeholder' in line.lower() or '...' in line:
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'INCOMPLETE',
                        'content': line.strip()
                    })

                # Check for stub implementations
                if 'stub' in line.lower() and 'implementation' in line.lower():
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'STUB',
                        'content': line.strip()
                    })

        except Exception as e:
            self.log(f"Error scanning {file_path}: {e}")

        return issues

    def run_audit(self, files: list = None, auto_fix: bool = False) -> dict:
        """
        Run full audit cycle.

        Args:
            files: List of files/patterns to audit
            auto_fix: If True, run aider with --yes to auto-apply fixes

        Returns:
            Audit results
        """
        self.log("="*60)
        self.log("Starting Self-Audit")
        self.log("="*60)

        # Check prerequisites
        if not self.check_prerequisites():
            return {"error": "Prerequisites check failed"}

        # Scan for issues
        issues = self.scan_for_issues(files)
        self.log(f"Found {len(issues)} potential issues")

        if not issues:
            self.log("No issues found - codebase looks clean!")
            return {"status": "clean", "issues": []}

        # Print issues
        self.log("\nIssues found:")
        for issue in issues[:20]:  # Show first 20
            self.log(f"  [{issue['type']}] {issue['file']}:{issue['line']}")
            self.log(f"    {issue['content']}")

        if auto_fix:
            self.log("\nLaunching aider to fix issues...")
            return self._run_aider_fix(issues)
        else:
            self.log("\nRun with --fix flag to auto-apply fixes")
            return {"status": "issues_found", "issues": issues}

    def _run_aider_fix(self, issues: list) -> dict:
        """Launch aider to fix issues."""
        # Create audit instruction file
        audit_file = self.base_dir / "agent-jobs" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(audit_file, 'w') as f:
            f.write("# Self-Audit Fix Session\n\n")
            f.write("## Issues to Fix\n\n")
            for issue in issues:
                f.write(f"- [{issue['type']}] {issue['file']}:{issue['line']}: {issue['content']}\n")
            f.write("\n## Instructions\n\n")
            f.write("Review and fix the issues above. For each:\n")
            f.write("1. Understand the context\n")
            f.write("2. Implement proper solution\n")
            f.write("3. Test if possible\n")
            f.write("4. Commit with descriptive message\n")

        # Build aider command
        files_to_add = list(set(i['file'] for i in issues))
        cmd = f"cd {self.base_dir} && aid --yes {audit_file} {' '.join(files_to_add)}"

        self.log(f"Running: {cmd}")

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3600
        )

        # Log results
        with open(self.audit_log, 'a') as f:
            f.write("\n" + "="*60 + "\n")
            f.write("AIDER OUTPUT:\n")
            f.write(result.stdout + "\n")
            if result.stderr:
                f.write("STDERR:\n" + result.stderr + "\n")
            f.write(f"Return code: {result.returncode}\n")

        if result.returncode == 0:
            self.log("Audit fix completed successfully")
            return {"status": "fixed", "issues_fixed": len(issues)}
        else:
            self.log("Audit fix failed")
            return {"status": "failed", "error": result.stderr[:500]}


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Botwave Self-Audit')
    parser.add_argument('--files', nargs='*', help='Files to audit')
    parser.add_argument('--all', action='store_true', help='Audit all Botwave files')
    parser.add_argument('--fix', action='store_true', help='Auto-fix with aider')
    parser.add_argument('--list-issues', action='store_true', help='Just list issues, no fix')

    args = parser.parse_args()

    audit = SelfAudit()

    if args.all:
        files = None  # Use default patterns
    elif args.files:
        files = args.files
    else:
        files = None

    if args.list_issues:
        issues = audit.scan_for_issues(files)
        print(f"\nFound {len(issues)} issues:\n")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['file']}:{issue['line']}")
            print(f"    {issue['content']}\n")
    else:
        result = audit.run_audit(files, auto_fix=args.fix)
        print(f"\nAudit result: {result}")


if __name__ == "__main__":
    main()
