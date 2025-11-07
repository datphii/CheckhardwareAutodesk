import psutil


def collect():
    disks = psutil.disk_partitions(all=False)
    # Lấy ổ hệ thống (thường C:)
    system_drive = next((d for d in disks if d.mountpoint.upper().startswith("C")), disks[0] if disks else None)
    free_gb = None
    if system_drive:
        usage = psutil.disk_usage(system_drive.mountpoint)
        free_gb = round(usage.free / (1024**3), 2)
    return {"primary_mount": system_drive.mountpoint if system_drive else None,
            "free_gb": free_gb}


