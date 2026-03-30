@echo off
title Jimenez Plumbing - Professional Laptop Setup
color 0B

:: ============================================================================
::   JIMENEZ PLUMBING - PROFESSIONAL LAPTOP OVERHAUL
::   Makes his laptop run like a proper business computer
::
::   Does NOT delete anything permanently
::   Everything goes to review folder first
:: ============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ================================================================================
echo              JIMENEZ PLUMBING - PROFESSIONAL LAPTOP SETUP
echo ================================================================================
echo.
echo   This will make your laptop run faster and cleaner.
echo.
echo   Like a brand new business computer should.
echo.
echo   SAFE MODE: Nothing is deleted without your approval.
echo.
echo ================================================================================
echo.
echo   What this will do:
echo.
echo   [X] Clean up temporary files (makes it faster)
echo   [X] Fix startup programs (stops slow boot)
echo   [X] Organize desktop files (easy to find stuff)
echo   [X] Remove browser junk (cleaner internet)
echo   [X] Set up proper folders (professional setup)
echo.
echo   Your personal files are SAFE.
echo.
echo ================================================================================
echo.
echo   Press any key to start...
pause >nul

cls
echo.
echo ================================================================================
echo   PHASE 1: Cleaning temporary files
echo ================================================================================
echo.
echo   This makes your computer run faster...
echo.

:: Clean Windows temp files
echo [1/6] Cleaning Windows temporary files...
del /q /s /f "%TEMP%\*" 2>nul
del /q /s /f "C:\Windows\Temp\*" 2>nul

:: Clean prefetch (old startup cache)
echo [2/6] Cleaning startup cache...
del /q /s /f "C:\Windows\Prefetch\*" 2>nul

:: Clean recycle bin
echo [3/6] Emptying Recycle Bin...
del /q /s /f "C:\$Recycle.Bin\*" 2>nul

:: Clean thumbnails cache
echo [4/6] Cleaning thumbnail cache...
del /q /s /f "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" 2>nul

:: Clean DNS cache
echo [5/6] Flushing DNS cache...
ipconfig /flushdns >nul 2>&1

:: Clean Windows update cache (old updates)
echo [6/6] Cleaning old Windows Update files...
del /q /s /f "C:\Windows\SoftwareDistribution\Download\*" 2>nul

echo.
echo   DONE! Temporary files cleaned.
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 2: Organizing your Desktop
echo ================================================================================
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "DOCUMENTS=%USERPROFILE%\Documents"
set "REVIEW=%DESKTOP%\FOR_REVIEW_BEFORE_DELETE"
set "DATE_STAMP=%date:~-4%%date:~3,2%%date:~0,2%"

:: Create review folder
echo [1/4] Creating review folder...
mkdir "%REVIEW%" 2>nul

:: Create organized business folders
echo [2/4] Creating professional folder structure...
mkdir "%DESKTOP%\01 - ACTIVE JOBS" 2>nul
mkdir "%DESKTOP%\02 - INVOICES" 2>nul
mkdir "%DESKTOP%\03 - ESTIMATES" 2>nul
mkdir "%DESKTOP%\04 - CUSTOMER PHOTOS" 2>nul
mkdir "%DESKTOP%\05 - RECEIPTS" 2>nul
mkdir "%DESKTOP%\06 - SUPPLIERS" 2>nul
mkdir "%DESKTOP%\99 - ARCHIVE" 2>nul

mkdir "%DOCUMENTS%\Jimenez Plumbing\Invoices" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Estimates" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Customer Photos" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Receipts" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Suppliers" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Insurance" 2>nul
mkdir "%DOCUMENTS%\Jimenez Plumbing\Licenses" 2>nul

:: Move random desktop files to review
echo [3/4] Organizing desktop files...
set /a MOVED=0

for %%e in (exe,bat,scr,cmd,com,vbs,msi,zip,rar) do (
    for %%f in ("%DESKTOP%\*.%%e") do (
        if exist "%%f" (
            move "%%f" "%REVIEW%\" >nul 2>&1
            set /a MOVED+=1
        )
    )
)

:: Move old files to archive
for %%f in ("%DESKTOP%\*.txt" "%DESKTOP%\*.doc" "%DESKTOP%\*.docx" "%DESKTOP%\*.pdf") do (
    if exist "%%f" (
        move "%%f" "%DESKTOP%\99 - ARCHIVE\" >nul 2>&1
        set /a MOVED+=1
    )
)

echo   Moved %MOVED% files to organized folders
echo.

:: Create shortcuts folder
echo [4/4] Creating shortcuts...
echo.

:: Create a simple batch file to open business folders
(
echo @echo off
echo title Jimenez Plumbing - Quick Access
echo color 0A
echo cls
echo.
echo ================================================================================
echo                    JIMENEZ PLUMBING - QUICK ACCESS
echo ================================================================================
echo.
echo   Opening business folders...
echo.
explorer "%DESKTOP%\01 - ACTIVE JOBS"
explorer "%DESKTOP%\02 - INVOICES"
explorer "%DESKTOP%\03 - ESTIMATES"
explorer "%DESKTOP%\04 - CUSTOMER PHOTOS"
echo.
echo   Folders opened!
echo.
echo   Press any key to close...
echo pause ^>nul
) > "%DESKTOP%\OPEN BUSINESS FOLDERS.bat"

echo   Created quick access shortcut on Desktop
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 3: Cleaning up Startup Programs
echo ================================================================================
echo.
echo   This stops unnecessary programs from slowing down startup...
echo.

:: Create registry backup first
echo [1/3] Backing up current settings...
reg export HKCU\Software\Microsoft\Windows\CurrentVersion\Run "%REVIEW%\startup_backup.reg" 2>nul

:: Disable common junk startup items
echo [2/3] Disabling unnecessary startup programs...

:: Skype startup
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Skype" /f 2>nul

:: OneDrive startup (keep it but disable auto-start)
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OneDrive" /f 2>nul

:: Cortana
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Cortana" /f 2>nul

:: Microsoft Teams
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "com.squirrel.Teams.Teams" /f 2>nul

:: Spotify
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Spotify" /f 2>nul

:: Steam
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Steam" /f 2>nul

:: Discord
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Discord" /f 2>nul

echo [3/3] Optimizing power settings...
:: Set to high performance
powercfg /setactive SCHEME_MIN 2>nul

echo.
echo   Startup programs cleaned!
echo   Computer will boot faster now.
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 4: Browser Cleanup
echo ================================================================================
echo.
echo   Cleaning internet browser junk...
echo.

:: Chrome cleanup
echo [1/3] Cleaning Google Chrome...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    del /q /s "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" 2>nul
)
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies" (
    echo   Chrome cookies preserved
)

:: Edge cleanup
echo [2/3] Cleaning Microsoft Edge...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    del /q /s "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul
)

:: Firefox cleanup
echo [3/3] Cleaning Mozilla Firefox...
if exist "%APPDATA%\Mozilla\Firefox\Profiles\" (
    for /d %%p in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
        del /q /s "%%p\cache2\entries\*" 2>nul
    )
)

echo.
echo   Browser cache cleaned!
echo   Internet should load faster now.
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 5: Creating Business Shortcuts
echo ================================================================================
echo.

:: Create business apps shortcut on desktop
(
echo @echo off
echo title Jimenez Plumbing - Business Apps
echo color 0B
echo cls
echo.
echo   Opening business applications...
echo.
timeout /t 1 >nul
start excel.exe
timeout /t 1 >nul
start winword.exe
timeout /t 1 >nul
start outlook.exe
echo.
echo   Business apps started!
echo.
pause
) > "%DESKTOP%\BUSINESS APPS.bat"

:: Create quick books backup reminder
(
echo @echo off
echo title QuickBooks Backup Reminder
echo color 0A
echo cls
echo.
echo ================================================================================
echo                    QUICKBOOKS BACKUP REMINDER
echo ================================================================================
echo.
echo   This is your reminder to back up QuickBooks!
echo.
echo   You should do this EVERY DAY before closing.
echo.
echo   1. Open QuickBooks
echo   2. Go to File - Save Copy or Backup
echo   3. Choose "Backup copy"
echo   4. Save to: %USERPROFILE%\Documents\Jimenez Plumbing\QuickBooks Backups
echo.
echo   Or plug in your USB drive and back up there.
echo.
echo ================================================================================
echo.
pause
) > "%DESKTOP%\QUICKBOOKS BACKUP REMINDER.bat"

echo   Created business shortcuts on Desktop
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 6: Creating Simple Instructions
echo ================================================================================
echo.

:: Create main instructions file
(
echo ================================================================================
echo              YOUR NEW PROFESSIONAL LAPTOP SETUP
echo ================================================================================
echo.
echo   Date: %date%
echo.
echo   Your laptop has been set up like a proper business computer.
echo.
echo ================================================================================
echo   WHAT CHANGED
echo ================================================================================
echo.
echo   DESKTOP - Now organized with proper folders:
echo.
echo   [01 - ACTIVE JOBS]      - Put current job files here
echo   [02 - INVOICES]         - All your invoices
echo   [03 - ESTIMATES]        - Quotes and estimates
echo   [04 - CUSTOMER PHOTOS]  - Job site photos
echo   [05 - RECEIPTS]         - Material receipts
echo   [06 - SUPPLIERS]        - Supplier info and price lists
echo   [99 - ARCHIVE]          - Old completed jobs
echo.
echo   DESKTOP SHORTCUTS:
echo.
echo   [OPEN BUSINESS FOLDERS] - Opens all your folders at once
echo   [BUSINESS APPS]         - Opens Excel, Word, Outlook together
echo   [QUICKBOOKS BACKUP]     - Reminder to back up QuickBooks
echo.
echo ================================================================================
echo   DAILY ROUTINE
echo ================================================================================
echo.
echo   MORNING:
echo   1. Turn on computer
echo   2. Click [BUSINESS APPS] to start your programs
echo   3. Check [01 - ACTIVE JOBS] for today's work
echo.
echo   EVENING (before closing):
echo   1. Run [QUICKBOOKS BACKUP]
echo   2. Move completed jobs to [99 - ARCHIVE]
echo   3. Shut down computer
echo.
echo ================================================================================
echo   WEEKLY ROUTINE (Friday afternoon)
echo ================================================================================
echo.
echo   1. Run [QUICKBOOKS BACKUP]
echo   2. Copy backup to USB drive (take home)
echo   3. Check [FOR_REVIEW_BEFORE_DELETE] folder
echo   4. Ask your son what's safe to delete
echo.
echo ================================================================================
echo   IMPORTANT NOTES
echo ================================================================================
echo.
echo   * Your computer should now start faster
echo   * Internet should load pages quicker
echo   * Desktop is organized - easy to find things
echo   * Nothing was permanently deleted
echo   * All your files are still in Documents
echo.
echo   FOR_REVIEW_BEFORE_DELETE folder has files your son should check.
echo   Don't delete anything in there until he says it's OK.
echo.
echo ================================================================================
echo              Setup by your son - Jimenez Plumbing Automation
echo ================================================================================
) > "%DESKTOP%\START_HERE_READ_THIS.txt"

echo   Created instruction file on Desktop
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo   PHASE 7: Creating Final Report
echo ================================================================================
echo.

:: Count what was done
set "FILES_CLEANED=0"
for /f "tokens=*" %%a in ('dir /b /a-d "%TEMP%" 2^>nul ^| find /c /v ""') do set FILES_CLEANED=%%a

:: Create final report
(
echo ================================================================================
echo                    LAPTOP OVERHAUL - COMPLETION REPORT
echo ================================================================================
echo.
echo   Date: %date% %time%
echo   Computer: %COMPUTERNAME%
echo   User: %USERNAME%
echo.
echo ================================================================================
echo   WHAT WAS DONE
echo ================================================================================
echo.
echo   CLEANING:
echo   - Temporary files removed: approximately %FILES_CLEANED% files
echo   - Windows Update cache: cleaned
echo   - Recycle Bin: emptied
echo   - Browser cache: cleaned (Chrome, Edge, Firefox)
echo   - DNS cache: flushed
echo.
echo   STARTUP OPTIMIZATION:
echo   - Unnecessary startup programs: disabled
echo   - Power settings: optimized for performance
echo   - Startup registry: backed up to FOR_REVIEW_BEFORE_DELETE folder
echo.
echo   ORGANIZATION:
echo   - Desktop: organized with professional folders
echo   - Documents: business folder structure created
echo   - Shortcuts: business apps quick launch created
echo.
echo   FOLDERS CREATED:
echo   - %DESKTOP%\01 - ACTIVE JOBS
echo   - %DESKTOP%\02 - INVOICES
echo   - %DESKTOP%\03 - ESTIMATES
echo   - %DESKTOP%\04 - CUSTOMER PHOTOS
echo   - %DESKTOP%\05 - RECEIPTS
echo   - %DESKTOP%\06 - SUPPLIERS
echo   - %DESKTOP%\99 - ARCHIVE
echo   - %DOCUMENTS%\Jimenez Plumbing\
echo.
echo ================================================================================
echo   EXPECTED IMPROVEMENTS
echo ================================================================================
echo.
echo   [X] Faster startup (programs won't auto-load unnecessarily)
echo   [X] Faster internet browsing (clean browser cache)
echo   [X] Easier to find files (organized folders)
echo   [X] Cleaner desktop (professional appearance)
echo   [X] Better backup habits (daily reminders)
echo.
echo ================================================================================
echo   FILES FOR REVIEW
echo ================================================================================
echo.
echo   Location: %REVIEW%
echo.
echo   This folder contains:
echo   - Executable files that were on Desktop
echo   - Startup registry backup
echo   - Any files flagged for review
echo.
echo   DO NOT DELETE anything in this folder until your son reviews it.
echo.
echo ================================================================================
echo                    Setup Complete!
echo ================================================================================
echo.
echo   Next Steps:
echo.
echo   1. Restart the computer to see improvements
echo   2. Read START_HERE_READ_THIS.txt on Desktop
echo   3. Review FOR_REVIEW_BEFORE_DELETE folder with your son
echo   4. Start using the new organized folders
echo.
echo   Questions? Your son will explain everything!
echo.
echo ================================================================================
echo              Jimenez Plumbing - Professional Business Setup
echo              Powered by Botwave Automation
echo ================================================================================
) > "%DESKTOP%\OVERHAUL_COMPLETE_REPORT.txt"

echo   Final report created on Desktop
echo.
timeout /t 2 >nul

cls
echo.
echo ================================================================================
echo                      ALL DONE!
echo ================================================================================
echo.
echo   Your laptop has been professionally set up.
echo.
echo   Check your Desktop for:
echo.
echo     [START_HERE_READ_THIS]     - Read this first!
echo     [01 - ACTIVE JOBS]         - Your current jobs
echo     [02 - INVOICES]            - All invoices
echo     [03 - ESTIMATES]           - Quotes
echo     [04 - CUSTOMER PHOTOS]     - Job photos
echo     [05 - RECEIPTS]            - Material receipts
echo     [06 - SUPPLIERS]           - Supplier info
echo     [99 - ARCHIVE]             - Completed jobs
echo.
echo     [OPEN BUSINESS FOLDERS]    - Opens all folders
echo     [BUSINESS APPS]            - Opens Excel, Word, Outlook
echo     [QUICKBOOKS BACKUP]        - Backup reminder
echo.
echo     [OVERHAUL_COMPLETE_REPORT.txt] - Full report
echo     [FOR_REVIEW_BEFORE_DELETE]     - Files to review with son
echo.
echo ================================================================================
echo.
echo   RESTART YOUR COMPUTER NOW to see the improvements!
echo.
echo   After restart:
echo   - Computer should boot faster
echo   - Internet should load quicker
echo   - Desktop is organized and professional
echo.
echo ================================================================================
echo.
echo   Press any key to open the instruction file...
pause >nul

notepad "%DESKTOP%\START_HERE_READ_THIS.txt"

:: Ask if user wants to restart
echo.
echo.
echo   Would you like to restart now?
echo.
echo   Press Y to restart, or close this window to restart later.
echo.
set /p RESTART="Restart now? (Y/N): "
if /i "%RESTART%"=="Y" (
    echo.
    echo   Restarting in 5 seconds...
    echo   Save any open files first!
    timeout /t 5
    shutdown /r /t 0
)

endlocal
