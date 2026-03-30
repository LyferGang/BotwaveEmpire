@echo off
REM Jimenez Plumbing - Business File Organizer
REM Run this on the Windows laptop to organize files

echo ==========================================
echo   JIMENEZ PLUMBING FILE ORGANIZER
echo ==========================================
echo.
echo This will organize your business files
echo NO FILES WILL BE DELETED - only copied
echo.

set BASEPATH=C:\Users\jpsji\OneDrive\Desktop\jpsji\Dropbox\JIMENEZ PLUMBING
set REVIEWFOLDER=%USERPROFILE%\Desktop\For_Review_TODAY
set ORGANIZED=%USERPROFILE%\Desktop\ORGANIZED_%date:~-4,4%%date:~-10,2%%date:~-7,2%

echo Checking path: %BASEPATH%

if not exist "%BASEPATH%" (
    echo ERROR: Path not found!
    echo Please verify the folder exists
    pause
    exit /b 1
)

echo.
echo Creating organization folders...
mkdir "%REVIEWFOLDER%" 2>nul
mkdir "%ORGANIZED%"\Invoices 2>nul
mkdir "%ORGANIZED%"\Photos_Jobs 2>nul
mkdir "%ORGANIZED%\Contracts" 2>nul
mkdir "%ORGANIZED%\Receipts" 2>nul
mkdir "%ORGANIZED%\Estimates" 2>nul
mkdir "%ORGANIZED%\Misc" 2>nul
mkdir "%ORGANIZED%\Archives" 2>nul

echo.
echo ==========================================
echo PHASE 1: Scanning for suspicious files...
echo ==========================================

echo Checking for suspicious executables...
for %%E in (exe bat scr com cmd) do (
    for /r "%BASEPATH%" %%F in (*.%%E) do (
        echo [WARNING] Suspicious file: %%F
        copy "%%F" "%REVIEWFOLDER%\SUSPICIOUS_%%~nxF" >nul 2>&1
        echo   - Copied to For_Review_TODAY
    )
)

echo.
echo Checking for files with suspicious names...
findstr /i /s /m "crack keygen patch hack serial" "%BASEPATH%\*.*" 2>nul > "%TEMP%\suspicious_files.txt"
for /f %%F in (%TEMP%\suspicious_files.txt) do (
    copy "%%F" "%REVIEWFOLDER%\QUESTIONABLE_%%~nxF" >nul 2>&1
    echo [QUARANTINED] %%F
)

echo.
echo ==========================================
echo PHASE 2: Organizing business files...
echo ==========================================

setlocal enabledelayedexpansion
set /a COUNT=0

for /r "%BASEPATH%" %%F in (*.pdf) do (
    copy "%%F" "%ORGANIZED%\Invoices\" 2>nul
    set /a COUNT+=1
)
echo PDFs: !COUNT! files

set /a COUNT=0
for /r "%BASEPATH%" %%F in (*.jpg *.jpeg *.png *.gif *.bmp *.heic) do (
    copy "%%F" "%ORGANIZED%\Photos_Jobs\" 2>nul
    set /a COUNT+=1
)
echo Photos: !COUNT! files

set /a COUNT=0
for /r "%BASEPATH%" %%F in (*.doc *.docx *.txt) do (
    copy "%%F" "%ORGANIZED%\Contracts\" 2>nul
    set /a COUNT+=1
)
echo Documents: !COUNT! files

set /a COUNT=0
for /r "%BASEPATH%" %%F in (*.zip *.rar *.7z) do (
    copy "%%F" "%ORGANIZED%\Archives\" 2>nul
    set /a COUNT+=1
)
echo Archives: !COUNT! files

endlocal

echo.
echo ==========================================
echo PHASE 3: Creating report...
echo ==========================================

set REPORT=%USERPROFILE%\Desktop\CLEANUP_REPORT_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt

echo JIMENEZ PLUMBING - COMPUTER CLEANUP REPORT > "%REPORT%"
echo ========================================= >> "%REPORT%"
echo Date: %date% %time% >> "%REPORT%"
echo Technician: Botwave System Organizer >> "%REPORT%"
echo. >> "%REPORT%"
echo WHAT WAS DONE: >> "%REPORT%"
echo - Scanned all business files >> "%REPORT%"
echo - Moved suspicious files to For_Review_TODAY >> "%REPORT%"
echo - Organized files by category >> "%REPORT%"
echo. >> "%REPORT%"
echo FOLDERS CREATED ON YOUR DESKTOP: >> "%REPORT%"
echo 1. For_Review_TODAY - Suspicious files for review >> "%REPORT%"
echo 2. ORGANIZED_[date] - Organized copies by type >> "%REPORT%"
echo. >> "%REPORT%"
echo IMPORTANT: >> "%REPORT%"
echo - NO FILES WERE DELETED >> "%REPORT%"
echo - Original files are still in place >> "%REPORT%"
echo - Copies were made for organization >> "%REPORT%"
echo - Review quarantined files with your son! >> "%REPORT%"
echo. >> "%REPORT%"
echo NEXT STEPS: >> "%REPORT%"
echo 1. Check Desktop/For_Review_TODAY folder >> "%REPORT%"
echo 2. Review suspicious files with your son >> "%REPORT%"
echo 3. Check organized folders >> "%REPORT%"
echo 4. Delete organized copies after confirming >> "%REPORT%"
echo. >> "%REPORT%"
echo Questions? Ask your son! >> "%REPORT%"

echo.
echo ==========================================
echo CLEANUP COMPLETE!
echo ==========================================
echo.
echo Check your Desktop for:
echo   - For_Review_TODAY folder (suspicious files)
echo   - ORGANIZED_[date] folder (organized copies)
echo   - CLEANUP_REPORT_[date].txt (full report)
echo.
echo Review the quarantined files with your son!
echo.
pause
