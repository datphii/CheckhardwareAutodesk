import argparse, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from scanner.collectors import os_info, cpu_info, ram_info, gpu_info, storage_info, network_info
from scanner.rules_engine import load_rules, evaluate


def collect_all():
    facts = {
        "os": os_info.collect(),
        "cpu": cpu_info.collect(),
        "ram": ram_info.collect(),
        "gpu": gpu_info.collect(),
        "storage": storage_info.collect(),
        # Bật nếu cần:
        # "network": network_info.collect(),
    }
    # Làm phẳng một số trường cho tiện rule
    facts["ram"]["total_gb"] = facts["ram"].get("total_gb")
    facts["gpu"]["vram_gb"] = facts["gpu"].get("vram_gb")
    facts["gpu"]["directx_feature_level"] = facts["gpu"].get("directx_feature_level")
    facts["storage"]["free_gb"] = facts["storage"].get("free_gb")
    facts["storage"]["primary_type"] = facts["storage"].get("primary_type")
    return facts


def _get_templates_dir() -> Path:
    # Hỗ trợ khi chạy trong PyInstaller (sys._MEIPASS)
    import sys
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
    return base / "report" / "templates"


def render_html(output_dir: Path, product: str, version: str, overall: str, details: dict, facts: dict):
    env = Environment(loader=FileSystemLoader(str(_get_templates_dir())))
    tpl = env.get_template("report.html.j2")
    html = tpl.render(product=product, version=version, overall=overall, details=details, facts=facts)
    out = output_dir / f"{product}_{version}_report.html"
    out.write_text(html, encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser(description="Autodesk Hardware Scanner (CLI)")
    ap.add_argument("--product", required=True, help="vd: revit | autocad | inventor")
    ap.add_argument("--version", required=True, help="vd: 2025")
    ap.add_argument("--out", default="out", help="thư mục xuất")
    ap.add_argument("--json-only", action="store_true", help="chỉ xuất JSON")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    facts = collect_all()
    rules = load_rules(args.product, args.version)
    overall, details = evaluate(rules, facts)

    # JSON
    json_path = out_dir / f"{args.product}_{args.version}_facts_and_result.json"
    json_path.write_text(
        json.dumps({
            "product": args.product,
            "version": args.version,
            "overall": overall,
            "details": details,
            "facts": facts
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not args.json_only:
        html_path = render_html(out_dir, args.product, args.version, overall, details, facts)
        print(f"[OK] Overall: {overall}\nHTML: {html_path}\nJSON: {json_path}")
        try:
            popup_report(html_path)
        except Exception as e:
            print(f"Could not open popup: {e}")
    else:
        print(f"[OK] Overall: {overall}\nJSON: {json_path}")


def popup_report(html_path):
    """Mở cửa sổ webview để hiển thị báo cáo HTML"""
    import webview
    import os
    abs_path = os.path.abspath(html_path)
    webview.create_window('Scan Result', f'file:///{abs_path}', width=950, height=800, resizable=True)
    webview.start()


if __name__ == "__main__":
    main()
