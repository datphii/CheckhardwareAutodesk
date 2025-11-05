# Hướng dẫn Cài đặt và Sử dụng

## Dành cho người dùng cuối

---

## Yêu cầu hệ thống

- **Windows 10** hoặc **Windows 11** (64-bit)
- **Không cần cài Python** - File EXE đã chứa tất cả mọi thứ cần thiết
- **Quyền Administrator** (không bắt buộc, nhưng có thể cần cho một số tính năng)

---

## Cài đặt

### Cách 1: Chạy trực tiếp (Không cần cài đặt)

1. **Tải file `AutodeskHWScanner.exe`**
2. **Copy file vào bất kỳ thư mục nào** (ví dụ: Desktop, Documents)
3. **Chạy file EXE** - Không cần cài đặt gì thêm!

### Cách 2: Cài đặt vào thư mục cố định (Khuyến nghị)

1. Tạo thư mục mới, ví dụ: `C:\Program Files\AutodeskHWScanner\`
2. Copy file `AutodeskHWScanner.exe` vào thư mục đó
3. (Tùy chọn) Tạo shortcut trên Desktop để tiện truy cập

---

## Cách sử dụng

### Chạy qua Command Prompt hoặc PowerShell

1. Mở **Command Prompt** (CMD) hoặc **PowerShell**
2. Điều hướng đến thư mục chứa file EXE:
   ```cmd
   cd "C:\Program Files\AutodeskHWScanner"
   ```
   (hoặc thư mục bạn đã đặt file EXE)

3. Chạy lệnh kiểm tra:

#### Kiểm tra Revit 2025:
```cmd
AutodeskHWScanner.exe --product revit --version 2025 --out kết_quả
```

#### Kiểm tra AutoCAD 2026:
```cmd
AutodeskHWScanner.exe --product autocad --version 2026 --out kết_quả
```

#### Kiểm tra Inventor 2025:
```cmd
AutodeskHWScanner.exe --product inventor --version 2025 --out kết_quả
```

### Các tham số

- `--product`: Tên sản phẩm cần kiểm tra
  - `revit` - Autodesk Revit
  - `autocad` - AutoCAD
  - `inventor` - Autodesk Inventor

- `--version`: Phiên bản sản phẩm
  - `2025` - Phiên bản 2025
  - `2026` - Phiên bản 2026
  - (Các phiên bản khác tùy theo rule JSON có sẵn)

- `--out`: Thư mục lưu kết quả (mặc định: `out`)
  - Có thể dùng đường dẫn tuyệt đối hoặc tương đối
  - Thư mục sẽ được tạo tự động nếu chưa tồn tại

- `--json-only`: Chỉ xuất file JSON, không tạo HTML và không mở popup

### Ví dụ đầy đủ:
```cmd
AutodeskHWScanner.exe --product revit --version 2025 --out "D:\Báo cáo\Kiểm tra máy"
```

---

## Kết quả

Sau khi chạy, bạn sẽ nhận được:

### 1. File JSON
- Tên file: `{product}_{version}_facts_and_result.json`
- Ví dụ: `revit_2025_facts_and_result.json`
- Chứa: Tất cả thông tin phần cứng và kết quả kiểm tra dưới dạng JSON

### 2. File HTML Report
- Tên file: `{product}_{version}_report.html`
- Ví dụ: `revit_2025_report.html`
- Chứa: Báo cáo đẹp mắt, dễ đọc với:
  - Tổng quan kết quả (Ready / Needs Upgrade / Not Supported)
  - Chi tiết từng tiêu chí kiểm tra
  - Thông tin phần cứng đầy đủ
  - Có thể in hoặc export PDF (nút Print trong trình duyệt)

### 3. Cửa sổ Popup (Tự động)
- Sau khi scan xong, cửa sổ webview sẽ tự động mở để hiển thị báo cáo HTML
- Bạn có thể đóng cửa sổ này hoặc lưu file HTML để xem sau

---

## Diễn giải kết quả

### Overall Status (Trạng thái tổng quan)

- **Ready** ✅
  - Máy tính của bạn đáp ứng đầy đủ yêu cầu phần cứng
  - Có thể cài đặt và sử dụng phần mềm Autodesk

- **Needs Upgrade** ⚠️
  - Một số thành phần phần cứng chưa đạt mức khuyến nghị
  - Vẫn có thể chạy phần mềm, nhưng hiệu năng có thể không tối ưu
  - Nên nâng cấp phần cứng để có trải nghiệm tốt hơn

- **Not Supported** ❌
  - Máy tính không đáp ứng yêu cầu tối thiểu
  - Không thể cài đặt hoặc chạy phần mềm Autodesk
  - Cần nâng cấp phần cứng

### Chi tiết từng tiêu chí

Mỗi tiêu chí sẽ có một trong các trạng thái:
- **PASS** ✅ - Đạt yêu cầu
- **FAIL** ❌ - Không đạt yêu cầu
- **WARN** ⚠️ - Đạt tối thiểu nhưng chưa đạt khuyến nghị

---

## Xử lý lỗi

### Lỗi: "Windows protected your PC"
**Giải pháp:**
1. Click "More info"
2. Click "Run anyway"
3. (Hoặc thêm file vào whitelist của Windows Defender)

### Lỗi: Antivirus chặn file EXE
**Giải pháp:**
- Đây là false positive phổ biến
- Thêm file EXE vào whitelist của phần mềm antivirus
- Hoặc tạm thời tắt antivirus khi chạy (không khuyến nghị)

### Lỗi: Không mở được popup webview
**Giải pháp:**
- Không ảnh hưởng đến kết quả scan
- File HTML vẫn được tạo ra, bạn có thể mở bằng trình duyệt web bất kỳ
- Dùng tham số `--json-only` nếu không muốn popup

### Lỗi: "Product not found" hoặc "Version not supported"
**Giải pháp:**
- Kiểm tra lại tên product và version có đúng không
- Danh sách product và version hỗ trợ:
  - Products: `revit`, `autocad`, `inventor`
  - Versions: `2025`, `2026` (tùy theo rule JSON có sẵn)

---

## Tips và Thủ thuật

### Chạy nhanh từ bất kỳ đâu

1. Thêm thư mục chứa EXE vào PATH của Windows:
   - Control Panel → System → Advanced System Settings
   - Environment Variables → Path → Edit
   - Thêm đường dẫn đến thư mục chứa EXE
2. Sau đó bạn có thể chạy từ bất kỳ đâu:
   ```cmd
   AutodeskHWScanner.exe --product revit --version 2025
   ```

### Chạy hàng loạt máy (Batch script)

Tạo file `scan_all.bat`:
```batch
@echo off
AutodeskHWScanner.exe --product revit --version 2025 --out kết_quả
AutodeskHWScanner.exe --product autocad --version 2025 --out kết_quả
AutodeskHWScanner.exe --product inventor --version 2025 --out kết_quả
pause
```

### Chỉ lấy JSON (không cần HTML)

```cmd
AutodeskHWScanner.exe --product revit --version 2025 --json-only --out kết_quả
```

---

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra lại các bước trong hướng dẫn này
2. Xem file log hoặc thông báo lỗi chi tiết
3. Liên hệ bộ phận IT hoặc người phát triển

---

## Phiên bản

- **Version:** 1.0
- **Last Updated:** 2025-10-30
- **Compatible with:** Windows 10/11 (64-bit)

