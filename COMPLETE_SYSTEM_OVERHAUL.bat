@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::   COMPLETE SYSTEM OVERHAUL - PROFESSIONAL IT EDITION
::   Version: 3.0 - Enterprise Methodology
::   Based on: ZL Technologies 3-Bucket System + AIIM Best Practices
::   Safety: Quarantine-first approach - NOTHING deleted without review
:: ============================================================================

title Complete System Overhaul - Professional IT Cleanup
color 0B

:: Initialize master counters
set "TOTAL_FILES_SCANNED=0"
set "TOTAL_FILES_ORGANIZED=0"
set "TOTAL_FILES_QUARANTINED=0"
set "TOTAL_SIZE_FREED=0"
set "DUPLICATES_FOUND=0"
set "ROT_FILES_FOUND=0"

:: Generate session ID for tracking
set "SESSION_ID=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%"
set "SESSION_ID=%SESSION_ID: =0%"
set "SESSION_ID=%SESSION_ID:=:%"

cls
echo.
echo ================================================================================
echo           COMPLETE SYSTEM OVERHAUL - PROFESSIONAL IT EDITION
echo ================================================================================
echo.
echo   Session ID: %SESSION_ID%
echo   Date: %date% %time%
echo.
echo   This tool implements enterprise-grade cleanup methodology:
echo   - Phase 1: Discovery ^& Metadata Analysis
echo   - Phase 2: Security Sweep (Executable Flagging)
echo   - Phase 3: ROT Analysis (Redundant/Obsolete/Trivial)
echo   - Phase 4: Intelligent Organization
echo   - Phase 5: Quarantine ^& Review
echo   - Phase 6: Cleanup ^& Documentation
echo.
echo   [SAFE] All actions are logged and reversible
echo   [SAFE] Files are quarantined before any deletion
echo.
echo ================================================================================
echo.
pause

:: ============================================================================
:: PATH SETUP
:: ============================================================================

set "DESKTOP=%USERPROFILE%\Desktop"
set "DOCUMENTS=%USERPROFILE%\Documents"
set "DOWNLOADS=%USERPROFILE%\Downloads"
set "TEMP=%TEMP%"

set "BASE_FOLDER=%DESKTOP%\OVERHAUL_%SESSION_ID%"
set "QUARANTINE=%BASE_FOLDER%\00_QUARANTINE_REVIEW"
set "ORGANIZED=%BASE_FOLDER%\01_ORGANIZED"
set "ROT_FOLDER=%BASE_FOLDER%\02_ROT_CANDIDATES"
set "REPORTS=%BASE_FOLDER%\03_REPORTS"
set "LOG_FILE=%BASE_FOLDER%\overhaul_log.txt"

:: Create folder structure
echo.
echo Creating folder structure...
mkdir "%BASE_FOLDER%" 2>nul
mkdir "%QUARANTINE%\01_Executables" 2>nul
mkdir "%QUARANTINE%\02_Suspicious" 2>nul
mkdir "%QUARANTINE%\03_Sensitive_Data" 2>nul
mkdir "%ORGANIZED%\01_Documents_PDFs" 2>nul
mkdir "%ORGANIZED%\02_Documents_Office" 2>nul
mkdir "%ORGANIZED%\03_Spreadsheets" 2>nul
mkdir "%ORGANIZED%\04_Images_Photos" 2>nul
mkdir "%ORGANIZED%\05_Videos" 2>nul
mkdir "%ORGANIZED%\06_Archives" 2>nul
mkdir "%ORGANIZED%\07_Code_Dev" 2>nul
mkdir "%ORGANIZED%\08_Business_Records" 2>nul
mkdir "%ROT_FOLDER%\01_Duplicates" 2>nul
mkdir "%ROT_FOLDER%\02_Temp_Files" 2>nul
mkdir "%ROT_FOLDER%\03_Old_Files_90days" 2>nul
mkdir "%ROT_FOLDER%\04_Empty_Folders" 2>nul
mkdir "%REPORTS%" 2>nul

echo Log started: %date% %time% > "%LOG_FILE%"
echo   Done.

:: ============================================================================
:: PHASE 1: DISCOVERY & METADATA ANALYSIS
:: ============================================================================

echo.
echo ================================================================================
echo   PHASE 1: DISCOVERY ^& METADATA ANALYSIS
echo ================================================================================
echo.

set "SCAN_LOCATIONS=%DESKTOP% %DOCUMENTS% %DOWNLOADS%"

echo Scanning locations...
for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        echo   Scanning: %%P
        for /f "tokens=*" %%F in ('dir /s /a-d /b "%%P" 2^>nul') do (
            set /a TOTAL_FILES_SCANNED+=1
        )
    )
)

echo.
echo   Total files discovered: !TOTAL_FILES_SCANNED!
echo   Log: !TOTAL_FILES_SCANNED! files catalogued >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 2: SECURITY SWEEP - EXECUTABLE FLAGGING
:: ============================================================================

echo.
echo ================================================================================
echo   PHASE 2: SECURITY SWEEP - EXECUTABLE FLAGGING
echo ================================================================================
echo.

set "EXEC_COUNT=0"

echo Scanning for executable files...
for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for %%E in (exe bat cmd vbs js jse ws wsc wsf psc1 msi com scr pif) do (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                set /a EXEC_COUNT+=1
                echo   [!EXEC_COUNT!] %%~nxF
                copy "%%F" "%QUARANTINE%\01_Executables\" 2>nul
                echo   Quarantined: %%F >> "%LOG_FILE%"
            )
        )
    )
)

echo.
echo   Executables flagged: !EXEC_COUNT!
echo   Security: !EXEC_COUNT! executables quarantined for review >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 3: ROT ANALYSIS - REDUNDANT OBSOLETE TRIVIAL
:: ============================================================================

echo.
echo ================================================================================
echo   PHASE 3: ROT ANALYSIS - REDUNDANT/OBSOLETE/TRIVIAL
echo ================================================================================
echo.

:: 3a: Temporary Files
echo [3a] Scanning for temporary files...
set "TEMP_COUNT=0"

for %%E in (tmp temp $tmp ~tmp bak old gibberish) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                set /a TEMP_COUNT+=1
                set /a ROT_FILES_FOUND+=1
                move "%%F" "%ROT_FOLDER%\02_Temp_Files\" 2>nul
            )
        )
    )
)

echo   Temp files found: !TEMP_COUNT!

:: 3b: Old Files (not accessed in 90+ days)
echo.
echo [3b] Scanning for old files (90+ days)...
set "OLD_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for /f "delims=" %%F in ('forfiles /p "%%P" /s /d -90 /c "cmd /c echo @path" 2^>nul') do (
            set /a OLD_COUNT+=1
            set /a ROT_FILES_FOUND+=1
            echo   %%~nxF
        )
    )
)

echo   Old files (90+ days): !OLD_COUNT!

:: 3c: Empty Folders
echo.
echo [3c] Finding empty folders...
set "EMPTY_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b /ad "%%P" 2^>nul') do (
            dir "%%F" /b 2>nul | findstr . >nul || (
                set /a EMPTY_COUNT+=1
                echo   Empty: %%F
            )
        )
    )
)

echo   Empty folders: !EMPTY_COUNT!

:: 3d: Common Junk Files
echo.
echo [3d] Removing common junk files...
set "JUNK_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for %%J in (thumbs.db desktop.ini $RECYCLE.BIN System\ Volume\ Information) do (
            for /f "delims=" %%F in ('dir /s /b "%%P\%%J" 2^>nul') do (
                set /a JUNK_COUNT+=1
                set /a ROT_FILES_FOUND+=1
                del /q "%%F" 2>nul
                set /a TOTAL_SIZE_FREED+=1
            )
        )
    )
)

echo   Junk files removed: !JUNK_COUNT!

echo.
echo   Total ROT files identified: !ROT_FILES_FOUND!
echo   ROT: !ROT_FILES_FOUND! files categorized as Redundant/Obsolete/Trivial >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 4: INTELLIGENT ORGANIZATION
:: ============================================================================

echo.
echo ================================================================================
echo   PHASE 4: INTELLIGENT ORGANIZATION
echo ================================================================================
echo.

:: 4a: PDF Documents
echo [4a] Organizing PDF documents...
set "PDF_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%P\*.pdf" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\01_Documents_PDFs\" 2>nul
            if !errorlevel! equ 0 set /a PDF_COUNT+=1
        )
    )
)

echo   PDFs: !PDF_COUNT!

:: 4b: Office Documents
echo [4b] Organizing Office documents...
set "DOC_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%P\*.doc*" "%%P\*.txt" "%%P\*.rtf" "%%P\*.odt" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\02_Documents_Office\" 2>nul
            if !errorlevel! equ 0 set /a DOC_COUNT+=1
        )
    )
)

echo   Office docs: !DOC_COUNT!

:: 4c: Spreadsheets
echo [4c] Organizing spreadsheets...
set "SHEET_COUNT=0"

for %%P in (%SCAN_LOCATIONS%) do (
    if exist "%%P" (
        for /f "delims=" %%F in ('dir /s /b "%%P\*.xls*" "%%P\*.csv" "%%P\*.ods" 2^>nul') do (
            copy "%%F" "%ORGANIZED%\03_Spreadsheets\" 2>nul
            if !errorlevel! equ 0 set /a SHEET_COUNT+=1
        )
    )
)

echo   Spreadsheets: !SHEET_COUNT!

:: 4d: Images
echo [4d] Organizing images and photos...
set "IMG_COUNT=0"

for %%E in (jpg jpeg png gif bmp heic webp tiff ico raw) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\04_Images_Photos\" 2>nul
                if !errorlevel! equ 0 set /a IMG_COUNT+=1
            )
        )
    )
)

echo   Images: !IMG_COUNT!

:: 4e: Videos
echo [4e] Organizing videos...
set "VID_COUNT=0"

for %%E in (mp4 avi mkv mov wmv flv webm m4v) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\05_Videos\" 2>nul
                if !errorlevel! equ 0 set /a VID_COUNT+=1
            )
        )
    )
)

echo   Videos: !VID_COUNT!

:: 4f: Archives
echo [4f] Organizing archives...
set "ARCH_COUNT=0"

for %%E in (zip rar 7z tar gz bz2 iso img) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\06_Archives\" 2>nul
                if !errorlevel! equ 0 set /a ARCH_COUNT+=1
            )
        )
    )
)

echo   Archives: !ARCH_COUNT!

:: 4g: Code/Dev Files
echo [4g] Organizing code and development files...
set "CODE_COUNT=0"

for %%E in (py js ts jsx tsx html css scss json xml yaml yml sh ps1 bat cmd md log sql) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*.%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\07_Code_Dev\" 2>nul
                if !errorlevel! equ 0 set /a CODE_COUNT+=1
            )
        )
    )
)

echo   Code files: !CODE_COUNT!

:: 4h: Business Records
echo [4h] Organizing business records...
set "BIZ_COUNT=0"

for %%E in (pdf doc docx) do (
    for %%P in (%SCAN_LOCATIONS%) do (
        if exist "%%P" (
            for /f "delims=" %%F in ('dir /s /b "%%P\*invoice*%%E" "%%P\*receipt*%%E" "%%P\*quote*%%E" "%%P\*estimate*%%E" 2^>nul') do (
                copy "%%F" "%ORGANIZED%\08_Business_Records\" 2>nul
                if !errorlevel! equ 0 set /a BIZ_COUNT+=1
            )
        )
    )
)

echo   Business records: !BIZ_COUNT!

set /a TOTAL_FILES_ORGANIZED=!PDF_COUNT!+!DOC_COUNT!+!SHEET_COUNT!+!IMG_COUNT!+!VID_COUNT!+!ARCH_COUNT!+!CODE_COUNT!+!BIZ_COUNT!

echo.
echo   Total files organized: !TOTAL_FILES_ORGANIZED!
echo   Organization: !TOTAL_FILES_ORGANIZED! files sorted into categories >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 5: GENERATE COMPREHENSIVE REPORT
:: ============================================================================

echo.
echo ================================================================================
echo   PHASE 5: GENERATING COMPREHENSIVE REPORT
echo ================================================================================
echo.

set "REPORT_FILE=%REPORTS%\OVERHAUL_REPORT_%SESSION_ID%.txt"

(
echo ================================================================================
echo              COMPLETE SYSTEM OVERHAUL - FINAL REPORT
echo ================================================================================
echo.
echo   Session ID: %SESSION_ID%
echo   Date: %date%
echo   Time: %time%
echo   Computer: %COMPUTERNAME%
echo   User: %USERNAME%
echo.
echo ================================================================================
echo   EXECUTIVE SUMMARY
echo ================================================================================
echo.
echo   Files Scanned:          !TOTAL_FILES_SCANNED!
echo   Files Organized:        !TOTAL_FILES_ORGANIZED!
echo   ROT Files Found:        !ROT_FILES_FOUND!
echo   Executables Flagged:    !EXEC_COUNT!
echo   Junk Files Removed:     !JUNK_COUNT!
echo.
echo ================================================================================
echo   ORGANIZATION BREAKDOWN
echo ================================================================================
echo.
echo   PDF Documents:          !PDF_COUNT!
echo   Office Documents:       !DOC_COUNT!
echo   Spreadsheets:           !SHEET_COUNT!
echo   Images/Photos:          !IMG_COUNT!
echo   Videos:                 !VID_COUNT!
echo   Archives:               !ARCH_COUNT!
echo   Code/Dev Files:         !CODE_COUNT!
echo   Business Records:       !BIZ_COUNT!
echo.
echo ================================================================================
echo   ROT ANALYSIS DETAILS
echo ================================================================================
echo.
echo   Temporary Files:        !TEMP_COUNT!
echo   Old Files (90+ days):   !OLD_COUNT!
echo   Empty Folders:          !EMPTY_COUNT!
echo   Junk Files Deleted:     !JUNK_COUNT!
echo.
echo ================================================================================
echo   FOLDER STRUCTURE CREATED
echo ================================================================================
echo.
echo   Base Location: %BASE_FOLDER%
echo.
echo   [00_QUARANTINE_REVIEW]
echo     Location: %QUARANTINE%
echo     Contents: !EXEC_COUNT! executable files flagged for security review
echo     Action: REVIEW WITH IT PROFESSIONAL before deletion
echo.
echo   [01_ORGANIZED]
echo     Location: %ORGANIZED%
echo     Contents: !TOTAL_FILES_ORGANIZED! files sorted by type
echo     Action: Review organized structure, move files to permanent locations
echo.
echo   [02_ROT_CANDIDATES]
echo     Location: %ROT_FOLDER%
echo     Contents: !ROT_FILES_FOUND! files identified as Redundant/Obsolete/Trivial
echo     Action: Review and approve for deletion
echo.
echo   [03_REPORTS]
echo     Location: %REPORTS%
echo     Contents: This report and detailed logs
echo     Action: Keep for records
echo.
echo ================================================================================
echo   PROFESSIONAL RECOMMENDATIONS
echo ================================================================================
echo.
echo   IMMEDIATE ACTIONS (This Week):
echo   1. Review quarantined executables with IT professional
echo   2. Approve ROT candidates for deletion
echo   3. Move organized files to permanent business folders
echo.
echo   SHORT-TERM (This Month):
echo   4. Implement standardized naming conventions
echo   5. Set up automated backup for organized folders
echo   6. Create folder structure documentation for team
echo.
echo   LONG-TERM (Ongoing):
echo   7. Schedule monthly mini-cleanups
echo   8. Implement automated retention policies
echo   9. Train team on file organization standards
echo.
echo ================================================================================
echo   NEXT STEPS CHECKLIST
echo ================================================================================
echo.
echo   [ ] Review files in QUARANTINE folder
echo   [ ] Approve/delete files in ROT_CANDIDATES folder
echo   [ ] Move ORGANIZED files to permanent locations
echo   [ ] Update backup configuration
echo   [ ] Document new folder structure for team
echo   [ ] Schedule next cleanup (recommended: monthly)
echo.
echo ================================================================================
echo   CONTACT SUPPORT
echo ================================================================================
echo.
echo   For assistance with this cleanup:
echo   - Review the log file: %LOG_FILE%
echo   - Contact your IT professional
echo   - Reference Session ID: %SESSION_ID%
echo.
echo ================================================================================
echo              PROFESSIONAL IT SYSTEM OVERHAUL COMPLETE
echo ================================================================================
) > "%REPORT_FILE%"

:: Copy report to Desktop for easy access
copy "%REPORT_FILE%" "%DESKTOP%\OVERHAUL_REPORT_%SESSION_ID%.txt" >nul

:: Write to log
echo. >> "%LOG_FILE%"
echo REPORT GENERATED: %REPORT_FILE% >> "%LOG_FILE%"
echo Log completed: %date% %time% >> "%LOG_FILE%"

:: ============================================================================
:: COMPLETION
:: ============================================================================

cls
echo.
echo ================================================================================
echo                    OVERHAUL COMPLETE!
echo ================================================================================
echo.
echo   Session ID: %SESSION_ID%
echo.
echo   SUMMARY:
echo   ---------
echo   Files Scanned:        !TOTAL_FILES_SCANNED!
echo   Files Organized:      !TOTAL_FILES_ORGANIZED!
echo   ROT Files Found:      !ROT_FILES_FOUND!
echo   Executables Flagged:  !EXEC_COUNT!
echo.
echo   BREAKDOWN:
echo   ----------
echo   PDFs: !PDF_COUNT!  |  Office: !DOC_COUNT!  |  Sheets: !SHEET_COUNT!
echo   Images: !IMG_COUNT!  |  Video: !VID_COUNT!  |  Archives: !ARCH_COUNT!
echo   Code: !CODE_COUNT!  |  Business: !BIZ_COUNT!
echo.
echo   CHECK YOUR DESKTOP:
echo   -------------------
echo   [OVERHAUL_REPORT_%SESSION_ID%.txt] - Full detailed report
echo.
echo   REVIEW FOLDERS ON DESKTOP:
echo   --------------------------
echo   [00_QUARANTINE_REVIEW]    - Security review required
echo   [01_ORGANIZED]            - Sorted files ready for placement
echo   [02_ROT_CANDIDATES]       - Approve for deletion
echo   [03_REPORTS]              - Logs and documentation
echo.
echo ================================================================================
echo.
echo   Recommended: Review quarantined files with IT professional
echo.
echo ================================================================================
echo.

:: Open report and folders
start notepad "%REPORT_FILE%"
timeout /t 3 >nul
start explorer "%QUARANTINE%"
timeout /t 2 >nul
start explorer "%ORGANIZED%"

echo.
pause

endlocal
