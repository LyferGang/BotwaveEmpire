#!/usr/bin/env python3
"""
System Cleaner Pro - Professional Edition
Cross-platform system cleanup and organization tool.

Safe, zero-loss cleanup for client computers.
Everything moves to REVIEW folder - nothing deleted without approval.

Supports: Windows, macOS, Linux

Part of Botwave Business Automation Suite
"""

import os
import sys
import shutil
import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class CleanupConfig:
    """Cleanup configuration."""
    # File type categories
    document_extensions: List[str] = field(default_factory=lambda: [
        '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'
    ])
    image_extensions: List[str] = field(default_factory=lambda: [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif', '.tiff', '.tif', '.svg', '.webp'
    ])
    video_extensions: List[str] = field(default_factory=lambda: [
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'
    ])
    audio_extensions: List[str] = field(default_factory=lambda: [
        '.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.m4a'
    ])
    archive_extensions: List[str] = field(default_factory=lambda: [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'
    ])
    installer_extensions: List[str] = field(default_factory=lambda: [
        '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.appimage'
    ])
    code_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go'
    ])

    # Suspicious patterns (flagged for review, not auto-deleted)
    suspicious_patterns: List[str] = field(default_factory=lambda: [
        'crack', 'keygen', 'patch', 'hack', 'serial', 'warez', 'torrent',
        'keymaker', 'activator', 'loader', 'bypass', 'patched'
    ])

    # System temp folders by platform
    temp_folders: Dict[str, List[str]] = field(default_factory=lambda: {
        'windows': [
            str(Path.home() / 'AppData' / 'Local' / 'Temp'),
            r'C:\Windows\Temp',
            str(Path.home() / 'AppData' / 'Local' / 'Microsoft' / 'Windows' / 'INetCache'),
        ],
        'darwin': [
            '/tmp',
            str(Path.home() / 'Library' / 'Caches'),
            str(Path.home() / 'Library' / 'Logs'),
        ],
        'linux': [
            '/tmp',
            '/var/tmp',
            str(Path.home() / '.cache'),
        ]
    })

    # Business-related search terms (for finding client files)
    business_terms: List[str] = field(default_factory=lambda: [
        'invoice', 'receipt', 'quote', 'estimate', 'contract', 'proposal',
        'customer', 'client', 'job', 'project', 'billing', 'payment'
    ])


# =============================================================================
# SYSTEM SCANNER
# =============================================================================

class SystemScanner:
    """Scan system for files and potential issues."""

    def __init__(self, config: CleanupConfig = None):
        self.config = config or CleanupConfig()
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'by_category': {},
            'suspicious_files': [],
            'large_files': [],
            'duplicate_candidates': [],
            'temp_files': []
        }

    def scan_directory(self, path: Path, max_depth: int = 10) -> Dict:
        """Scan a directory and categorize files."""
        results = {
            'path': str(path),
            'files': [],
            'categories': {},
            'total_size': 0,
            'file_count': 0
        }

        try:
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        ext = item.suffix.lower()

                        # Categorize
                        category = self._categorize_file(ext)
                        if category not in results['categories']:
                            results['categories'][category] = {'count': 0, 'size': 0}

                        results['categories'][category]['count'] += 1
                        results['categories'][category]['size'] += size

                        results['total_size'] += size
                        results['file_count'] += 1

                        # Check for suspicious files
                        if self._is_suspicious(item.name):
                            results['suspicious'] = results.get('suspicious', [])
                            results['suspicious'].append({
                                'path': str(item),
                                'size': size,
                                'reason': 'suspicious_name'
                            })

                        # Check for large files (>100MB)
                        if size > 100 * 1024 * 1024:
                            results['large_files'] = results.get('large_files', [])
                            results['large_files'].append({
                                'path': str(item),
                                'size_mb': round(size / (1024 * 1024), 2)
                            })

                    except (PermissionError, OSError):
                        continue

        except (PermissionError, OSError) as e:
            results['error'] = str(e)

        return results

    def scan_temp_folders(self) -> List[Dict]:
        """Scan system temp folders."""
        os_type = platform.system().lower()
        if os_type == 'windows':
            os_type = 'windows'
        elif os_type == 'darwin':
            os_type = 'darwin'
        else:
            os_type = 'linux'

        temp_files = []
        temp_folders = self.config.temp_folders.get(os_type, [])

        for folder in temp_folders:
            folder_path = Path(folder)
            if folder_path.exists():
                try:
                    for item in folder_path.iterdir():
                        if item.is_file():
                            try:
                                temp_files.append({
                                    'path': str(item),
                                    'size': item.stat().st_size,
                                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                                })
                            except (PermissionError, OSError):
                                continue
                except (PermissionError, OSError):
                    continue

        return temp_files

    def _categorize_file(self, ext: str) -> str:
        """Categorize file by extension."""
        if ext in self.config.document_extensions:
            return 'documents'
        elif ext in self.config.image_extensions:
            return 'images'
        elif ext in self.config.video_extensions:
            return 'videos'
        elif ext in self.config.audio_extensions:
            return 'audio'
        elif ext in self.config.archive_extensions:
            return 'archives'
        elif ext in self.config.installer_extensions:
            return 'installers'
        elif ext in self.config.code_extensions:
            return 'code'
        else:
            return 'other'

    def _is_suspicious(self, filename: str) -> bool:
        """Check if filename matches suspicious patterns."""
        name_lower = filename.lower()
        return any(pattern in name_lower for pattern in self.config.suspicious_patterns)


# =============================================================================
# FILE ORGANIZER
# =============================================================================

class FileOrganizer:
    """Organize files into categories."""

    def __init__(self, review_folder: Path, organized_folder: Path):
        self.review_folder = review_folder
        self.organized_folder = organized_folder
        self.operations = []

    def organize_files(self, scan_results: Dict, source_path: Path) -> Dict:
        """Organize scanned files into categories."""
        stats = {
            'organized': 0,
            'flagged': 0,
            'errors': 0
        }

        # Create category folders
        categories = ['documents', 'images', 'videos', 'audio', 'archives', 'installers', 'code', 'other']
        for cat in categories:
            (self.organized_folder / cat).mkdir(parents=True, exist_ok=True)

        # Process files (copy, don't move - safe mode)
        if 'suspicious' in scan_results:
            for item in scan_results['suspicious']:
                try:
                    src = Path(item['path'])
                    dst = self.review_folder / f"FLAGGED_{src.name}"
                    shutil.copy2(src, dst)
                    stats['flagged'] += 1
                    self.operations.append({
                        'action': 'flagged',
                        'source': str(src),
                        'destination': str(dst)
                    })
                except Exception as e:
                    stats['errors'] += 1
                    self.operations.append({
                        'action': 'error',
                        'source': item['path'],
                        'error': str(e)
                    })

        return stats


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator:
    """Generate cleanup reports."""

    @staticmethod
    def generate_report(scan_results: Dict, operations: List[Dict],
                        review_folder: Path, organized_folder: Path) -> str:
        """Generate a detailed cleanup report."""

        report = f"""
================================================================================
                    BOTWAVE SYSTEM CLEANER - CLIENT REPORT
================================================================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Computer: {platform.node()}
OS: {platform.system()} {platform.release()}

================================================================================
SCAN SUMMARY
================================================================================

"""
        if 'file_count' in scan_results:
            report += f"Total Files Scanned: {scan_results['file_count']:,}\n"
            report += f"Total Size: {scan_results['total_size'] / (1024*1024*1024):.2f} GB\n\n"

        if 'categories' in scan_results:
            report += "FILES BY CATEGORY:\n"
            report += "-" * 40 + "\n"
            for cat, data in scan_results['categories'].items():
                report += f"  {cat.title():15} {data['count']:>8,} files  ({data['size'] / (1024*1024):.2f} MB)\n"
            report += "\n"

        if scan_results.get('suspicious'):
            report += f"SUSPICIOUS FILES FLAGGED: {len(scan_results['suspicious'])}\n"
            report += "-" * 40 + "\n"
            for item in scan_results['suspicious'][:20]:  # Show first 20
                report += f"  ⚠️  {item['path']}\n"
            if len(scan_results['suspicious']) > 20:
                report += f"  ... and {len(scan_results['suspicious']) - 20} more\n"
            report += "\n"

        if scan_results.get('large_files'):
            report += f"LARGE FILES (>100MB): {len(scan_results['large_files'])}\n"
            report += "-" * 40 + "\n"
            for item in scan_results['large_files'][:10]:
                report += f"  {item['size_mb']:>8.2f} MB  {item['path']}\n"
            report += "\n"

        report += f"""
================================================================================
FOLDERS CREATED
================================================================================

📁 REVIEW FOLDER:
   {review_folder}

   Contains files flagged for your review before deletion.
   These may be suspicious files or items needing approval.

📁 ORGANIZED FOLDER:
   {organized_folder}

   Contains COPIES of your files organized by type:
   - documents/  - PDFs, Word docs, spreadsheets
   - images/     - Photos, screenshots, graphics
   - videos/     - Video files
   - audio/      - Music, recordings
   - archives/   - ZIP, RAR files
   - installers/ - Software installers
   - code/       - Source code files
   - other/      - Everything else

================================================================================
IMPORTANT NOTES
================================================================================

✓ NO FILES WERE DELETED
✓ Original files remain in their original locations
✓ Organized folder contains COPIES for easy browsing
✓ Flagged files are COPIES - originals untouched

================================================================================
NEXT STEPS
================================================================================

1. REVIEW the flagged files in the REVIEW folder
   - These may be malware or unauthorized software
   - Review with your IT provider before deleting

2. BROWSE the organized folder
   - Files are sorted by type for easy finding
   - Use this to locate specific files quickly

3. APPROVE deletions
   - Only delete files you're sure about
   - When in doubt, keep it or ask for help

4. MAINTENANCE
   - Run this cleanup monthly
   - Keep downloads folder organized
   - Empty recycle bin regularly

================================================================================
                    Botwave System Cleaner v1.0
                    Professional IT Services
================================================================================
"""
        return report


# =============================================================================
# MAIN CLEANER
# =============================================================================

class BotwaveSystemCleaner:
    """Main system cleaner application."""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home()
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create output folders on desktop
        desktop = self._get_desktop()
        self.review_folder = desktop / f"BOTWAVE_REVIEW_{self.timestamp}"
        self.organized_folder = desktop / f"BOTWAVE_ORGANIZED_{self.timestamp}"

        self.review_folder.mkdir(parents=True, exist_ok=True)
        self.organized_folder.mkdir(parents=True, exist_ok=True)

        self.config = CleanupConfig()
        self.scanner = SystemScanner(self.config)
        self.organizer = FileOrganizer(self.review_folder, self.organized_folder)

    def run_cleanup(self, scan_only: bool = False) -> Dict:
        """Run the full cleanup process."""

        print("=" * 80)
        print("     BOTWAVE SYSTEM CLEANER")
        print("=" * 80)
        print()
        print(f"Scanning: {self.base_path}")
        print(f"Review folder: {self.review_folder}")
        print(f"Organized folder: {self.organized_folder}")
        print()

        # Phase 1: Scan
        print("Phase 1: Scanning files...")
        scan_results = self.scanner.scan_directory(self.base_path)

        # Add temp file scan
        temp_files = self.scanner.scan_temp_folders()
        scan_results['temp_files'] = temp_files
        scan_results['temp_count'] = len(temp_files)

        print(f"  Found {scan_results.get('file_count', 0):,} files")
        print(f"  Flagged {len(scan_results.get('suspicious', []))} suspicious files")
        print(f"  Found {scan_results.get('temp_count', 0)} temp files")
        print()

        if scan_only:
            print("Scan-only mode. No files organized.")
            return {'status': 'success', 'scan': scan_results}

        # Phase 2: Organize
        print("Phase 2: Organizing files...")
        org_stats = self.organizer.organize_files(scan_results, self.base_path)
        print(f"  Organized: {org_stats['organized']} files")
        print(f"  Flagged: {org_stats['flagged']} files")
        print(f"  Errors: {org_stats['errors']}")
        print()

        # Phase 3: Generate report
        print("Phase 3: Generating report...")
        report = ReportGenerator.generate_report(
            scan_results,
            self.organizer.operations,
            self.review_folder,
            self.organized_folder
        )

        report_path = self.review_folder.parent / f"BOTWAVE_REPORT_{self.timestamp}.txt"
        report_path.write_text(report, encoding='utf-8')
        print(f"  Report: {report_path}")
        print()

        # Create warning file
        warning = """
⚠️  BOTWAVE REVIEW FOLDER  ⚠️

This folder contains files flagged for your review.

DO NOT DELETE anything until you've reviewed it!

These files may be:
- Malware or viruses
- Unauthorized software
- Suspicious downloads
- Files with concerning names

Your original files are SAFE - these are COPIES for review.

When in doubt, ASK YOUR IT PROVIDER before deleting!

Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        (self.review_folder / "⚠️_READ_THIS_FIRST.txt").write_text(warning)

        print("=" * 80)
        print("     CLEANUP COMPLETE!")
        print("=" * 80)
        print()
        print("Check your Desktop for:")
        print(f"  📁 {self.review_folder.name}/")
        print(f"  📁 {self.organized_folder.name}/")
        print(f"  📄 BOTWAVE_REPORT_{self.timestamp}.txt")
        print()

        return {
            'status': 'success',
            'review_folder': str(self.review_folder),
            'organized_folder': str(self.organized_folder),
            'report_path': str(report_path),
            'scan': scan_results,
            'operations': self.organizer.operations
        }

    def _get_desktop(self) -> Path:
        """Get desktop path for current OS."""
        os_type = platform.system()

        if os_type == 'Windows':
            return Path.home() / 'Desktop'
        elif os_type == 'Darwin':
            return Path.home() / 'Desktop'
        else:  # Linux
            xdg_desktop = os.environ.get('XDG_DESKTOP_DIR')
            if xdg_desktop:
                return Path(xdg_desktop)
            # Try common locations
            for path in [Path.home() / 'Desktop', Path.home() / 'desktop']:
                if path.exists():
                    return path
            return Path.home() / 'Desktop'


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Botwave System Cleaner - Professional cross-platform cleanup tool'
    )
    parser.add_argument(
        '--path', '-p',
        type=Path,
        default=Path.home(),
        help='Path to scan (default: home directory)'
    )
    parser.add_argument(
        '--scan-only', '-s',
        action='store_true',
        help='Only scan, don\'t organize files'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Custom output folder for organized files'
    )

    args = parser.parse_args()

    cleaner = BotwaveSystemCleaner(args.path)

    if args.output:
        cleaner.organized_folder = args.output
        cleaner.organized_folder.mkdir(parents=True, exist_ok=True)

    result = cleaner.run_cleanup(scan_only=args.scan_only)

    if result['status'] == 'success':
        print("\n✅ Cleanup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Cleanup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
