@echo off
echo ------------------------------------------
echo 🧼 Cleaning previous build...
echo ------------------------------------------
rmdir /s /q build
rmdir /s /q dist

echo ------------------------------------------
echo 🔨 Building Chromium Updater GUI (.exe)...
echo ------------------------------------------

pyinstaller main_gui.spec

echo.
echo ✅ Build complete! Check the 'dist' folder.
pause
