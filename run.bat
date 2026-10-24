@echo off
setlocal enabledelayedexpansion
title YouTube Video ^& Music Downloader

:: ================================================================================
:: 1. Check if Python is already accessible in PATH
:: ================================================================================
where python.exe >nul 2>&1
if %errorlevel% equ 0 (
    python "%~dp0downloader.py" %*
    goto :end
)

:: ================================================================================
:: 2. Check standard Windows user installation folders
:: ================================================================================
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" "%~dp0downloader.py" %*
    goto :end
)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%~dp0downloader.py" %*
    goto :end
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%~dp0downloader.py" %*
    goto :end
)
if exist "%ProgramFiles%\Python312\python.exe" (
    "%ProgramFiles%\Python312\python.exe" "%~dp0downloader.py" %*
    goto :end
)
if exist "%ProgramFiles%\Python313\python.exe" (
    "%ProgramFiles%\Python313\python.exe" "%~dp0downloader.py" %*
    goto :end
)

:: ================================================================================
:: 3. Python is not installed -> Automatically download & install it
:: ================================================================================
echo ================================================================================
echo               PYTHON NOT DETECTED - AUTOMATIC INSTALLER
echo ================================================================================
echo [*] Python was not found on this system.
echo [*] Downloading and installing Python for Windows automatically...
echo [*] Please wait a moment while setup completes...
echo ================================================================================

set "PYTHON_INSTALLED=0"

:: Attempt 1: winget (Windows 10/11 default package manager)
where winget.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Installing Python via Windows Package Manager (winget)...
    winget install -e --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements >nul 2>&1
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_INSTALLED=1"
        set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

:: Attempt 2: Direct download from python.org via PowerShell (universal fallback)
if "%PYTHON_INSTALLED%"=="0" (
    echo [*] Downloading official Python installer from python.org...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$url = 'https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe';" ^
        "$out = Join-Path $env:TEMP 'python_setup.exe';" ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
        "Write-Host ' [*] Downloading installer (approx. 25 MB)...';" ^
        "(New-Object System.Net.WebClient).DownloadFile($url, $out);" ^
        "Write-Host ' [*] Running silent installation (user space, no admin needed)...';" ^
        "Start-Process -FilePath $out -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0' -Wait;" ^
        "Remove-Item -Path $out -Force -ErrorAction SilentlyContinue"

    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_INSTALLED=1"
        set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

:: ================================================================================
:: 4. Verify installation and launch
:: ================================================================================
where python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] Python installed successfully! Launching downloader...
    python "%~dp0downloader.py" %*
    goto :end
)

if defined PY_BIN (
    if exist "!PY_BIN!" (
        echo [+] Python installed successfully! Launching downloader...
        "!PY_BIN!" "%~dp0downloader.py" %*
        goto :end
    )
)

echo [!] Could not automatically install Python. Please install Python manually from https://www.python.org/
pause

:end
