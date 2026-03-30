@echo off
title Jimenez Plumbing - Computer Setup
color 0E

:: ============================================================================
::   START HERE - JIMENEZ PLUMBING COMPUTER SETUP
::   Your son made this for you
:: ============================================================================

cls
echo.
echo ================================================================================
echo              WELCOME - JIMENEZ PLUMBING COMPUTER SETUP
echo ================================================================================
echo.
echo   Your son set up this computer to run like a proper business.
echo.
echo   You have TWO tools to keep this computer running perfect:
echo.
echo ================================================================================
echo.
echo   1. INITIAL SETUP (Run this once)
echo      "jimenez_plumbing_laptop_overhaul.bat"
echo.
echo      Use this when the computer is messy and slow.
echo      This organizes everything and makes it fast.
echo.
echo      >>> RUN THIS FIRST if computer is a mess <<<
echo.
echo.
echo   2. MONTHLY MAINTENANCE (Run every few months)
echo      "MONTHLY MAINTENANCE.bat"
echo.
echo      Use this to keep the computer clean and fast.
echo      Takes 2 minutes. Run it every 2-3 months.
echo.
echo      >>> RUN THIS EVERY FEW MONTHS <<<
echo.
echo ================================================================================
echo.
echo   Which one do you want to run?
echo.
echo   Press 1 for INITIAL SETUP (big cleanup)
echo   Press 2 for MONTHLY MAINTENANCE (quick cleanup)
echo   Press 3 to just read the instructions
echo.
set /p CHOICE="Your choice (1, 2, or 3): "

if "%CHOICE%"=="1" (
    cls
    echo.
    echo   Starting INITIAL SETUP...
    echo.
    echo   This will organize your entire computer.
    echo   Nothing will be deleted permanently.
    echo.
    pause
    call "jimenez_plumbing_laptop_overhaul.bat"
) else if "%CHOICE%"=="2" (
    cls
    echo.
    echo   Starting MONTHLY MAINTENANCE...
    echo.
    pause
    call "MONTHLY MAINTENANCE.bat"
) else if "%CHOICE%"=="3" (
    cls
    notepad "START_HERE_READ_THIS.txt"
) else (
    echo.
    echo   Invalid choice. Run this again and pick 1, 2, or 3.
    echo.
    pause
)
