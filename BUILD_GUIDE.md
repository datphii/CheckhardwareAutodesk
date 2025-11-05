# Hướng dẫn Đóng gói Autodesk Hardware Scanner

## Yêu cầu hệ thống

- **Windows 10/11** (64-bit)
- **Python 3.10 hoặc 3.11** (khuyến nghị, không dùng Python 3.13 vì có thể gặp lỗi với PyInstaller)
- **pip** đã được cài đặt
- **Quyền Administrator** (không bắt buộc nhưng khuyến nghị)

---

## Bước 1: Chuẩn bị môi trường

### 1.1. Kiểm tra Python
```cmd
python --version
```
Phải hiển thị Python 3.10.x hoặc 3.11.x

### 1.2. Cài đặt dependencies
```cmd
cd "D:\7. Code\Check Hardware\autodesk-hwscanner"
python -m pip install -r requirements.txt
```

### 1.3. Cài đặt PyInstaller
```cmd
python -m pip install pyinstaller
```

---

## Bước 2: Build EXE

### Cách 1: Dùng script tự động (KHUYẾN NGHỊ)

Đơn giản nhất, chỉ cần chạy:
```cmd
build.bat
```

Script này sẽ:
- Tự kiểm tra Python và PyInstaller
- Tự động cài PyInstaller nếu chưa có
- Build EXE theo file `build.spec`
- Hiển thị kết quả và hướng dẫn sử dụng

### Cách 2: Build thủ công

```cmd
cd "D:\7. Code\Check Hardware\autodesk-hwscanner"
python -m PyInstaller build.spec --clean
```

**Lưu ý quan trọng:**
- **KHÔNG** chạy lệnh từ `C:\Windows\System32`
- Phải chạy từ **thư mục gốc của dự án** (`autodesk-hwscanner`)

---

## Bước 3: Kiểm tra kết quả

Sau khi build thành công, file EXE sẽ nằm ở:
```
dist\AutodeskHWScanner.exe
```

### Test chạy EXE:
```cmd
cd dist
AutodeskHWScanner.exe --product revit --version 2025 --out test_output
```

Nếu chạy thành công, bạn sẽ thấy:
- Thư mục `test_output` được tạo
- File JSON và HTML report được sinh ra
- Cửa sổ webview hiển thị báo cáo (nếu không có lỗi)

---

## Bước 4: Phân phối

### 4.1. File cần phân phối

**Tối thiểu:**
- `dist\AutodeskHWScanner.exe` (file EXE chính)

**File EXE đã bao gồm:**
- Tất cả dependencies (Python runtime, các thư viện)
- Tất cả rules JSON trong `scanner/rules/`
- Template HTML trong `report/templates/`
- File `dxinfo.xml` (nếu cần)

### 4.2. Tạo package phân phối

#### Option A: Chỉ file EXE (Đơn giản nhất)
1. Copy `dist\AutodeskHWScanner.exe` ra USB hoặc thư mục chia sẻ
2. Người dùng chỉ cần chạy file EXE này, không cần cài đặt gì thêm

#### Option B: Tạo thư mục phân phối (Chuyên nghiệp)
```
AutodeskHWScanner_v1.0/
├── AutodeskHWScanner.exe
├── README.txt (hướng dẫn sử dụng)
└── examples/
    └── (ví dụ lệnh chạy)
```

#### Option C: Tạo Installer (Chuyên nghiệp nhất)
Có thể dùng công cụ như:
- **Inno Setup** (miễn phí, dễ dùng)
- **NSIS** (miễn phí, mạnh mẽ)
- **WiX Toolset** (Microsoft official)

---

## Bước 5: Xử lý lỗi thường gặp

### Lỗi: "No module named PyInstaller"
**Giải pháp:**
```cmd
python -m pip install pyinstaller
```

### Lỗi: "Do not run pyinstaller from C:\Windows\System32"
**Giải pháp:**
- Đóng terminal hiện tại
- Mở File Explorer, vào thư mục `autodesk-hwscanner`
- Gõ `cmd` vào thanh địa chỉ, Enter
- Chạy lại lệnh build

### Lỗi: "No module named webview"
**Giải pháp:**
```cmd
python -m pip install pywebview
```

### Lỗi: EXE chạy nhưng không tìm thấy rules/templates
**Giải pháp:**
- Kiểm tra file `build.spec` có đúng đường dẫn `datas` không
- Đảm bảo các thư mục `scanner/rules` và `report/templates` tồn tại

### Lỗi: Windows Defender/antivirus báo virus
**Giải pháp:**
- Đây là **false positive** phổ biến với PyInstaller
- Thêm file EXE vào whitelist của antivirus
- Hoặc ký số (code signing) cho file EXE (yêu cầu chứng chỉ)

---

## Tùy chỉnh Build

### Thêm Icon cho EXE

1. Tạo hoặc tải file `.ico` (ví dụ: `icon.ico`)
2. Đặt vào thư mục gốc dự án
3. Sửa file `build.spec`:
```python
icon='icon.ico',  # Thay None bằng đường dẫn icon
```

### Thay đổi tên EXE

Sửa file `build.spec`:
```python
name='TenFileCuaBan',  # Thay 'AutodeskHWScanner'
```

### Build không có console (Windowed mode)

Sửa file `build.spec`:
```python
console=False,  # Thay True thành False
```

**Lưu ý:** Nếu dùng windowed mode, bạn sẽ không thấy output trong console, nên cần có logging hoặc GUI để hiển thị lỗi.

---

## Checklist trước khi phân phối

- [ ] EXE đã được test trên máy khác (không có Python)
- [ ] Tất cả các rule JSON đã được cập nhật đúng
- [ ] Template HTML đã được kiểm tra hiển thị đúng
- [ ] EXE chạy được với tất cả các product (revit, autocad, inventor)
- [ ] EXE chạy được với tất cả các version (2025, 2026)
- [ ] Không có lỗi khi chạy trên Windows 10 và Windows 11
- [ ] File size hợp lý (thường 50-150 MB cho PyInstaller onefile)
- [ ] Đã test trên máy sạch (không có Python, không có dependencies)

---

## Ghi chú kỹ thuật

- **File size:** EXE onefile thường lớn (50-150 MB) vì chứa toàn bộ Python runtime và dependencies
- **Thời gian khởi động:** EXE onefile có thể mất 2-5 giây để khởi động (do giải nén vào temp folder)
- **Performance:** So với chạy Python trực tiếp, EXE có thể chậm hơn một chút do overhead của PyInstaller
- **Tương thích:** EXE chỉ chạy trên Windows (64-bit), không thể chạy trên Linux/Mac

---

## Hỗ trợ

Nếu gặp vấn đề trong quá trình build, vui lòng:
1. Kiểm tra lại các bước trong hướng dẫn này
2. Xem log lỗi chi tiết từ PyInstaller
3. Đảm bảo đã cài đúng Python version (3.10 hoặc 3.11)

