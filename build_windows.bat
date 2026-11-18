@echo off
setlocal
cd /d "%~dp0"

py -3 -m pip install -r requirements-build.txt
if errorlevel 1 (
    echo Failed to install the Windows build dependency.
    exit /b 1
)

py -3 -m PyInstaller --noconfirm --clean --windowed --name ComputerStoreHelpdesk main.py
if errorlevel 1 (
    echo Windows executable build failed.
    exit /b 1
)

echo Build complete: dist\ComputerStoreHelpdesk\ComputerStoreHelpdesk.exe
