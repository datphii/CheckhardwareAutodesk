import psutil


def collect():
    disks = psutil.disk_partitions(all=False)
    # Lấy ổ hệ thống (thường C:)
    system_drive = next((d for d in disks if d.mountpoint.upper().startswith("C")), disks[0] if disks else None)
    free_gb = None
    if system_drive:
        usage = psutil.disk_usage(system_drive.mountpoint)
        free_gb = round(usage.free / (1024**3), 2)
    # Loại ổ: heuristic đơn giản (NVMe/SSD/HDD)
    drive_type = detect_drive_type()
    return {"primary_mount": system_drive.mountpoint if system_drive else None,
            "free_gb": free_gb,
            "primary_type": drive_type}


def detect_drive_type():
    # Cách đơn giản: đọc từ tên thiết bị nếu có NVMe, nếu không giả định SSD/HDD
    try:
        import subprocess, re
        out = subprocess.check_output(["wmic", "diskdrive", "get", "Model,MediaType"], text=True)
        if "NVMe" in out:
            return "NVMe"
        if "SSD" in out:
            return "SSD"
        if "HDD" in out or "Fixed hard disk" in out:
            return "HDD"
    except Exception:
        pass
    return "Unknown"


