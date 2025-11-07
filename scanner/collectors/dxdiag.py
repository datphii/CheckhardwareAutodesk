import subprocess, re, os
from lxml import etree


def run_dxdiag_xml(path="dxinfo.xml"):
    subprocess.check_output(["dxdiag", "/x", path], stderr=subprocess.STDOUT)

def get_registry_video_info_best():
    try:
        import winreg
        base_path = r"SYSTEM\\CurrentControlSet\\Control\\Video"
        hklm = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(hklm, base_path)
        i = 0
        best = None  # (vendor_score, vram_bytes, name)
        while True:
            try:
                sub = winreg.EnumKey(key, i)
            except OSError:
                break
            i += 1
            try:
                # Each GPU has 0000,0001... subkeys
                subkey = winreg.OpenKey(hklm, base_path + "\\" + sub)
                j = 0
                while True:
                    try:
                        leaf = winreg.EnumKey(subkey, j)
                    except OSError:
                        break
                    j += 1
                    if not leaf.isdigit():
                        continue
                    leaf_key = winreg.OpenKey(hklm, base_path + f"\\{sub}\\{leaf}")
                    def get_value(name):
                        try:
                            v, _ = winreg.QueryValueEx(leaf_key, name)
                            return v
                        except OSError:
                            return None
                    name = get_value("DriverDesc") or get_value("HardwareInformation.AdapterString") or ""
                    vram = get_value("HardwareInformation.qwMemorySize") or get_value("HardwareInformation.MemorySize") or 0
                    if isinstance(vram, bytes):
                        try:
                            vram = int.from_bytes(vram, 'little')
                        except Exception:
                            vram = 0
                    try:
                        vram = int(vram)
                    except Exception:
                        vram = 0
                    vn = str(name).lower()
                    vendor_score = 2 if ('nvidia' in vn or 'amd' in vn or 'radeon' in vn or 'geforce' in vn or 'quadro' in vn) else (0 if 'intel' in vn else 1)
                    candidate = (vendor_score, vram, name)
                    if (best is None) or (candidate > best):
                        best = candidate
            except Exception:
                continue
        if best:
            vram_gb = round(best[1] / (1024 ** 3), 2) if best[1] and best[1] > 0 else None
            return {"description": best[2], "vram_gb": vram_gb, "directx_feature_level": None}
    except Exception:
        pass
    return {"description": None, "vram_gb": None, "directx_feature_level": None}

def list_gpus_all_sources():
    """Trả về danh sách tất cả GPU với (name, vram_gb) nếu có.
    Ưu tiên PowerShell CIM; fallback pywin32 WMI; cuối cùng registry (không đầy đủ tên với một số máy).
    """
    adapters = []
    # PowerShell CIM
    try:
        import subprocess, json
        out = subprocess.check_output([
            "powershell","-Command",
            "Get-CimInstance Win32_VideoController | Select Name,AdapterRAM,PNPDeviceID,AdapterCompatibility | ConvertTo-Json -Compress"
        ], text=True)
        data = json.loads(out)
        items = data if isinstance(data, list) else [data]
        for v in items:
            name = (v.get('Name') or '').strip()
            vr = int(v.get('AdapterRAM') or 0)
            vram_gb = round(vr/(1024**3),2) if vr>0 else None
            if name:
                adapters.append({"name": name, "vram_gb": vram_gb})
    except Exception:
        pass
    # pywin32 WMI
    if not adapters:
        try:
            import win32com.client
            svc = win32com.client.Dispatch("WbemScripting.SWbemLocator").ConnectServer(".", "root\\cimv2")
            items = svc.ExecQuery("SELECT Name, AdapterRAM FROM Win32_VideoController")
            for v in items:
                name = str(getattr(v,'Name','') or '')
                vr = int(getattr(v,'AdapterRAM',0) or 0)
                vram_gb = round(vr/(1024**3),2) if vr>0 else None
                if name:
                    adapters.append({"name": name, "vram_gb": vram_gb})
        except Exception:
            pass
    # Registry (best-effort): we may not map each instance, but try Intel entries as seen
    if not adapters:
        reg = get_registry_video_info_best()
        if reg.get("description"):
            adapters.append({"name": reg["description"], "vram_gb": reg.get("vram_gb")})
    return adapters

def get_system_info(path="dxinfo.xml"):
    """Đọc một số trường tổng quát từ dxdiag: Processor, MachineName (Computer Name), SystemModel.
    Trả về dict {processor, computer_name, system_model}. Nếu không có, trả None.
    """
    try:
        if not os.path.exists(path):
            run_dxdiag_xml(path)
        tree = etree.parse(path)
        root = tree.getroot()
        # Các tag phổ biến trong dxdiag XML
        processor = root.findtext(".//Processor") or None
        computer = root.findtext(".//MachineName") or None
        model = root.findtext(".//SystemModel") or None
        # Một số bản có tên khác
        if not model:
            model = root.findtext(".//System Model") or root.findtext(".//SystemModel")
        return {"processor": processor, "computer_name": computer, "system_model": model}
    except Exception:
        return {"processor": None, "computer_name": None, "system_model": None}

def get_wmi_video_info_best():
    try:
        import wmi
        c = wmi.WMI()
        best = None
        for v in c.Win32_VideoController():
            name = getattr(v, 'Name', '') or ''
            vendor_name = (getattr(v, 'AdapterCompatibility', '') or '') + ' ' + name
            vr = int(getattr(v, 'AdapterRAM', 0) or 0)
            vn = vendor_name.lower()
            # Prefer discrete vendors (NVIDIA/AMD/RADEON/QUADRO/GEFORCE) over Intel
            vendor_score = 2 if ('nvidia' in vn or 'amd' in vn or 'radeon' in vn or 'geforce' in vn or 'quadro' in vn) else (0 if 'intel' in vn else 1)
            candidate = (vendor_score, vr, name)
            if (best is None) or (candidate > best):
                best = candidate
        if best:
            vram_gb = round(best[1] / (1024 ** 3), 2) if best[1] and best[1] > 0 else None
            return {"description": best[2], "vram_gb": vram_gb, "directx_feature_level": None}
    except Exception:
        # Fallback without python-wmi: use pywin32 COM
        try:
            import win32com.client
            locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = locator.ConnectServer(".", "root\\cimv2")
            items = svc.ExecQuery("SELECT Name, AdapterRAM, AdapterCompatibility, PNPDeviceID FROM Win32_VideoController")
            best = None
            for v in items:
                name = str(getattr(v, 'Name', '') or '')
                vendor_name = str(getattr(v, 'AdapterCompatibility', '') or '') + ' ' + name + ' ' + str(getattr(v, 'PNPDeviceID', '') or '')
                vr = int(getattr(v, 'AdapterRAM', 0) or 0)
                vn = vendor_name.lower()
                vendor_score = 2 if ('nvidia' in vn or 'amd' in vn or 'radeon' in vn or 'geforce' in vn or 'quadro' in vn or 'ven_10de' in vn or 'ven_1002' in vn) else (0 if ('intel' in vn or 'ven_8086' in vn) else 1)
                candidate = (vendor_score, vr, name)
                if (best is None) or (candidate > best):
                    best = candidate
            if best:
                vram_gb = round(best[1] / (1024 ** 3), 2) if best[1] and best[1] > 0 else None
                return {"description": best[2], "vram_gb": vram_gb, "directx_feature_level": None}
        except Exception:
            # Last resort: PowerShell CIM query
            try:
                import subprocess, json
                cmd = [
                    "powershell",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,PNPDeviceID,AdapterCompatibility | ConvertTo-Json -Compress"
                ]
                out = subprocess.check_output(cmd, text=True)
                data = json.loads(out)
                items = data if isinstance(data, list) else [data]
                best = None
                for v in items:
                    name = (v.get('Name') or '')
                    vendor_name = (v.get('AdapterCompatibility') or '') + ' ' + name + ' ' + (v.get('PNPDeviceID') or '')
                    vr = int(v.get('AdapterRAM') or 0)
                    vn = vendor_name.lower()
                    vendor_score = 2 if ('nvidia' in vn or 'amd' in vn or 'radeon' in vn or 'geforce' in vn or 'quadro' in vn or 'ven_10de' in vn or 'ven_1002' in vn) else (0 if ('intel' in vn or 'ven_8086' in vn) else 1)
                    candidate = (vendor_score, vr, name)
                    if (best is None) or (candidate > best):
                        best = candidate
                if best:
                    vram_gb = round(best[1] / (1024 ** 3), 2) if best[1] and best[1] > 0 else None
                    return {"description": best[2], "vram_gb": vram_gb, "directx_feature_level": None}
            except Exception:
                pass
    return {"description": None, "vram_gb": None, "directx_feature_level": None}

def parse_dxdiag(path="dxinfo.xml"):
    if not os.path.exists(path):
        return get_wmi_video_info_best()
    try:
        tree = etree.parse(path)
        root = tree.getroot()
        devs = root.findall(".//DisplayDevices")
        best = {"description": "", "vram_gb": None, "directx_feature_level": None}
        best_tuple = None  # (vendor_score, vram_gb, desc)
        # Lấy DirectX phiên bản lớn nhất từ file dxdiag (duy nhất)
        fl_text = root.findtext(".//DirectXVersion") or ""
        feature_level = 12 if "12" in fl_text else (11 if "11" in fl_text else None)
        for dev in devs:
            # Một số bản dxdiag dùng CardName thay vì Description
            desc = dev.findtext("Description") or dev.findtext("CardName") or ""
            vram_text = dev.findtext("DedicatedMemory") or "0"
            vram_mb = int(re.sub(r"[^\d]", "", vram_text)) if re.search(r"\d", vram_text) else 0
            vram_gb = round(vram_mb / 1024, 2) if vram_mb else 0
            vn = desc.lower()
            vendor_score = 2 if ('nvidia' in vn or 'amd' in vn or 'radeon' in vn or 'geforce' in vn or 'quadro' in vn) else (0 if 'intel' in vn else 1)
            candidate = (vendor_score, vram_gb, desc)
            if (best_tuple is None) or (candidate > best_tuple):
                best_tuple = candidate
                best = {"description": desc, "vram_gb": (vram_gb if vram_gb else None), "directx_feature_level": feature_level}
        # Nếu không tìm được VRAM hoặc giá trị quá thấp, fallback từ WMI/Registry nhưng luôn giữ DirectX feature_level từ DXdiag nếu có
        if (not best["vram_gb"]) or (best["vram_gb"] < 0.1):
            info = get_wmi_video_info_best()
            if (not info.get("vram_gb")) or (info.get("vram_gb") is None):
                info = get_registry_video_info_best()
            info["directx_feature_level"] = feature_level
            return info
        return best
    except Exception:
        # Nếu dxdiag parse fail hoàn toàn, fallback WMI/Registry (không có feature_level)
        info = get_wmi_video_info_best()
        if not info.get("vram_gb"):
            info = get_registry_video_info_best()
        return info


