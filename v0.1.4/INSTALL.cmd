@echo off
setlocal

echo ========================================
echo SpectrumB Installer Bootstrapper
echo ========================================

rem 1) Detect any of python, python3, or py in PATH
set "PY_CMD="
for %%I in (python python3 py) do (
    %%I --version >nul 2>&1 && (
        set "PY_CMD=%%I"
        goto :Found
    )
)

rem 2) If none found, download & install Python 3.12.4
echo No Python found. Downloading Python 3.12.4...
set "PY_VER=3.12.4"
set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"
set "PY_TMP=%TEMP%\python_installer.exe"

curl -L "%PY_URL%" -o "%PY_TMP%" --progress-bar
if not exist "%PY_TMP%" (
    echo ERROR: Download failed.
    pause
    exit /b 1
)

echo Installing Python silently...
"%PY_TMP%" /passive InstallAllUsers=1 PrependPath=1 Include_pip=1
del /f /q "%PY_TMP%"

rem Refresh PATH from registry
for /F "skip=2 tokens=2,*" %%A in ('
    reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
') do set "PATH=%%B"

rem Re-run detection
for %%I in (python python3 py) do (
    %%I --version >nul 2>&1 && (
        set "PY_CMD=%%I"
        goto :Found
    )
)

:Found
if not defined PY_CMD (
    echo ERROR: Python install failed or interpreter not found.
    pause
    exit /b 1
)

echo.
echo Using interpreter: %PY_CMD%
%PY_CMD% --version
echo.

rem 3) Install pip & rarfile
echo Installing/upgrading pip and rarfile...
%PY_CMD% -m ensurepip --upgrade
%PY_CMD% -m pip install --upgrade pip rarfile

rem 4) Launch the GUI
echo.
echo Launching SpectrumB Installer Tool...
pushd "%~dp0"
%PY_CMD% gui.py
popd

endlocal
