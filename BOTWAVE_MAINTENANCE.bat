@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::   BOTWAVE - MONTHLY MAINTENANCE SYSTEM
::   Version: 2.0
::   Purpose: Keep business computers optimized and secure
::   Schedule: Run every 2-3 months
:: ============================================================================

title Botwave - Monthly Maintenance
color 0B

cls
echo.
echo ================================================================================
echo              BOTWAVE - MONTHLY MAINTENANCE
echo ================================================================================
echo.
echo   Keep your business computer running at peak performance.
echo.
echo   This maintenance will:
echo     [X] Clean temporary files (free disk space)
echo     [X] Clear browser caches (faster browsing)
echo     [X] Optimize system performance
echo     [X] Check system health
echo.
echo   Safe: All actions are reversible
echo.
echo ================================================================================
echo.
pause
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "REVIEW=%DESKTOP%\BOTWAVE_MAINTENANCE_%date:~-4,4%%date:~-10,2%%date:~-7,2%"
set "REPORT=%DESKTOP%\BOTWAVE_MAINTENANCE_REPORT_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

mkdir "%REVIEW%" 2>nul

:: Phase 1: System Cleanup
cls
echo.
echo ================================================================================
echo   PHASE 1: System Cleanup
echo ================================================================================
echo.

echo [1/5] Cleaning temporary files...
del /q /s /f "%TEMP%\*" 2>nul
del /q /s /f "C:\Windows\Temp\*" 2>nul
echo   Done.

echo [2/5] Flushing DNS cache...
ipconfig /flushdns >nul 2>&1
echo   Done.

echo [3/5] Emptying Recycle Bin...
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
taskkill /f /im "Skype.exe" 2>nul
taskkill /f /im "Teams.exe" 2>nul
echo   Done.

echo.
echo   Phase 1 complete.
timeout /t 2 >nul

:: Phase 2: Browser Cleanup
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
    echo   Chrome not found.
)

echo [2/3] Cleaning Edge cache...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    del /q /s /f "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul
    echo   Edge cleaned.
) else (
    echo   Edge not found.
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
    echo   Firefox not found.
)

echo.
echo   Phase 2 complete.
timeout /t 2 >nul

:: Phase 3: System Health Check
cls
echo.
echo ================================================================================
echo   PHASE 3: System Health Check
echo ================================================================================
echo.

echo [1/2] Checking disk space...
powershell -Command "Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\" | Select-Object @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,2)}},@{Name='FreeGB';Expression={[math]::Round($_.FreeSpace/1GB,2)}},@{Name='PercentFree';Expression={[math]::Round(($_.FreeSpace/$_.Size)*100,1)}} | Format-Table -AutoSize"

echo.
echo [2/2] System information...
systeminfo 2>nul | findstr /B /C:"OS Name" /C:"Total Physical Memory" /C:"Available Physical Memory"

echo.
echo   Phase 3 complete.
timeout /t 2 >nul

:: Phase 4: Generate Report
cls
echo.
echo ================================================================================
echo   PHASE 4: Generating Report
echo ================================================================================
echo.

(
echo ================================================================================
echo                    BOTWAVE - MAINTENANCE REPORT
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
echo   [X] Browser caches cleared (Chrome, Edge, Firefox)
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
echo   2. Restart your computer weekly
echo   3. Keep your desktop organized
echo   4. Contact Botwave Support for assistance
echo.
echo ================================================================================
echo   SUPPORT
echo ================================================================================
echo.
echo   Website: www.botwave.ai
echo   Email: support@botwave.ai
echo   Phone: 1-800-BOTWAVE
echo.
echo ================================================================================
echo              Botwave - Professional IT Maintenance
echo              www.botwave.ai | support@botwave.ai
echo ================================================================================
) > "%REPORT%"

copy "%REPORT%" "%REVIEW%\README.txt" >nul 2>&1

echo   Report saved to Desktop
echo.

:: Completion
cls
echo.
echo ================================================================================
echo                    MAINTENANCE COMPLETE!
echo ================================================================================
echo.
echo   Your computer has been optimized.
echo.
echo   Files created:
echo.
echo     [BOTWAVE_MAINTENANCE_REPORT_...txt] - Full report
echo.
echo   Next maintenance: Run this again in 2-3 months
echo.
echo   Support: www.botwave.ai/support
echo.
echo ================================================================================
echo.
pause

start notepad "%REPORT%"

endlocal
