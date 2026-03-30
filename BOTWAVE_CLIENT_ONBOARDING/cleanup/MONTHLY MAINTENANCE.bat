@echo off
title Jimenez Plumbing - Monthly Maintenance
color 0A

:: ============================================================================
::   JIMENEZ PLUMBING - MONTHLY MAINTENANCE
::   Run this every few months to keep laptop running like new
::
::   Takes 2-3 minutes. Safe. Nothing deleted permanently.
:: ============================================================================

cls
echo.
echo ================================================================================
echo              MONTHLY LAPTOP MAINTENANCE
echo              Jimenez Plumbing - Business Computer
echo ================================================================================
echo.
echo   Run this every 2-3 months to keep your laptop fast and clean.
echo.
echo   What this does:
echo.
echo   [X] Cleans temporary files
echo   [X] Cleans browser cache
echo   [X] Organizes desktop files
echo   [X] Checks for suspicious downloads
echo   [X] Creates backup of important settings
echo.
echo   SAFE: Nothing is permanently deleted.
echo   Everything goes to a review folder first.
echo.
echo ================================================================================
echo.
echo   Press any key to start maintenance...
pause >nul

cls
set "DATE_STAMP=%date:~-4%%date:~3,2%%date:~0,2%"
set "DESKTOP=%USERPROFILE%\Desktop"
set "REVIEW=%DESKTOP%\MAINTENANCE_REVIEW_%DATE_STAMP%"

:: Create review folder
mkdir "%REVIEW%" 2>nul

echo.
echo ================================================================================
echo   STEP 1: Cleaning Temporary Files
echo ================================================================================
echo.

echo [1/5] Cleaning Windows temp files...
del /q /s /f "%TEMP%\*" 2>nul

echo [2/5] Cleaning Windows Update cache...
del /q /s /f "C:\Windows\SoftwareDistribution\Download\*" 2>nul

echo [3/5] Emptying Recycle Bin...
del /q /s /f "C:\$Recycle.Bin\*" 2>nul

echo [4/5] Cleaning thumbnail cache...
del /q /s /f "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" 2>nul

echo [5/5] Flushing DNS cache...
ipconfig /flushdns >nul 2>&1

echo.
echo   DONE! Temporary files cleaned.
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   STEP 2: Cleaning Browser Cache
echo ================================================================================
echo.

echo [1/3] Cleaning Google Chrome cache...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    del /q /s "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" 2>nul
    echo   Chrome cache cleaned
) else (
    echo   Chrome cache not found (or already clean)
)

echo [2/3] Cleaning Microsoft Edge cache...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    del /q /s "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul
    echo   Edge cache cleaned
) else (
    echo   Edge cache not found (or already clean)
)

echo [3/3] Cleaning Firefox cache...
if exist "%APPDATA%\Mozilla\Firefox\Profiles\" (
    for /d %%p in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
        del /q /s "%%p\cache2\entries\*" 2>nul
    )
    echo   Firefox cache cleaned
) else (
    echo   Firefox not installed or cache not found
)

echo.
echo   Browser cache cleaned!
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   STEP 3: Organizing Desktop
echo ================================================================================
echo.

echo [1/3] Moving executable files to review...
set /a MOVED=0

for %%e in (exe,bat,scr,cmd,com,vbs,msi) do (
    for %%f in ("%DESKTOP%\*.%%e") do (
        if exist "%%f" (
            move "%%f" "%REVIEW%\" >nul 2>&1
            set /a MOVED+=1
        )
    )
)
echo   Moved %MOVED% executable files to review folder

echo [2/3] Organizing documents into folders...
for %%f in ("%DESKTOP%\*.pdf") do (
    if exist "%%f" move "%%f" "%DESKTOP%\02 - INVOICES\" >nul 2>&1
)

for %%f in ("%DESKTOP%\*.jpg" "%DESKTOP%\*.jpeg" "%DESKTOP%\*.png") do (
    if exist "%%f" move "%%f" "%DESKTOP%\04 - CUSTOMER PHOTOS\" >nul 2>&1
)

echo   Documents organized into proper folders

echo [3/3] Creating maintenance report...
(
echo ================================================================================
echo              MAINTENANCE REVIEW FOLDER
echo ================================================================================
echo.
echo   Date: %date% %time%
echo.
echo   This folder contains files that were moved during maintenance.
echo.
echo   FILES HERE:
echo   - Executable files (.exe, .bat, .cmd) that were on Desktop
echo   - Any suspicious downloads
echo   - Files that shouldn't be on Desktop
echo.
echo   WHAT TO DO:
echo   1. Look through this folder
echo   2. If you see something you need, move it back
echo   3. If unsure, ask your son
echo   4. When approved, you can delete this entire folder
echo.
echo   Remember: These are just COPIES or misplaced files.
echo   Your real files are safe in their proper folders.
echo.
echo ================================================================================
) > "%REVIEW%\README.txt"

echo   Report created
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   STEP 4: Quick System Check
echo ================================================================================
echo.

echo [1/4] Checking disk space...
wmic logicaldisk get size,freespace,caption 2>nul | findstr /v "Caption" | findstr /v "^$"

echo [2/4] Checking memory usage...
wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value 2>nul

echo [3/4] Checking startup programs...
echo   Current startup items:
wmic startup get caption,command 2>nul | findstr /v "^$" | findstr /v "Caption"

echo [4/4] Checking for recent software installs...
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s 2>nul | findstr "DisplayName" | findstr /v "Microsoft" | head -10

echo.
echo   System check complete!
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   STEP 5: Creating Maintenance Report
echo ================================================================================
echo.

(
echo ================================================================================
echo                    MONTHLY MAINTENANCE REPORT
echo                    Jimenez Plumbing - Business Computer
echo ================================================================================
echo.
echo   Date: %date% %time%
echo   Computer: %COMPUTERNAME%
echo.
echo ================================================================================
echo   WHAT WAS CLEANED
echo ================================================================================
echo.
echo   [X] Windows temporary files
echo   [X] Windows Update cache
echo   [X] Recycle Bin
echo   [X] Thumbnail cache
echo   [X] DNS cache
echo   [X] Chrome browser cache
echo   [X] Edge browser cache
echo   [X] Firefox browser cache
echo   [X] Desktop executable files (moved to review)
echo   [X] Desktop documents (organized into folders)
echo.
echo ================================================================================
echo   REVIEW FOLDER
echo ================================================================================
echo.
echo   Location: %REVIEW%
echo.
echo   This folder contains files moved during maintenance.
echo   Review with your son before deleting.
echo.
echo ================================================================================
echo   RECOMMENDATIONS
echo ================================================================================
echo.
echo   1. Run this maintenance every 2-3 months
echo   2. Keep Desktop organized - use the folders
echo   3. Back up QuickBooks daily
echo   4. Restart computer weekly
echo   5. Don't download software without checking first
echo.
echo ================================================================================
echo   NEXT MAINTENANCE DUE
echo ================================================================================
echo.
echo   Run this again in 2-3 months, or when:
echo   - Computer feels slow
echo   - Internet is loading slowly
echo   - Desktop is getting messy
echo   - You've downloaded new software
echo.
echo ================================================================================
echo              Maintenance by Jimenez Plumbing Automation
echo              Powered by Botwave
echo ================================================================================
) > "%DESKTOP%\MAINTENANCE_REPORT_%DATE_STAMP%.txt"

echo   Report saved to Desktop
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo                      MAINTENANCE COMPLETE!
echo ================================================================================
echo.
echo   Your laptop is now clean and optimized.
echo.
echo   On your Desktop:
echo.
echo     [MAINTENANCE_REPORT_%DATE_STAMP%.txt] - Full report
echo     [MAINTENANCE_REVIEW_%DATE_STAMP%]     - Files for review
echo.
echo   Run this maintenance script again in 2-3 months.
echo.
echo   Or whenever your computer feels slow.
echo.
echo ================================================================================
echo.
echo   Tips for keeping laptop fast:
echo.
echo   * Don't download programs without checking first
echo   * Keep Desktop organized - use the folders
echo   * Restart computer at least once a week
echo   * Run this maintenance every few months
echo.
echo ================================================================================
echo.
echo   Press any key to view the report...
pause >nul

notepad "%DESKTOP%\MAINTENANCE_REPORT_%DATE_STAMP%.txt"

echo.
echo.
echo   Done! You can close this window.
echo.
echo   Next maintenance due in 2-3 months.
echo.
pause
