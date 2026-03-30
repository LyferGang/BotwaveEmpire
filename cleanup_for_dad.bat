@echo off
title Jimenez Plumbing - Computer Cleanup
color 0A

:: ============================================================================
::   JIMENEZ PLUMBING - ONE-CLICK COMPUTER CLEANUP
::   Made for people who hate computers
::   Nothing gets deleted - just organized
:: ============================================================================

cls
echo.
echo ================================================================================
echo              JIMENEZ PLUMBING - COMPUTER CLEANUP
echo ================================================================================
echo.
echo   This will organize your computer files.
echo.
echo   IMPORTANT: NOTHING WILL BE DELETED!
echo   Everything just gets sorted into folders.
echo.
echo   Your files are SAFE.
echo.
echo ================================================================================
echo.
pause
echo.

:: Create folders on Desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "REVIEW=%DESKTOP%\FILES_TO_REVIEW"
set "ORGANIZED=%DESKTOP%\ORGANIZED_FILES"

echo Step 1 of 4: Creating folders...
mkdir "%REVIEW%" 2>nul
mkdir "%ORGANIZED%\Invoices_and_Receipts" 2>nul
mkdir "%ORGANIZED\Job_Photos" 2>nul
mkdir "%ORGANIZED\Documents" 2>nul
mkdir "%ORGANIZED\Archives" 2>nul
echo DONE!
echo.

echo Step 2 of 4: Looking for suspicious files...
set /a SUSPICIOUS=0

:: Check for dangerous file types
for %%e in (exe,bat,scr,cmd,com,vbs,js) do (
    for /f "delims=" %%f in ('dir /s /b *.%e% 2^>nul ^| findstr /i /v /c:"%~f0"') do (
        echo   Found: %%f
        copy "%%f" "%REVIEW%\FLAGGED_%%~nf.%%e" >nul 2>&1
        set /a SUSPICIOUS+=1
    )
)
echo   Flagged %SUSPICIOUS% files for review
echo.

echo Step 3 of 4: Organizing your files...
set /a PDFS=0
set /a PHOTOS=0
set /a DOCS=0
set /a ARCHIVES=0

:: Find and copy PDFs
for /f "delims=" %%f in ('dir /s /b *.pdf 2^>nul') do (
    copy "%%f" "%ORGANIZED%\Invoices_and_Receipts\" >nul 2>&1
    set /a PDFS+=1
)

:: Find and copy photos
for %%e in (jpg,jpeg,png,gif,bmp,heic) do (
    for /f "delims=" %%f in ('dir /s /b *.%%e 2^>nul') do (
        copy "%%f" "%ORGANIZED%\Job_Photos\" >nul 2>&1
        set /a PHOTOS+=1
    )
)

:: Find and copy documents
for %%e in (doc,docx,txt,rtf,xls,xlsx) do (
    for /f "delims=" %%f in ('dir /s /b *.%%e 2^>nul') do (
        copy "%%f" "%ORGANIZED%\Documents\" >nul 2>&1
        set /a DOCS+=1
    )
)

:: Find and copy archives
for %%e in (zip,rar,7z) do (
    for /f "delims=" %%f in ('dir /s /b *.%%e 2^>nul') do (
        copy "%%f" "%ORGANIZED%\Archives\" >nul 2>&1
        set /a ARCHIVES+=1
    )
)

echo DONE!
echo.
echo   PDFs and Receipts: %PDFS%
echo   Job Photos: %PHOTOS%
echo   Documents: %DOCS%
echo   Archives: %ARCHIVES%
echo.

echo Step 4 of 4: Writing your report...

:: Create simple report
set "REPORT=%DESKTOP%\CLEANUP_REPORT.txt"
(
echo ================================================================================
echo                 YOUR COMPUTER HAS BEEN ORGANIZED!
echo ================================================================================
echo.
echo Date: %date% %time%
echo.
echo WHAT HAPPENED:
echo --------------
echo Your files have been organized into folders on your Desktop.
echo.
echo Your ORIGINAL files are still where they always were.
echo We just made COPIES and put them in neat folders.
echo.
echo FOLDERS ON YOUR DESKTOP:
echo ------------------------
echo.
echo 1. FILES_TO_REVIEW
echo    - These files might be dangerous
echo    - DO NOT OPEN anything in here
echo    - Show this folder to your son
echo.
echo 2. ORGANIZED_FILES
echo    - Invoices_and_Receipts  (all your PDFs)
echo    - Job_Photos             (all your pictures)
echo    - Documents              (Word docs, spreadsheets)
echo    - Archives               (ZIP files)
echo.
echo IMPORTANT:
echo ----------
echo * NOTHING WAS DELETED
echo * Your originals are safe
echo * These are just COPIES to help you find things
echo.
echo WHAT TO DO NEXT:
echo ----------------
echo 1. Look in ORGANIZED_FILES to find your stuff
echo 2. Show FILES_TO_REVIEW to your son
echo 3. Ask him what's safe to delete
echo.
echo When you're done, you can delete the ORGANIZED_FILES folder.
echo The copies were just to help you see what you have.
echo.
echo ================================================================================
echo              Made by your son - Jimenez Plumbing Automation
echo ================================================================================
) > "%REPORT%"

echo DONE!
echo.

:: Create warning file
(
echo WARNING - READ THIS FIRST!
echo ==========================
echo.
echo This folder has files that might be dangerous.
echo.
echo DO NOT OPEN or DELETE anything in here!
echo.
echo Show this folder to your son first.
echo.
echo He will tell you what's safe.
) > "%REVIEW%\WARNING_READ_FIRST.txt"

:: Open folders for user
explorer "%REVIEW%"
explorer "%ORGANIZED%"
explorer "%DESKTOP%"

cls
echo.
echo ================================================================================
echo                    ALL DONE!
echo ================================================================================
echo.
echo   Check your Desktop for:
echo.
echo     [FILES_TO_REVIEW]      - Files to show your son
echo     [ORGANIZED_FILES]      - Your files, sorted nicely
echo     [CLEANUP_REPORT.txt]   - This report
echo.
echo   Your original files are still where they always were.
echo.
echo   Double-click CLEANUP_REPORT.txt to read more details.
echo.
echo ================================================================================
echo.
echo   Questions? Call your son!
echo.
echo ================================================================================
echo.
pause
