@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::   JIMENEZ PLUMBING - PROFESSIONAL COMPUTER CLEANUP
::   Version: 2.0
::   Created: For professional business file organization
::   Safety: NOTHING IS DELETED - files are only copied/moved to review folders
:: ============================================================================

title Jimenez Plumbing - Computer Cleanup
color 0A

:: Initialize counters
set "FILES_SCANNED=0"
set "FILES_ORGANIZED=0"
set "FILES_FLAGGED=0"

cls
echo.
echo ================================================================================
echo              JIMENEZ PLUMBING - COMPUTER CLEANUP
echo ================================================================================
echo.
echo   This tool organizes your computer files safely.
echo.
echo   [IMPORTANT] NOTHING WILL BE DELETED!
echo   Files are only copied to organized folders for review.
echo.
echo ================================================================================
echo.
pause
echo.

:: ============================================================================
:: SETUP PATHS
:: ============================================================================

set "DESKTOP=%USERPROFILE%\Desktop"
set "DOCUMENTS=%USERPROFILE%\Documents"
set "REVIEW_FOLDER=%DESKTOP%\FILES_TO_REVIEW_%date:~-4,4%%date:~-10,2%%date:~-7,2%"
set "ORGANIZED=%DESKTOP%\ORGANIZED_FILES_%date:~-4,4%%date:~-10,2%%date:~-7,2%"

:: Validate desktop path exists
if not exist "%DESKTOP%" (
    echo ERROR: Could not find Desktop folder!
    echo Path: %DESKTOP%
    pause
    exit /b 1
)

:: ============================================================================
:: STEP 1: Create folder structure
:: ============================================================================

echo Step 1: Creating organization folders...

mkdir "%REVIEW_FOLDER%" 2>nul
if errorlevel 1 (
    echo Warning: Could not create review folder
)

mkdir "%ORGANIZED%\01-PDFs_and_Documents" 2>nul
mkdir "%ORGANIZED%\02-Job_Photos" 2>nul
mkdir "%ORGANIZED%\03-Spreadsheets" 2>nul
mkdir "%ORGANIZED%\04-Archives" 2>nul
mkdir "%ORGANIZED%\05-Other_Files" 2>nul

echo   Done.
echo.

:: ============================================================================
:: STEP 2: Scan for suspicious files
:: ============================================================================

echo Step 2: Scanning for potentially risky files...
set "SUSPICIOUS_COUNT=0"

:: Check common download locations for executables
set "SCAN_PATHS=%USERPROFILE%\Downloads %DESKTOP% %TEMP%"

for %%P in (%SCAN_PATHS%) do (
    if exist "%%P" (
        for %%E in (exe bat cmd vbs js scr) do (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                set /a SUSPICIOUS_COUNT+=1
                echo   [!SUSPICIOUS_COUNT!] Found: %%~nxF
                copy "%%F" "%REVIEW_FOLDER%\FLAGGED_%%~nxF" >nul 2>&1
            )
        )
    )
)

if !SUSPICIOUS_COUNT! gtr 0 (
    echo   [!SUSPICIOUS_COUNT!] files flagged for review
) else (
    echo   No suspicious files found
)
echo.

:: ============================================================================
:: STEP 3: Organize PDFs
:: ============================================================================

echo Step 3: Organizing PDF documents...
set "PDF_COUNT=0"

for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.pdf" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\01-PDFs_and_Documents\" >nul 2>&1
            if !errorlevel! equ 0 (
                set /a PDF_COUNT+=1
            )
        )
    )
)

echo   PDFs organized: !PDF_COUNT!
echo.

:: ============================================================================
:: STEP 4: Organize Photos
:: ============================================================================

echo Step 4: Organizing photos...
set "PHOTO_COUNT=0"

for %%E in (jpg jpeg png gif bmp heic webp) do (
    for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%~P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\02-Job_Photos\" >nul 2>&1
                if !errorlevel! equ 0 (
                    set /a PHOTO_COUNT+=1
                )
            )
        )
    )
)

echo   Photos organized: !PHOTO_COUNT!
echo.

:: ============================================================================
:: STEP 5: Organize Documents
:: ============================================================================

echo Step 5: Organizing documents...
set "DOC_COUNT=0"
set "SHEET_COUNT=0"

for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.doc*" "%%~P\*.txt" "%%~P\*.rtf" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\01-PDFs_and_Documents\" >nul 2>&1
            if !errorlevel! equ 0 (
                set /a DOC_COUNT+=1
            )
        )
        for /f "delims=" %%F in ('dir /s /b "%%~P\*.xls*" "%%~P\*.csv" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\03-Spreadsheets\" >nul 2>&1
            if !errorlevel! equ 0 (
                set /a SHEET_COUNT+=1
            )
        )
    )
)

echo   Documents: !DOC_COUNT!  Spreadsheets: !SHEET_COUNT!
echo.

:: ============================================================================
:: STEP 6: Organize Archives
:: ============================================================================

echo Step 6: Organizing archive files...
set "ARCHIVE_COUNT=0"

for %%E in (zip rar 7z tar gz) do (
    for %%P in ("%USERPROFILE%\Downloads" "%DESKTOP%") do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%~P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\04-Archives\" >nul 2>&1
                if !errorlevel! equ 0 (
                    set /a ARCHIVE_COUNT+=1
                )
            )
        )
    )
)

echo   Archives organized: !ARCHIVE_COUNT!
echo.

:: ============================================================================
:: STEP 7: Create Report
:: ============================================================================

echo Step 7: Creating report...

set "REPORT_FILE=%DESKTOP%\CLEANUP_REPORT_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

(
echo ================================================================================
echo                    JIMENEZ PLUMBING - CLEANUP REPORT
echo ================================================================================
echo.
echo   Date: %date% %time%
echo   Computer: %COMPUTERNAME%
echo   User: %USERNAME%
echo.
echo ================================================================================
echo   SUMMARY
echo ================================================================================
echo.
echo   PDF Documents:       !PDF_COUNT!
echo   Photos:              !PHOTO_COUNT!
echo   Word Documents:      !DOC_COUNT!
echo   Spreadsheets:        !SHEET_COUNT!
echo   Archives:            !ARCHIVE_COUNT!
echo   Files Flagged:       !SUSPICIOUS_COUNT!
echo.
echo ================================================================================
echo   FOLDERS CREATED ON YOUR DESKTOP
echo ================================================================================
echo.
echo   [REVIEW_FOLDER]
echo   Location: %REVIEW_FOLDER%
echo   Contains: Potentially risky files for your review
echo   Action: Show this folder to your son before deleting anything
echo.
echo   [ORGANIZED_FILES]
echo   Location: %ORGANIZED%
echo   Contains: Copies of your files, organized by type
echo   Action: Review these copies, then delete the folder when done
echo.
echo ================================================================================
echo   IMPORTANT NOTES
echo ================================================================================
echo.
echo   * NO FILES WERE DELETED FROM YOUR COMPUTER
echo   * Original files remain in their original locations
echo   * These are COPIES for your review and organization
echo   * After review, you can safely delete the organized folders
echo.
echo ================================================================================
echo   NEXT STEPS
echo ================================================================================
echo.
echo   1. Review the FILES_TO_REVIEW folder with your son
echo   2. Check the organized files in ORGANIZED_FILES
echo   3. Delete the ORGANIZED_FILES folder when done reviewing
echo   4. Keep the FILES_TO_REVIEW folder until approved for deletion
echo.
echo ================================================================================
echo              Jimenez Plumbing - Professional IT Services
echo ================================================================================
) > "%REPORT_FILE%"

:: Create README in review folder
copy "%REPORT_FILE%" "%REVIEW_FOLDER%\README.txt" >nul 2>&1

echo   Report saved to Desktop
echo.

:: ============================================================================
:: COMPLETION
:: ============================================================================

cls
echo.
echo ================================================================================
echo                    CLEANUP COMPLETE!
echo ================================================================================
echo.
echo   Files organized:  !PDF_COUNT! PDFs, !PHOTO_COUNT! photos, !DOC_COUNT! docs
echo   Files flagged:    !SUSPICIOUS_COUNT!
echo.
echo   Check your Desktop for:
echo.
echo     [FILES_TO_REVIEW_...]    - Review with your son
echo     [ORGANIZED_FILES_...]    - Organized copies
echo     [CLEANUP_REPORT_...txt]  - Full report
echo.
echo ================================================================================
echo.
pause

:: Open folders for review
start explorer "%REVIEW_FOLDER%"
start explorer "%ORGANIZED%"

endlocal
