@echo off
REM Build script cho Autodesk Hardware Scanner
REM Yêu cầu: Python 3.10+ đã cài pip và pyinstaller

echo ========================================
echo Autodesk Hardware Scanner - Build EXE
echo ========================================
echo.

REM Tìm Python - thử nhiều đường dẫn
set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    REM Thử các đường dẫn thông thường
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    ) else if exist "C:\Python313\python.exe" (
        set PYTHON_CMD=C:\Python313\python.exe
    ) else if exist "C:\Python311\python.exe" (
        set PYTHON_CMD=C:\Python311\python.exe
    ) else if exist "C:\Python310\python.exe" (
        set PYTHON_CMD=C:\Python310\python.exe
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set PYTHON_CMD=C:\Program Files\Python311\python.exe
    ) else if exist "C:\Program Files\Python310\python.exe" (
        set PYTHON_CMD=C:\Program Files\Python310\python.exe
    ) else (
        echo [ERROR] Python không được tìm thấy!
        echo Vui lòng cài Python 3.10+ hoặc thêm Python vào PATH
        pause
        exit /b 1
    )
)

REM Kiểm tra Python
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy! Vui lòng cài Python 3.10+
    pause
    exit /b 1
)
echo [OK] Đang dùng Python: %PYTHON_CMD%

REM Kiểm tra PyInstaller
%PYTHON_CMD% -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller chưa được cài. Đang cài đặt...
    %PYTHON_CMD% -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Không thể cài PyInstaller!
        pause
        exit /b 1
    )
)

REM Chuyển vào thư mục script
cd /d "%~dp0"

echo [INFO] Đang build EXE...
echo.

REM Build bằng spec file
%PYTHON_CMD% -m PyInstaller build.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build thất bại!
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo [SUCCESS] Build thành công!
    echo ========================================
    echo File EXE: dist\AutodeskHWScanner.exe
    echo.
    echo Cách sử dụng:
    echo   dist\AutodeskHWScanner.exe --product revit --version 2025 --out out
    echo.
)

pause

