:: build.bat – Reliable EXE builder for ChroMate using .spec
@echo off
setlocal enabledelayedexpansion

set VERSION=1.0.0
set EXENAME=ChroMate_v%VERSION%

REM ✅ Clean previous build artifacts
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1

REM 🔄 Generate custom .spec file with hooks for plyer notifications
pyi-makespec --noconfirm --onefile --windowed ^
  --icon=chromium_updater_icon.ico ^
  --name "ChroMate" ^
  main_gui.py

REM ✏️ Inject plyer backend manually into spec
REM ⚠️ Only works if plyer installed and platform is Windows
REM This assumes plyer/platforms/win/ exists under site-packages

powershell -Command "(Get-Content ChroMate.spec) -replace '\)\n\n', ',\n    hiddenimports=[\"plyer.platforms.win.notification\"]\n)\n\n' | Set-Content ChroMate.spec"

REM ✨ Build from spec file
pyinstaller ChroMate.spec --clean

echo.
echo ✅ Build complete! Check the 'dist' folder for %EXENAME%.exe
pause

:: End of build.bat
