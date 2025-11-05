import subprocess, re, os
from lxml import etree


def run_dxdiag_xml(path="dxinfo.xml"):
    subprocess.check_output(["dxdiag", "/x", path], stderr=subprocess.STDOUT)

def get_wmi_video_info_best():
    try:
        import wmi
        c = wmi.WMI()
        best = None
        for v in c.Win32_VideoController():
            vr = int(getattr(v, 'AdapterRAM', 0) or 0)
            if not best or vr > best[1]:
                best = (getattr(v, 'Name', ''), vr)
        if best and best[1] > 0:
            vram_gb = round(best[1] / (1024 ** 3), 2)
            return {"description": best[0], "vram_gb": vram_gb, "directx_feature_level": None}
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
        max_vram = -1
        # Lấy DirectX phiên bản lớn nhất từ file dxdiag (duy nhất)
        fl_text = root.findtext(".//DirectXVersion") or ""
        feature_level = 12 if "12" in fl_text else (11 if "11" in fl_text else None)
        for dev in devs:
            desc = dev.findtext("Description") or ""
            vram_text = dev.findtext("DedicatedMemory") or "0"
            vram_mb = int(re.sub(r"[^\d]", "", vram_text)) if re.search(r"\d", vram_text) else 0
            vram_gb = round(vram_mb / 1024, 2) if vram_mb else None
            if vram_gb and vram_gb > max_vram:
                best = {"description": desc, "vram_gb": vram_gb, "directx_feature_level": feature_level}
                max_vram = vram_gb
        # Nếu không tìm được VRAM hoặc giá trị quá thấp, fallback từ WMI nhưng luôn giữ DirectX feature_level từ DXdiag nếu có
        if (not best["vram_gb"]) or (best["vram_gb"] < 0.1):
            wmi_info = get_wmi_video_info_best()
            wmi_info["directx_feature_level"] = feature_level
            return wmi_info
        return best
    except Exception:
        # Nếu dxdiag parse fail hoàn toàn, fallback WMI (không có feature_level)
        return get_wmi_video_info_best()


