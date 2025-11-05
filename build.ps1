# Build script cho Autodesk Hardware Scanner (PowerShell)
# Yêu cầu: Python 3.10+ đã cài pip và pyinstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Autodesk Hardware Scanner - Build EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Chuyển vào thư mục script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Tìm Python - thử nhiều đường dẫn
Write-Host "[INFO] Đang tìm Python..." -ForegroundColor Yellow
$pythonCmd = $null

# Thử tìm trong PATH
try {
    $null = Get-Command python -ErrorAction Stop
    $pythonCmd = "python"
} catch {
    # Thử các đường dẫn thông thường
    $pythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Python313\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            $pythonCmd = $path
            break
        }
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "[ERROR] Python không được tìm thấy!" -ForegroundColor Red
    Write-Host "Vui lòng cài Python 3.10+ hoặc thêm Python vào PATH" -ForegroundColor Yellow
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

Write-Host "[OK] Tìm thấy Python: $pythonCmd" -ForegroundColor Green

# Kiểm tra Python
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Không thể chạy Python!" -ForegroundColor Red
    Read-Host "Nhấn Enter để thoát"
    exit 1
}

# Kiểm tra PyInstaller
Write-Host "[INFO] Đang kiểm tra PyInstaller..." -ForegroundColor Yellow
try {
    $null = & $pythonCmd -m PyInstaller --version 2>&1
    Write-Host "[OK] PyInstaller đã được cài đặt" -ForegroundColor Green
} catch {
    Write-Host "[INFO] PyInstaller chưa được cài. Đang cài đặt..." -ForegroundColor Yellow
    & $pythonCmd -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Không thể cài PyInstaller!" -ForegroundColor Red
        Read-Host "Nhấn Enter để thoát"
        exit 1
    }
}

Write-Host ""
Write-Host "[INFO] Đang build EXE..." -ForegroundColor Yellow
Write-Host ""

# Build bằng spec file
& $pythonCmd -m PyInstaller build.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Build thất bại!" -ForegroundColor Red
    Read-Host "Nhấn Enter để thoát"
    exit 1
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Build thành công!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "File EXE: dist\AutodeskHWScanner.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Cách sử dụng:" -ForegroundColor Yellow
    Write-Host "  .\dist\AutodeskHWScanner.exe --product revit --version 2025 --out out" -ForegroundColor White
    Write-Host ""
}

Read-Host "Nhấn Enter để thoát"

