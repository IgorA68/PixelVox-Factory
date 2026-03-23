@echo off
setlocal

where pyw >nul 2>nul
if %errorlevel%==0 (
	start "" pyw -3 -m vox_art.gui_launcher
	exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
	start "" py -3 -m vox_art.gui_launcher
	exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
	start "" pythonw -m vox_art.gui_launcher
	exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
	start "" python -m vox_art.gui_launcher
	exit /b 0
)

echo Python launcher not found.
echo Install Python 3 and make sure py, pyw, python, or pythonw is available in PATH.
pause
exit /b 1