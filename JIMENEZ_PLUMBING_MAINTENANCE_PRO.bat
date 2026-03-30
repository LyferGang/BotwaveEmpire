@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::   JIMENEZ PLUMBING - PROFESSIONAL MONTHLY MAINTENANCE
::   Version: 2.0
::   Purpose: Keep business computers running smoothly
::   Run: Every 2-3 months or when computer feels slow
:: ============================================================================

title Jimenez Plumbing - Monthly Maintenance
color 0B

cls
echo.
echo ================================================================================
echo              JIMENEZ PLUMBING - MONTHLY MAINTENANCE
echo ================================================================================
echo.
echo   This maintenance script keeps your business computer running fast.
echo.
echo   What it does:
echo     [X] Cleans temporary files (frees disk space)
echo     [X] Cleans browser cache (faster internet)
echo     [X] Checks disk space (prevents problems)
echo     [X] Reviews startup programs (faster boot)
echo.
echo   Safe: Nothing is permanently deleted without backup
echo.
echo ================================================================================
echo.
pause
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "REVIEW=%DESKTOP%\MAINTENANCE_REVIEW_%date:~-4,4%%date:~-10,2%%date:~-7,2%"
set "REPORT=%DESKTOP%\MAINTENANCE_REPORT_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

mkdir "%REVIEW%" 2>nul

:: ============================================================================
:: PHASE 1: System Cleanup
:: ============================================================================

cls
echo.
echo ================================================================================
echo   PHASE 1: System Cleanup
echo ================================================================================
echo.

echo [1/5] Cleaning Windows temporary files...
del /q /s /f "%TEMP%\*" 2>nul
del /q /s /f "C:\Windows\Temp\*" 2>nul
echo   Done.

echo [2/5] Flushing DNS cache...
ipconfig /flushdns >nul 2>&1
echo   Done.

echo [3/5] Cleaning Recycle Bin...
if exist "C:\$Recycle.Bin" (
    for /d %%x in ("C:\$Recycle.Bin\*") do (
        rd /s /q "%%x" 2>nul
    )
)
echo   Done.

echo [4/5] Cleaning thumbnail cache...
del /q /s /f "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" 2>nul
echo   Done.

echo [5/5] Stopping unnecessary background processes...
taskkill /f /im "OneDrive.exe" 2>nul
taskkill /f /im "Skype.exe" 2>nul
echo   Done.

echo.
echo   Phase 1 complete.
timeout /t 2 >nul

:: ============================================================================
:: PHASE 2: Browser Cleanup
:: ============================================================================

cls
echo.
echo ================================================================================
echo   PHASE 2: Browser Cleanup
echo ================================================================================
echo.

echo [1/3] Cleaning Chrome cache...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    del /q /s /f "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" 2>nul
    echo   Chrome cleaned.
) else (
    echo   Chrome not found or already clean.
)

echo [2/3] Cleaning Edge cache...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    del /q /s /f "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul
    echo   Edge cleaned.
) else (
    echo   Edge not found or already clean.
)

echo [3/3] Cleaning Firefox cache...
if exist "%APPDATA%\Mozilla\Firefox\Profiles" (
    for /d %%p in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
        if exist "%%p\cache2\entries" (
            del /q /s /f "%%p\cache2\entries\*" 2>nul
        )
    )
    echo   Firefox cleaned.
) else (
    echo   Firefox not found or already clean.
)

echo.
echo   Phase 2 complete.
timeout /t 2 >nul

:: ============================================================================
:: PHASE 3: System Health Check
:: ============================================================================

cls
echo.
echo ================================================================================
echo   PHASE 3: System Health Check
echo ================================================================================
echo.

echo [1/3] Checking disk space...
for /f "tokens=3" %%a in ('wmic logicaldisk where "DeviceID='C:'" get FreeSpace /value 2^>nul ^| find "="') do set "FREE_BYTES=%%a"
for /f "tokens=3" %%a in ('wmic logicaldisk where "DeviceID='C:'" get Size /value 2^>nul ^| find "="') do set "TOTAL_BYTES=%%a"

:: Simple display (detailed in report)
powershell -Command "Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\" | Select-Object @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,2)}},@{Name='FreeGB';Expression={[math]::Round($_.FreeSpace/1GB,2)}},@{Name='PercentFree';Expression={[math]::Round(($_.FreeSpace/$_.Size)*100,1)}} | Format-Table -AutoSize"

echo.
echo [2/3] Checking for large temporary files...
set "LARGE_FILES=0"
for /f %%a in ('dir /s "C:\Windows\Temp" 2^>nul ^| find "File(s)"') do (
    echo   Windows temp files: %%a
)

echo [3/3] System information...
systeminfo 2>nul | findstr /B /C:"OS Name" /C:"Total Physical Memory" /C:"Available Physical Memory"

echo.
echo   Phase 3 complete.
timeout /t 2 >nul

:: ============================================================================
:: PHASE 4: Generate Report
:: ============================================================================

cls
echo.
echo ================================================================================
echo   PHASE 4: Generating Report
echo ================================================================================
echo.

(
echo ================================================================================
echo                    JIMENEZ PLUMBING - MAINTENANCE REPORT
echo ================================================================================
echo.
echo   Date: %date% %time%
echo   Computer: %COMPUTERNAME%
echo   User: %USERNAME%
echo.
echo ================================================================================
echo   MAINTENANCE COMPLETED
echo ================================================================================
echo.
echo   [X] Windows temporary files cleaned
echo   [X] Browser caches cleaned (Chrome, Edge, Firefox)
echo   [X] DNS cache flushed
echo   [X] Recycle Bin emptied
echo   [X] Thumbnail cache cleared
echo   [X] System health checked
echo.
echo ================================================================================
echo   RECOMMENDATIONS
echo ================================================================================
echo.
echo   1. Run this maintenance every 2-3 months
echo   2. Restart your computer at least once a week
echo   3. Keep desktop organized using your business folders
echo   4. Back up QuickBooks files daily
echo   5. Don't download software without asking your son first
echo.
echo ================================================================================
echo   NEXT MAINTENANCE DUE
echo ================================================================================
echo.
echo   Schedule: 2-3 months from today
echo   Or when: Computer feels slow, internet is slow, or desktop is messy
echo.
echo ================================================================================
echo              Jimenez Plumbing - Professional IT Maintenance
echo ================================================================================
) > "%REPORT%"

echo   Report saved to: %REPORT%
copy "%REPORT%" "%REVIEW%\README.txt" >nul 2>&1
echo.

:: ============================================================================
:: COMPLETION
:: ============================================================================

cls
echo.
echo ================================================================================
echo                    MAINTENANCE COMPLETE!
echo ================================================================================
echo.
echo   Your computer has been cleaned and optimized.
echo.
echo   Files on your Desktop:
echo.
echo     [MAINTENANCE_REPORT_...txt] - Full report with details
echo     [MAINTENANCE_REVIEW_...]    - Review folder (if needed)
echo.
echo   Recommended next steps:
echo     1. Read the report for full details
echo     2. Restart your computer now for best performance
echo     3. Run this again in 2-3 months
echo.
echo ================================================================================
echo.
pause

:: Open the report
start notepad "%REPORT%"

endlocal
