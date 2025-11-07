# Autodesk Hardware Scanner

Tool kiểm tra phần cứng máy tính có đáp ứng yêu cầu để chạy các phần mềm Autodesk (Revit, AutoCAD, Inventor).

## 📚 Tài liệu

- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Hướng dẫn chi tiết đóng gói EXE cho developer
- **[INSTALL.md](INSTALL.md)** - Hướng dẫn cài đặt và sử dụng cho người dùng cuối

## 🚀 Quick Start (Developer)

### Yêu cầu
- Windows 10/11 64-bit
- Python 3.10 hoặc 3.11 (khuyến nghị, không dùng 3.13)
- PowerShell (chạy Run as Administrator)

### Cài đặt
```bash
pip install -r requirements.txt
```

### Chạy thử
```bash
python -m scanner.main --product revit --version 2025 --out out
```

### Đóng gói EXE
```bash
# Cách 1: Dùng script tự động (KHUYẾN NGHỊ)
build.bat

# Cách 2: Build thủ công
python -m PyInstaller build.spec --clean
```

File EXE sẽ nằm ở: `dist\AutodeskHWScanner.exe`

### Chạy EXE (CLI và GUI)
```bash
# Chế độ GUI (mới):
.\dist\AutodeskHWScanner.exe --gui

# Chế độ CLI cũ:
.\dist\AutodeskHWScanner.exe --product revit --version 2025 --out out
```

### Chạy từ mã nguồn với GUI
```bash
python -m scanner.main --gui
```

## 📋 Kết quả

Sau khi chạy, bạn sẽ nhận được:
- `{product}_{version}_facts_and_result.json` - Dữ liệu JSON đầy đủ
- `{product}_{version}_report.html` - Báo cáo HTML đẹp mắt
- Cửa sổ popup tự động hiển thị báo cáo

## ⚙️ Cập nhật quy tắc

Sửa các file JSON trong `scanner/rules/*.json` theo yêu cầu phần cứng của Autodesk.

## 📝 Ghi chú

- Xem [BUILD_GUIDE.md](BUILD_GUIDE.md) để biết chi tiết về build và xử lý lỗi
- Xem [INSTALL.md](INSTALL.md) để biết cách sử dụng cho người dùng cuối
