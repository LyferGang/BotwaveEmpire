@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::   BOTWAVE - PROFESSIONAL COMPUTER CLEANUP SYSTEM
::   Version: 2.0
::   Purpose: Business file organization and system optimization
::   Safety: Non-destructive - creates copies only
:: ============================================================================

title Botwave - Business Computer Cleanup
color 0A

cls
echo.
echo ================================================================================
echo              BOTWAVE - PROFESSIONAL COMPUTER CLEANUP
echo ================================================================================
echo.
echo   This tool safely organizes your business files.
echo.
echo   [IMPORTANT] ORIGINAL FILES ARE NEVER DELETED
echo   We create organized copies for your review.
echo.
echo ================================================================================
echo.
pause
echo.

:: Initialize paths
set "DESKTOP=%USERPROFILE%\Desktop"
set "DOCUMENTS=%USERPROFILE%\Documents"
set "REVIEW_FOLDER=%DESKTOP%\BOTWAVE_REVIEW_%date:~-4,4%%date:~-10,2%%date:~-7,2%"
set "ORGANIZED=%DESKTOP%\BOTWAVE_ORGANIZED_%date:~-4,4%%date:~-10,2%%date:~-7,2%"

:: Validate paths
if not exist "%DESKTOP%" (
    echo ERROR: Desktop folder not found!
    pause
    exit /b 1
)

:: Create folder structure
echo Creating organization folders...
mkdir "%REVIEW_FOLDER%" 2>nul
mkdir "%ORGANIZED%\01-Documents_PDFs" 2>nul
mkdir "%ORGANIZED%\02-Photos_Images" 2>nul
mkdir "%ORGANIZED%\03-Spreadsheets_Data" 2>nul
mkdir "%ORGANIZED%\04-Archives_Zips" 2>nul
mkdir "%ORGANIZED%\05-Executables_ForReview" 2>nul

echo   Done.
echo.

:: Phase 1: Security Scan
echo Phase 1: Security scan for executable files...
set "SUSPICIOUS_COUNT=0"

:: Scan common locations for executables
set "SCAN_PATHS=%USERPROFILE%\Downloads %DESKTOP%"

for %%P in (%SCAN_PATHS%) do (
    if exist "%%P" (
        for %%E in (exe bat cmd vbs js scr msi) do (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                set /a SUSPICIOUS_COUNT+=1
                echo   [!SUSPICIOUS_COUNT!] Found: %%~nxF
                copy "%%F" "%ORGANIZED%\05-Executables_ForReview\" >nul 2>&1
            )
        )
    )
)

if !SUSPICIOUS_COUNT! gtr 0 (
    echo   [!SUSPICIOUS_COUNT!] executable files found and flagged
) else (
    echo   No executable files found
)
echo.

:: Phase 2: Organize Documents
echo Phase 2: Organizing documents...
set "PDF_COUNT=0"
set "DOC_COUNT=0"

for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.pdf" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\01-Documents_PDFs\" >nul 2>&1
            if !errorlevel! equ 0 set /a PDF_COUNT+=1
        )
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.doc*" "%%~P\*.txt" "%%~P\*.rtf" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\01-Documents_PDFs\" >nul 2>&1
            if !errorlevel! equ 0 set /a DOC_COUNT+=1
        )
    )
)

echo   PDFs: !PDF_COUNT!  Documents: !DOC_COUNT!
echo.

:: Phase 3: Organize Photos
echo Phase 3: Organizing images...
set "PHOTO_COUNT=0"

for %%E in (jpg jpeg png gif bmp heic webp tiff) do (
    for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%~P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\02-Photos_Images\" >nul 2>&1
                if !errorlevel! equ 0 set /a PHOTO_COUNT+=1
            )
        )
    )
)

echo   Images organized: !PHOTO_COUNT!
echo.

:: Phase 4: Organize Spreadsheets
echo Phase 4: Organizing spreadsheets...
set "SHEET_COUNT=0"

for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.xls*" "%%~P\*.csv" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\03-Spreadsheets_Data\" >nul 2>&1
            if !errorlevel! equ 0 set /a SHEET_COUNT+=1
        )
    )
)

echo   Spreadsheets: !SHEET_COUNT!
echo.

:: Phase 5: Organize Archives
echo Phase 5: Organizing archives...
set "ARCHIVE_COUNT=0"

for %%E in (zip rar 7z tar gz bz2) do (
    for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%~P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\04-Archives_Zips\" >nul 2>&1
                if !errorlevel! equ 0 set /a ARCHIVE_COUNT+=1
            )
        )
    )
)

echo   Archives: !ARCHIVE_COUNT!
echo.

:: Generate Report
echo Phase 6: Generating report...

set "REPORT_FILE=%DESKTOP%\BOTWAVE_CLEANUP_REPORT_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

(
echo ================================================================================
echo                    BOTWAVE - CLEANUP REPORT
echo ================================================================================
echo.
echo   Date: %date% %time%
echo   Computer: %COMPUTERNAME%
echo   User: %USERNAME%
echo.
echo ================================================================================
echo   FILES ORGANIZED
echo ================================================================================
echo.
echo   PDF Documents:       !PDF_COUNT!
echo   Word Documents:      !DOC_COUNT!
echo   Photos/Images:       !PHOTO_COUNT!
echo   Spreadsheets:        !SHEET_COUNT!
echo   Archives:            !ARCHIVE_COUNT!
echo   Executables Flagged: !SUSPICIOUS_COUNT!
echo.
echo ================================================================================
echo   FOLDERS CREATED
echo ================================================================================
echo.
echo   Review Folder:     %REVIEW_FOLDER%
echo   Organized Files:   %ORGANIZED%
echo.
echo ================================================================================
echo   IMPORTANT NOTES
echo ================================================================================
echo.
echo   * NO ORIGINAL FILES WERE DELETED
echo   * All files remain in their original locations
echo   * These are COPIES for organization and review
echo   * Review flagged executables before deletion
echo.
echo ================================================================================
echo   NEXT STEPS
echo ================================================================================
echo.
echo   1. Review organized files in BOTWAVE_ORGANIZED folder
echo   2. Check BOTWAVE_REVIEW folder for flagged executables
echo   3. Delete organized folders when done reviewing
echo   4. Contact Botwave Support for assistance: support@botwave.ai
echo.
echo ================================================================================
echo              Botwave - Professional IT Automation
echo              www.botwave.ai | support@botwave.ai
echo ================================================================================
) > "%REPORT_FILE%"

copy "%REPORT_FILE%" "%REVIEW_FOLDER%\README.txt" >nul 2>&1

echo   Report saved to Desktop
echo.

:: Completion
echo ================================================================================
echo                    CLEANUP COMPLETE!
echo ================================================================================
echo.
echo   Files organized:  !PDF_COUNT! PDFs, !PHOTO_COUNT! images, !DOC_COUNT! docs
echo   Files flagged:    !SUSPICIOUS_COUNT!
echo.
echo   Check your Desktop for:
echo.
echo     [BOTWAVE_REVIEW_...]     - Review flagged files here
echo     [BOTWAVE_ORGANIZED_...]  - Organized file copies
echo     [BOTWAVE_CLEANUP_...txt] - Full report
echo.
echo   Questions? Visit: www.botwave.ai/support
echo.
echo ================================================================================
echo.
pause

start explorer "%REVIEW_FOLDER%"
start explorer "%ORGANIZED%"

endlocal
