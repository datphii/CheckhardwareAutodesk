@echo off
REM Build script đơn giản - yêu cầu bạn chỉ định đường dẫn Python

echo ========================================
echo Autodesk Hardware Scanner - Build EXE
echo ========================================
echo.

REM Thay đổi đường dẫn Python của bạn ở đây
set PYTHON_CMD=C:\Python313\python.exe

REM Hoặc nếu Python có trong PATH, dùng:
REM set PYTHON_CMD=python

REM Kiểm tra Python
if not exist "%PYTHON_CMD%" (
    echo [ERROR] Không tìm thấy Python tại: %PYTHON_CMD%
    echo.
    echo Vui lòng sửa dòng "set PYTHON_CMD=..." trong file này
    echo để trỏ đến đúng đường dẫn python.exe của bạn
    echo.
    echo Ví dụ:
    echo   set PYTHON_CMD=C:\Python311\python.exe
    echo   set PYTHON_CMD=C:\Users\YourName\AppData\Local\Programs\Python\Python313\python.exe
    echo.
    pause
    exit /b 1
)

echo [OK] Đang dùng Python: %PYTHON_CMD%
%PYTHON_CMD% --version

REM Chuyển vào thư mục script
cd /d "%~dp0"

REM Kiểm tra PyInstaller
echo [INFO] Đang kiểm tra PyInstaller...
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

