#!/usr/bin/env pwsh
# ==============================================================================
#   S C R Y P T  K E E P E R   | B O T W A V E   E M P I R E
# ==============================================================================
#   JOB: UNIVERSAL BUSINESS WRENCH - JPS OPTIMIZATION
#   STATION: HQ-POP_OS (Windows)
#   STATUS: READY FOR DEPLOYMENT
# ==============================================================================

$ClientName = "JIMENEZ PLUMBING"
$SearchTerms = @("JPS", "JIMENEZ PLUMBING", "Invoices", "Materials")
$BackupDir = "$env:USERPROFILE\Desktop\BOTWAVE_BACKUP"

$foundFolders = @()
$totalFound = 0

# THE SWEEP (JETTING)
foreach ($term in $SearchTerms) {
    try {
        # Hunt for directories matching search terms
        $matches = Get-ChildItem -Path C:\ -Recurse | Where-Object { $_.Name -like "*$term*" }
        
        if ($matches.Count -gt 0) {
            foreach ($match in $matches) {
                $foundFolders += $match.FullName
                $totalFound++
            }
        }
    } catch {
        Write-Host "Error scanning for '$term': $_" -ForegroundColor Red
    }
}

# THE GREASE TRAP (BACKUP)
if ($foundFolders.Count -gt 0) {
    try {
        $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
        $backupPath = Join-Path $BackupDir ("BOTWAVE_BACKUP_$timestamp")
        
        New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
        
        foreach ($folder in $foundFolders) {
            Copy-Item -Path $folder -Destination $backupPath -Recurse -ErrorAction SilentlyContinue
        }
        
        Write-Host "BACKUP COMPLETE: Folders moved to $backupPath" -ForegroundColor Green
    } catch {
        Write-Host "Backup error: $_" -ForegroundColor Red
    }
}

# THE PURGE (SYSTEM SLUDGE)
$purgePaths = @(
    "C:\Windows\Temp",
    "$env:TEMP",
    "$env:SystemRoot\System32\Prefetch"
)

foreach ($path in $purgePaths) {
    try {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Purge error for '$path': $_" -ForegroundColor Yellow
    }
}

# THE REPORT
Write-Host ""
Write-Host "TOTAL FOLDERS FOUND: [$totalFound] | SYSTEM SLUDGE PURGED: [OK]" -ForegroundColor Cyan
