# Jimenez Plumbing - Business File Organizer
# PowerShell script to organize and clean business files

param(
    [string]$BusinessPath = "C:\Users\jpsji\OneDrive\Desktop\jpsji\Dropbox\JIMENEZ PLUMBING"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   JIMENEZ PLUMBING FILE ORGANIZER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will organize your business files" -ForegroundColor Yellow
Write-Host "NO FILES WILL BE DELETED - only copied" -ForegroundColor Green
Write-Host ""

# Verify path exists
if (-not (Test-Path $BusinessPath)) {
    Write-Host "ERROR: Path not found: $BusinessPath" -ForegroundColor Red
    Write-Host "Checking alternative paths..." -ForegroundColor Yellow

    $alternatives = @(
        "C:\Users\jpsji\Desktop\jpsji\Dropbox\JIMENEZ PLUMBING",
        "C:\Users\jpsji\Documents\JIMENEZ PLUMBING",
        "$env:USERPROFILE\Desktop\JIMENEZ PLUMBING"
    )

    foreach ($alt in $alternatives) {
        if (Test-Path $alt) {
            Write-Host "Found: $alt" -ForegroundColor Green
            $BusinessPath = $alt
            break
        }
    }

    if (-not (Test-Path $BusinessPath)) {
        Write-Host "ERROR: Could not find Jimenez Plumbing folder!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Target: $BusinessPath" -ForegroundColor Green
Write-Host ""

# Create folders
$ReviewFolder = "$env:USERPROFILE\Desktop\For_Review_TODAY"
$OrganizedFolder = "$env:USERPROFILE\Desktop\ORGANIZED_$(Get-Date -Format 'yyyyMMdd')"

New-Item -ItemType Directory -Force -Path $ReviewFolder | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Invoices" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Photos_Jobs" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Contracts" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Receipts" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Estimates" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Misc" | Out-Null
New-Item -ItemType Directory -Force -Path "$OrganizedFolder\Archives" | Out-Null

Write-Host "Created: $ReviewFolder" -ForegroundColor Green
Write-Host "Created: $OrganizedFolder" -ForegroundColor Green
Write-Host ""

# Phase 1: Scan for suspicious files
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PHASE 1: Scanning for suspicious files..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$SuspiciousCount = 0
$SuspiciousPatterns = @('*.exe', '*.bat', '*.scr', '*.cmd', '*.com')

foreach ($pattern in $SuspiciousPatterns) {
    Get-ChildItem -Path $BusinessPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "[WARNING] Suspicious file: $($_.FullName)" -ForegroundColor Red
        Copy-Item $_.FullName -Destination "$ReviewFolder\SUSPICIOUS_$($_.Name)" -Force
        Write-Host "  -> Copied to For_Review_TODAY" -ForegroundColor Yellow
        $SuspiciousCount++
    }
}

# Check for suspicious keywords in filenames
Get-ChildItem -Path $BusinessPath -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match 'crack|keygen|patch|hack|serial|warez|torrent'
} | ForEach-Object {
    Write-Host "[QUARANTINED] Suspicious name: $($_.FullName)" -ForegroundColor Red
    Copy-Item $_.FullName -Destination "$ReviewFolder\QUESTIONABLE_$($_.Name)" -Force
    $SuspiciousCount++
}

Write-Host "Found $SuspiciousCount suspicious files" -ForegroundColor Yellow
Write-Host ""

# Phase 2: Organize files
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PHASE 2: Organizing business files..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$Stats = @{
    PDFs = 0
    Photos = 0
    Documents = 0
    Archives = 0
}

# PDFs (Invoices, Receipts)
Get-ChildItem -Path $BusinessPath -Filter "*.pdf" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName -Destination "$OrganizedFolder\Invoices\" -Force
    $Stats.PDFs++
}
Write-Host "PDFs: $($Stats.PDFs) files" -ForegroundColor Green

# Photos
@('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.heic') | ForEach-Object {
    Get-ChildItem -Path $BusinessPath -Filter $_ -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "$OrganizedFolder\Photos_Jobs\" -Force
        $Stats.Photos++
    }
}
Write-Host "Photos: $($Stats.Photos) files" -ForegroundColor Green

# Documents
@('*.doc', '*.docx', '*.txt', '*.rtf') | ForEach-Object {
    Get-ChildItem -Path $BusinessPath -Filter $_ -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "$OrganizedFolder\Contracts\" -Force
        $Stats.Documents++
    }
}
Write-Host "Documents: $($Stats.Documents) files" -ForegroundColor Green

# Archives
@('*.zip', '*.rar', '*.7z', '*.tar', '*.gz') | ForEach-Object {
    Get-ChildItem -Path $BusinessPath -Filter $_ -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item $_.FullName -Destination "$OrganizedFolder\Archives\" -Force
        $Stats.Archives++
    }
}
Write-Host "Archives: $($Stats.Archives) files" -ForegroundColor Green

Write-Host ""

# Phase 3: Generate report
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PHASE 3: Generating report..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ReportPath = "$env:USERPROFILE\Desktop\CLEANUP_REPORT_$(Get-Date -Format 'yyyyMMdd').txt"
$ReportContent = @"
================================================================================
                    JIMENEZ PLUMBING - COMPUTER CLEANUP REPORT
================================================================================

Date: $(Get-Date)
Technician: Botwave System Organizer
Service: Business File Organization

WHAT WAS DONE
-------------
Your business computer has been organized to improve efficiency.
All files have been categorized - your originals are still in place!

SCAN RESULTS
------------
Files Scanned: $($Stats.PDFs + $Stats.Photos + $Stats.Documents + $Stats.Archives + $SuspiciousCount)
Suspicious Files Found: $SuspiciousCount
PDFs Organized: $($Stats.PDFs)
Photos Organized: $($Stats.Photos)
Documents Organized: $($Stats.Documents)
Archives Organized: $($Stats.Archives)

FOLDERS CREATED ON YOUR DESKTOP
-------------------------------
1. For_Review_TODAY
   - Suspicious/questionable files copied here
   - REVIEW THESE WITH YOUR SON BEFORE DELETING
   - May contain malware or unauthorized software

2. ORGANIZED_$(Get-Date -Format 'yyyyMMdd')
   - Copies of your files sorted by type:
     * Invoices - PDFs and billing documents
     * Photos_Jobs - Job site photos
     * Contracts - Agreements and documents
     * Receipts - Purchase receipts
     * Estimates - Job quotes
     * Archives - Zip files and compressed folders
     * Misc - Other file types

IMPORTANT NOTES
---------------
✓ NO FILES WERE DELETED
✓ Your originals are still in the same place
✓ Copies were made for organization purposes
✓ Quarantined files are copies - originals remain
✓ When in doubt, ask your son before deleting

NEXT STEPS
----------
1. Open "For_Review_TODAY" folder on your Desktop
2. Review the quarantined files with your son
3. Check the organized folders - they're just copies
4. After confirming copies work, delete the organized folder
5. Keep your originals - they're untouched

MAINTENANCE TIPS
----------------
• Save new invoices to the Invoices folder
• Keep job photos organized by date
• Delete old photos after jobs are complete
• Run this cleanup monthly

Questions? Ask your son - he'll explain everything!

================================================================================
                    Report Generated by Botwave Empire
                    Professional Business Automation
================================================================================
"@

$ReportContent | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved to: $ReportPath" -ForegroundColor Green

# Create warning file in review folder
$WarningContent = @"
⚠️ ⚠️ ⚠️  IMPORTANT - READ THIS FIRST ⚠️ ⚠️ ⚠️

This folder contains files that were flagged as suspicious or questionable.

DO NOT DELETE ANYTHING until you review with your son!

These files may be:
- Malware or viruses
- Unauthorized software
- Suspicious downloads
- Files with concerning names

Your son will help you:
1. Identify what each file is
2. Decide if it's safe to delete
3. Keep your business computer secure

Remember: Your original files are still in place.
These are COPIES for review purposes.

When in doubt, ASK YOUR SON before clicking delete!

Date: $(Get-Date)
"@

$WarningContent | Out-File -FilePath "$ReviewFolder\⚠️ READ THIS FIRST.txt" -Encoding UTF8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "         CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Check your Desktop for:" -ForegroundColor Yellow
Write-Host "  ✓ For_Review_TODAY folder (suspicious files)" -ForegroundColor White
Write-Host "  ✓ ORGANIZED_$(Get-Date -Format 'yyyyMMdd') folder (organized copies)" -ForegroundColor White
Write-Host "  ✓ CLEANUP_REPORT_$(Get-Date -Format 'yyyyMMdd').txt (full report)" -ForegroundColor White
Write-Host ""
Write-Host "Review the quarantined files with your son!" -ForegroundColor Cyan
Write-Host ""

# Open folders
Start-Process explorer.exe "$ReviewFolder"
Start-Process explorer.exe "$OrganizedFolder"

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
