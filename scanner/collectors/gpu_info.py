from .dxdiag import run_dxdiag_xml, parse_dxdiag, get_wmi_video_info_best, get_registry_video_info_best, list_gpus_all_sources


def collect():
    try:
        run_dxdiag_xml()
        data = parse_dxdiag()
    except Exception:
        data = {}
    # Nếu vẫn thiếu VRAM, bổ sung từ WMI/Registry ngay tại đây như một lớp bảo hiểm
    name = data.get("description")
    vram_gb = data.get("vram_gb")
    adapters = list_gpus_all_sources()
    # pick best from adapters if missing
    if not vram_gb:
        info = get_wmi_video_info_best()
        if info.get("description"):
            name = info.get("description")
        if info.get("vram_gb"):
            vram_gb = info.get("vram_gb")
    if not vram_gb:
        info = get_registry_video_info_best()
        if info.get("description") and not name:
            name = info.get("description")
        if info.get("vram_gb"):
            vram_gb = info.get("vram_gb")
    # As a final step: take maximum VRAM across enumerated adapters
    try:
        if adapters:
            max_adapter = None
            for g in adapters:
                vg = g.get("vram_gb") or 0
                if (max_adapter is None) or (vg > (max_adapter.get("vram_gb") or 0)):
                    max_adapter = g
            if max_adapter:
                if not vram_gb and max_adapter.get("vram_gb"):
                    vram_gb = max_adapter.get("vram_gb")
                # Prefer naming by the adapter with largest VRAM if name missing
                if not name and max_adapter.get("name"):
                    name = max_adapter.get("name")
    except Exception:
        pass
    return {
        "name": name,
        "vram_gb": vram_gb,
        "directx_feature_level": data.get("directx_feature_level"),
        "adapters": adapters
    }


