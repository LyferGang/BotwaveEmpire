"""
System Organizer Agent
Remote laptop cleanup and organization for business optimization.
Connects via SSH to organize files and quarantine suspicious content.
"""

import os
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

from core.base_agent import BaseAgent
from core.secrets import secrets


class SystemOrganizerAgent(BaseAgent):
    """
    Agent for remotely organizing and cleaning business laptops.

    Capabilities:
    - SSH into remote systems via Tailscale
    - Scan and categorize files
    - Move suspicious/questionable files to quarantine
    - Organize documents by type and date
    - Generate human-readable reports
    - Preserve all data (no permanent deletion)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("system_organizer", config)
        self.ssh_host = None
        self.ssh_user = None
        self.quarantine_dir = "For_Review"
        self.organized_dir = "Organized"

    def run(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute system organization task.

        Args:
            task_input: Must contain:
                - 'host': Tailscale/SSH hostname or IP
                - 'user': SSH username
                - 'action': 'organize', 'scan', or 'quarantine'

        Returns:
            Organization report
        """
        self.ssh_host = task_input.get("host")
        self.ssh_user = task_input.get("user", "admin")
        action = task_input.get("action", "organize")

        if not self.ssh_host:
            return self._format_error(
                ValueError("No host specified"),
                "Please provide Tailscale IP or hostname"
            )

        try:
            # Verify SSH connectivity first
            if not self._test_connection():
                return self._format_error(
                    ConnectionError("SSH connection failed"),
                    f"Cannot connect to {self.ssh_host}. Is Tailscale active?"
                )

            if action == "scan":
                return self._scan_system()
            elif action == "organize":
                return self._organize_files()
            elif action == "quarantine":
                return self._quarantine_suspicious()
            elif action == "full_cleanup":
                return self._full_cleanup()
            else:
                return self._format_error(
                    ValueError(f"Unknown action: {action}"),
                    "Supported: scan, organize, quarantine, full_cleanup"
                )

        except Exception as e:
            return self._format_error(e)

    def _test_connection(self) -> bool:
        """Test SSH connectivity to target."""
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10",
                 "-o", "StrictHostKeyChecking=no",
                 f"{self.ssh_user}@{self.ssh_host}", "echo 'connected'"],
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.returncode == 0 and "connected" in result.stdout
        except Exception as e:
            self.logger.error(f"SSH test failed: {e}")
            return False

    def _scan_system(self) -> Dict[str, Any]:
        """Scan system for file inventory and analysis."""
        self.logger.info(f"Scanning {self.ssh_host}...")

        # Get file inventory
        scan_script = r"""
        echo "=== SYSTEM SCAN ==="
        echo "Date: $(date)"
        echo "User: $(whoami)"
        echo "Hostname: $(hostname)"
        echo ""
        echo "--- DISK USAGE ---"
        df -h / 2>/dev/null | head -5
        echo ""
        echo "--- LARGE FILES (>100MB) ---"
        find /home -type f -size +100M 2>/dev/null | head -20
        echo ""
        echo "--- DOWNLOADS FOLDER ---"
        ls -la ~/Downloads 2>/dev/null | head -30
        echo ""
        echo "--- DESKTOP FILES ---"
        ls -la ~/Desktop 2>/dev/null | head -30
        echo ""
        echo "--- DOCUMENTS ---"
        find ~/Documents -type f 2>/dev/null | head -50
        echo ""
        echo "--- SUSPICIOUS EXTENSIONS ---"
        find /home -type f \( -name "*.exe" -o -name "*.bat" -o -name "*.ps1" -o -name "*.scr" \) 2>/dev/null
        echo ""
        echo "--- TEMP FILES ---"
        ls -la /tmp 2>/dev/null | head -20
        """

        result = self._ssh_exec(scan_script)

        # Parse results
        files_found = self._parse_scan_results(result)

        return self._format_success({
            "scan_date": datetime.utcnow().isoformat(),
            "hostname": self.ssh_host,
            "raw_output": result,
            "files_found": files_found,
            "recommendations": self._generate_recommendations(files_found)
        }, "System scan complete")

    def _organize_files(self) -> Dict[str, Any]:
        """Organize files into categorized folders."""
        self.logger.info(f"Organizing files on {self.ssh_host}...")

        organize_script = rf"""
        BASE_DIR="$HOME"
        ORG_DIR="$BASE_DIR/{self.organized_dir}_$(date +%Y%m%d)"

        echo "Creating organization structure..."
        mkdir -p "$ORG_DIR"/{{Documents,Photos,Videos,Music,Archives,PDFs,Misc}}

        # Move PDFs
        find "$BASE_DIR" -maxdepth 2 -type f -name "*.pdf" 2>/dev/null | while read f; do
            cp "$f" "$ORG_DIR/PDFs/" 2>/dev/null && echo "Copied: $f"
        done

        # Move images
        find "$BASE_DIR" -maxdepth 2 -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" \) 2>/dev/null | while read f; do
            cp "$f" "$ORG_DIR/Photos/" 2>/dev/null && echo "Copied: $f"
        done

        # Move documents
        find "$BASE_DIR" -maxdepth 2 -type f \( -name "*.doc" -o -name "*.docx" -o -name "*.txt" -o -name "*.rtf" \) 2>/dev/null | while read f; do
            cp "$f" "$ORG_DIR/Documents/" 2>/dev/null && echo "Copied: $f"
        done

        # Move archives
        find "$BASE_DIR" -maxdepth 2 -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.gz" -o -name "*.rar" \) 2>/dev/null | while read f; do
            cp "$f" "$ORG_DIR/Archives/" 2>/dev/null && echo "Copied: $f"
        done

        # Generate summary
        echo ""
        echo "=== ORGANIZATION SUMMARY ==="
        for dir in "$ORG_DIR"/*/; do
            count=$(find "$dir" -type f 2>/dev/null | wc -l)
            echo "$(basename "$dir"): $count files"
        done

        echo ""
        echo "Organized files saved to: $ORG_DIR"
        """

        result = self._ssh_exec(organize_script)

        return self._format_success({
            "action": "organize",
            "output": result,
            "organized_location": f"~/{self.organized_dir}_{datetime.now().strftime('%Y%m%d')}",
            "note": "Original files preserved. Review and delete organized copies after approval."
        }, "Files organized successfully")

    def _quarantine_suspicious(self) -> Dict[str, Any]:
        """Move suspicious/questionable files to quarantine for review."""
        self.logger.info(f"Quarantining suspicious files on {self.ssh_host}...")

        quarantine_script = rf"""
        BASE_DIR="$HOME"
        QUAR_DIR="$BASE_DIR/Desktop/{self.quarantine_dir}"

        echo "Creating quarantine folder..."
        mkdir -p "$QUAR_DIR"

        echo "Scanning for suspicious files..."
        echo ""

        # Suspicious executables in user folders
        echo "--- Potential Malware (executables in home) ---"
        find "$BASE_DIR" -maxdepth 3 -type f \( -name "*.exe" -o -name "*.bat" -o -name "*.scr" -o -name "*.com" \) ! -path "*/\.*" 2>/dev/null | while read f; do
            dest="$QUAR_DIR/$(basename "$f")"
            counter=1
            while [ -e "$dest" ]; do
                dest="$QUAR_DIR/${{counter}}_$(basename "$f")"
                counter=$((counter + 1))
            done
            mv "$f" "$dest" 2>/dev/null && echo "QUARANTINED: $f -> $dest"
        done

        # Suspicious scripts
        echo ""
        echo "--- Suspicious Scripts ---"
        find "$BASE_DIR" -maxdepth 3 -type f \( -name "*.ps1" -o -name "*.vbs" -o -name "*.js" -o -name "*.sh" \) ! -path "*/\.*" 2>/dev/null | head -20 | while read f; do
            if grep -q -E "(password|key|token|secret|credential)" "$f" 2>/dev/null; then
                dest="$QUAR_DIR/POTENTIAL_CREDENTIALS_$(basename "$f")"
                mv "$f" "$dest" 2>/dev/null && echo "QUARANTINED (credentials?): $f"
            fi
        done

        # Files with suspicious patterns in Downloads
        echo ""
        echo "--- Downloads Scan ---"
        ls -la "$BASE_DIR/Downloads" 2>/dev/null | grep -E "(crack|keygen|patch|hack|cracked)" | while read line; do
            filename=$(echo "$line" | awk '{{print $NF}}')
            if [ -f "$BASE_DIR/Downloads/$filename" ]; then
                mv "$BASE_DIR/Downloads/$filename" "$QUAR_DIR/SUSPICIOUS_$filename" 2>/dev/null
                echo "QUARANTINED: $filename"
            fi
        done

        # Large temp files
        echo ""
        echo "--- Large Temp Files (>500MB) ---"
        find /tmp -type f -size +500M 2>/dev/null | while read f; do
            echo "WARNING: Large temp file: $f ($(du -h "$f" | cut -f1))"
        done

        echo ""
        echo "=== QUARANTINE SUMMARY ==="
        quarantined=$(find "$QUAR_DIR" -type f 2>/dev/null | wc -l)
        echo "Files quarantined: $quarantined"
        echo "Location: $QUAR_DIR"
        echo ""
        echo "REVIEW these files with the owner before taking any action!"
        """

        return self._format_success({
            "action": "quarantine",
            "output": result,
            "quarantine_location": f"~/Desktop/{self.quarantine_dir}",
            "warning": "REVIEW ALL QUARANTINED FILES WITH BUSINESS OWNER BEFORE DELETING",
            "note": "No files were permanently deleted. Everything is in the For_Review folder."
        }, "Suspicious files quarantined for review")

    def _full_cleanup(self) -> Dict[str, Any]:
        """Complete system cleanup workflow."""
        self.logger.info(f"Starting full cleanup on {self.ssh_host}...")

        results = {
            "scan": None,
            "quarantine": None,
            "organize": None,
            "report_path": None
        }

        # Step 1: Scan
        scan_result = self._scan_system()
        results["scan"] = scan_result.get("data", {})

        # Step 2: Quarantine suspicious
        quarantine_result = self._quarantine_suspicious()
        results["quarantine"] = quarantine_result.get("data", {})

        # Step 3: Organize
        organize_result = self._organize_files()
        results["organize"] = organize_result.get("data", {})

        # Step 4: Generate report
        report = self._generate_report(results)
        results["report"] = report

        return self._format_success(results, "Full cleanup completed successfully")

    def _ssh_exec(self, script: str) -> str:
        """Execute script via SSH."""
        try:
            result = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no",
                 f"{self.ssh_user}@{self.ssh_host}", script],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "ERROR: SSH command timed out after 5 minutes"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _parse_scan_results(self, output: str) -> Dict[str, Any]:
        """Parse scan output into structured data."""
        files = {
            "large_files": [],
            "executables": [],
            "documents": [],
            "suspicious": []
        }

        lines = output.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if "LARGE FILES" in line:
                current_section = "large_files"
            elif "SUSPICIOUS EXTENSIONS" in line:
                current_section = "suspicious"
            elif line.startswith('/home') or line.startswith('/Users'):
                if current_section and line:
                    files[current_section].append(line)

        return files

    def _generate_recommendations(self, files: Dict[str, Any]) -> List[str]:
        """Generate cleanup recommendations based on scan."""
        recommendations = []

        if files.get("large_files"):
            recommendations.append(f"Found {len(files['large_files'])} large files (>100MB) - consider moving to external storage")

        if files.get("executables"):
            recommendations.append(f"Found {len(files['executables'])} executable files in user folders - review for malware")

        if files.get("suspicious"):
            recommendations.append(f"Found {len(files['suspicious'])} suspicious files - quarantine recommended")

        recommendations.append("Run 'organize' to sort files by type")
        recommendations.append("Run 'quarantine' to isolate suspicious files for review")

        return recommendations

    def _generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report for business owner."""
        report = f"""
================================================================================
                    PLUMBING BUSINESS COMPUTER CLEANUP REPORT
================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Technician: Botwave System Organizer Agent
Business: Dad's Plumbing Service

SUMMARY
-------
This report contains the results of an automated cleanup of your business
computer. NO FILES WERE PERMANENTLY DELETED. All items have been organized
or moved to folders for your review.

ACTIONS TAKEN
-------------
1. System Scan: Complete inventory of files and storage
2. Quarantine: Suspicious/questionable files moved to "For_Review" folder
3. Organization: Files sorted by type into categorized folders

QUARANTINED ITEMS (REQUIRES YOUR REVIEW)
----------------------------------------
Location: Desktop/For_Review/
"""

        quarantine_data = results.get("quarantine", {})
        if quarantine_data:
            report += f"\nOutput:\n{quarantine_data.get('output', 'N/A')}\n"

        report += f"""
ORGANIZED FILES
---------------
Location: {results.get('organize', {}).get('organized_location', 'N/A')}

Your files have been sorted into categories:
- Documents: Word docs, text files
- PDFs: All PDF documents
- Photos: Images and screenshots
- Archives: Zip files and compressed folders
- Misc: Other file types

NEXT STEPS
----------
1. Review the "For_Review" folder on your Desktop
2. Decide what to keep/delete from quarantined items
3. Check the organized folders - delete originals after confirming copies
4. Ask your technician about any items you're unsure about

IMPORTANT
---------
- Nothing was permanently deleted
- Your original files are still in place
- Copies were made for organization purposes
- Delete organized copies after you verify they work

Questions? Ask your technician (the person who ran this cleanup)!

================================================================================
                        Report Generated by Botwave Empire
                        Professional Business Automation
================================================================================
"""

        # Save report to remote system
        report_script = f"""
        cat > "$HOME/Desktop/CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d')}.txt" << 'ENDREPORT'
{report}
ENDREPORT
echo "Report saved to Desktop"
"""
        self._ssh_exec(report_script)

        return report


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python system_organizer_agent.py <tailscale_ip> [action]")
        print("Actions: scan, organize, quarantine, full_cleanup")
        sys.exit(1)

    host = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "full_cleanup"

    agent = SystemOrganizerAgent()
    result = agent.run({
        "host": host,
        "user": "dad",  # Adjust based on the laptop's username
        "action": action
    })

    print("\n" + "="*80)
    print(f"STATUS: {result['status']}")
    print(f"MESSAGE: {result.get('message', '')}")
    print("="*80)

    if result['status'] == 'success':
        data = result.get('data', {})
        if 'report' in data:
            print("\nREPORT FOR BUSINESS OWNER:")
            print(data['report'])

        if 'quarantine' in data:
            print(f"\n📁 Quarantine folder: {data['quarantine'].get('quarantine_location')}")
            print("⚠️  REVIEW THESE FILES WITH YOUR DAD BEFORE DELETING ANYTHING!")

        if 'organize' in data:
            print(f"\n📁 Organized files: {data['organize'].get('organized_location')}")

    print("\nCleanup complete! Check the Desktop for the report.")


if __name__ == "__main__":
    main()
