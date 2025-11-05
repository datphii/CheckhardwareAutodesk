import platform


def collect():
    return {
        "platform": platform.system(),
        "release": platform.release(),
        "version": get_windows_version_string()
    }


def get_windows_version_string():
    # Ghép tên dễ đọc, ví dụ "Windows 11" hoặc "Windows 10 22H2"
    try:
        import subprocess, re
        # Thử wmic trước
        try:
            out = subprocess.check_output(["cmd", "/c", "wmic os get Caption,BuildNumber /value"], text=True)
            cap = re.search(r"Caption=(.+)", out)
            ver = cap.group(1).strip() if cap else None
            if ver:
                return ver
        except Exception:
            pass
        # Fallback: gọi PowerShell (Get-CimInstance)
        try:
            out = subprocess.check_output(["powershell", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption"], text=True)
            ver = out.strip().split("\n")[0] if out.strip() else None
            if ver:
                return ver
        except Exception:
            pass
        # ultimate fallback
        return platform.version()
    except Exception:
        return platform.version()


