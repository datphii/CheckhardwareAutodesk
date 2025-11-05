from .dxdiag import run_dxdiag_xml, parse_dxdiag


def collect():
    try:
        run_dxdiag_xml()
        data = parse_dxdiag()
    except Exception:
        data = {}
    # Ghi chú: Nếu không lấy được VRAM qua dxdiag, parse_dxdiag sẽ tự fallback sang WMI.
    return {
        "name": data.get("description"),
        "vram_gb": data.get("vram_gb"),
        "directx_feature_level": data.get("directx_feature_level")
    }


