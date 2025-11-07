import argparse, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from scanner.collectors import os_info, cpu_info, ram_info, gpu_info, storage_info, network_info
from scanner.collectors.dxdiag import get_system_info
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
    # Bổ sung thông tin hệ thống từ dxdiag
    try:
        dxs = get_system_info()
        # Lưu các giá trị thô từ dxdiag vào facts.dxdiag để ghi ra JSON
        facts["dxdiag"] = {
            "processor": dxs.get("processor"),
            "system_model": dxs.get("system_model"),
            "computer_name": dxs.get("computer_name"),
        }
        # Đồng thời map sang các field hiển thị hiện có
        if dxs.get("processor"):
            facts["cpu"]["name"] = dxs.get("processor")
        if dxs.get("system_model"):
            facts["os"]["hostname"] = dxs.get("system_model")
        if dxs.get("computer_name"):
            facts["os"]["user"] = dxs.get("computer_name")
    except Exception:
        facts["dxdiag"] = {"processor": None, "system_model": None, "computer_name": None}
    # Làm phẳng một số trường cho tiện rule
    facts["ram"]["total_gb"] = facts["ram"].get("total_gb")
    facts["gpu"]["vram_gb"] = facts["gpu"].get("vram_gb")
    facts["gpu"]["directx_feature_level"] = facts["gpu"].get("directx_feature_level")
    facts["storage"]["free_gb"] = facts["storage"].get("free_gb")
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


def _discover_options():
    """Đọc thư mục rules để suy ra danh sách product và version khả dụng."""
    import re, sys
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
    rules_dir = base / "scanner" / "rules"
    products_to_versions = {}
    for path in rules_dir.glob("*.json"):
        m = re.match(r"(\w+)_(\d{4})\.json$", path.name)
        if not m:
            continue
        product, version = m.group(1), m.group(2)
        products_to_versions.setdefault(product, set()).add(version)
    # sort
    products = sorted(products_to_versions.keys())
    for p in products:
        products_to_versions[p] = sorted(products_to_versions[p])
    return products, products_to_versions


def _interactive_select():
    """Hiển thị GUI để chọn product/version/out.
    Ưu tiên Tkinter (không phụ thuộc .NET). Nếu Tkinter không khả dụng, thử pywebview.
    Trả về tuple (product, version, out_dir) hoặc None nếu hủy."""
    products, mapping = _discover_options()
    if not products:
        return None

    # 1) Thử Tkinter trước (ổn định nhất trên Windows/PyInstaller)
    try:
        import tkinter as tk
        from tkinter import ttk
        from tkinter import filedialog

        selection = {"product": products[0], "version": mapping[products[0]][0], "out": "out"}

        def on_product_change(event=None):
            vers = mapping[product_var.get()]
            version_box["values"] = vers
            version_var.set(vers[0])

        def browse_out():
            path = filedialog.askdirectory()
            if path:
                out_var.set(path)

        def on_submit():
            selection["product"] = product_var.get()
            selection["version"] = version_var.get()
            selection["out"] = out_var.get() or "out"
            root.destroy()

        root = tk.Tk()
        root.title("Autodesk Hardware Scanner")
        root.geometry("360x220")

        tk.Label(root, text="Product").pack(anchor="w", padx=12, pady=(12,2))
        product_var = tk.StringVar(value=products[0])
        product_box = ttk.Combobox(root, textvariable=product_var, values=products, state="readonly")
        product_box.pack(fill="x", padx=12)

        tk.Label(root, text="Version").pack(anchor="w", padx=12, pady=(10,2))
        version_var = tk.StringVar(value=mapping[products[0]][0])
        version_box = ttk.Combobox(root, textvariable=version_var, values=mapping[products[0]], state="readonly")
        version_box.pack(fill="x", padx=12)

        product_box.bind("<<ComboboxSelected>>", on_product_change)

        tk.Label(root, text="Output folder").pack(anchor="w", padx=12, pady=(10,2))
        out_var = tk.StringVar(value="out")
        frm = tk.Frame(root)
        frm.pack(fill="x", padx=12)
        tk.Entry(frm, textvariable=out_var).pack(side="left", fill="x", expand=True)
        ttk.Button(frm, text="Browse", command=browse_out).pack(side="left", padx=(6,0))

        ttk.Button(root, text="Run", command=on_submit).pack(pady=12)
        root.mainloop()
        return (selection["product"], selection["version"], selection["out"]) if selection else None
    except Exception:
        pass

    # 2) Thử pywebview nếu Tkinter không dùng được
    try:
        import os
        os.environ.setdefault('PYWEBVIEW_GUI', 'mshtml')
        import webview
        import json as _json, threading

        options_json = _json.dumps(mapping)
        html_tpl = """
        <html><head><meta charset='utf-8'>
        <style>body{font-family:Segoe UI,Arial,sans-serif;padding:18px}label{display:block;margin-top:10px}select,input{width:100%;padding:8px;margin-top:6px}button{margin-top:16px;padding:10px 14px}</style>
        </head><body>
        <h2>Autodesk Hardware Scanner</h2>
        <label>Product</label><select id='product'></select>
        <label>Version</label><select id='version'></select>
        <label>Output folder</label><input id='out' value='out'/>
        <button onclick='submit()'>Run</button>
        <script>
          const mapping=__OPTIONS_JSON__;
          const p=document.getElementById('product');const v=document.getElementById('version');
          function fillP(){Object.keys(mapping).forEach(x=>{let o=document.createElement('option');o.value=x;o.text=x;p.appendChild(o);});}
          function fillV(){v.innerHTML='';(mapping[p.value]||[]).forEach(x=>{let o=document.createElement('option');o.value=x;o.text=x;v.appendChild(o);});}
          p.addEventListener('change',fillV);
          function submit(){window.pywebview.api.set_selection({product:p.value,version:v.value,out:document.getElementById('out').value});}
          fillP();p.selectedIndex=0;fillV();
        </script>
        </body></html>
        """
        html = html_tpl.replace("__OPTIONS_JSON__", options_json)

        class Api:
            def __init__(self):
                self.selection=None
                self.evt=threading.Event()
            def set_selection(self, data):
                self.selection=(data.get('product'), data.get('version'), data.get('out') or 'out')
                self.evt.set()
                try:
                    webview.windows[0].destroy()
                except Exception:
                    pass

        api=Api()
        webview.create_window('Select options', html=html, width=420, height=420, resizable=False, js_api=api)
        webview.start(http_server=False, debug=False)
        api.evt.wait(timeout=300)
        return api.selection
    except Exception:
        return None


def run_gui_flow_and_show_report():
    """Luồng GUI một cửa sổ thuần Tkinter: chọn tham số và mở báo cáo trong trình duyệt mặc định."""
    products, mapping = _discover_options()
    if not products:
        return False

    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        import webbrowser

        ok = {"v": False}

        def on_product_change(event=None):
            vers = mapping[product_var.get()]
            version_box["values"] = vers
            version_var.set(vers[0])

        def browse_out():
            path = filedialog.askdirectory()
            if path:
                out_var.set(path)

        def on_run():
            try:
                product = product_var.get()
                version = version_var.get()
                out_value = out_var.get() or 'out'
                out_dir = Path(out_value).resolve()
                out_dir.mkdir(parents=True, exist_ok=True)
                facts = collect_all()
                rules = load_rules(product, version)
                overall, details = evaluate(rules, facts)
                json_path = out_dir / f"{product}_{version}_facts_and_result.json"
                json_path.write_text(json.dumps({
                    'product': product,
                    'version': version,
                    'overall': overall,
                    'details': details,
                    'facts': facts
                }, indent=2, ensure_ascii=False), encoding='utf-8')
                html_path = render_html(out_dir, product, version, overall, details, facts)
                webbrowser.open_new_tab(html_path.resolve().as_uri())
                ok["v"] = True
                root.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        root = tk.Tk()
        root.title("Autodesk Hardware Scanner")
        root.geometry("380x240")

        tk.Label(root, text="Product").pack(anchor="w", padx=12, pady=(12,2))
        product_var = tk.StringVar(value=products[0])
        product_box = ttk.Combobox(root, textvariable=product_var, values=products, state="readonly")
        product_box.pack(fill="x", padx=12)

        tk.Label(root, text="Version").pack(anchor="w", padx=12, pady=(10,2))
        version_var = tk.StringVar(value=mapping[products[0]][0])
        version_box = ttk.Combobox(root, textvariable=version_var, values=mapping[products[0]], state="readonly")
        version_box.pack(fill="x", padx=12)
        product_box.bind("<<ComboboxSelected>>", on_product_change)

        tk.Label(root, text="Output folder").pack(anchor="w", padx=12, pady=(10,2))
        out_var = tk.StringVar(value="out")
        frm = tk.Frame(root); frm.pack(fill="x", padx=12)
        tk.Entry(frm, textvariable=out_var).pack(side="left", fill="x", expand=True)
        ttk.Button(frm, text="Browse", command=browse_out).pack(side="left", padx=(6,0))

        ttk.Button(root, text="Run", command=on_run).pack(pady=12)
        root.mainloop()
        return ok["v"]
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description="Autodesk Hardware Scanner (CLI)")
    ap.add_argument("--product", help="vd: revit | autocad | inventor")
    ap.add_argument("--version", help="vd: 2025")
    ap.add_argument("--out", default="out", help="thư mục xuất")
    ap.add_argument("--json-only", action="store_true", help="chỉ xuất JSON")
    ap.add_argument("--gui", action="store_true", help="mở giao diện chọn nếu không truyền tham số")
    args = ap.parse_args()

    product = args.product
    version = args.version
    out_value = args.out

    if (args.gui or not product or not version):
        # Luồng một cửa sổ: chọn và hiển thị ngay
        ok = run_gui_flow_and_show_report()
        if ok:
            return
        # Nếu GUI không khởi tạo được, fallback chọn tạm và chạy CLI
        sel = _interactive_select()
        if sel:
            product, version, out_value = sel
        elif not (product and version):
            products, mapping = _discover_options()
            if products:
                product = product or products[0]
                version = version or mapping.get(product, ["2025"])[0]
        if not (product and version):
            print("Thiếu tham số --product/--version và không thể mở GUI")
            return

    out_dir = Path(out_value)
    out_dir.mkdir(parents=True, exist_ok=True)

    facts = collect_all()
    rules = load_rules(product, version)
    overall, details = evaluate(rules, facts)

    # JSON
    json_path = out_dir / f"{product}_{version}_facts_and_result.json"
    json_path.write_text(
        json.dumps({
            "product": product,
            "version": version,
            "overall": overall,
            "details": details,
            "facts": facts
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not args.json_only:
        html_path = render_html(out_dir, product, version, overall, details, facts)
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
    os.environ.setdefault('PYWEBVIEW_GUI', 'edgechromium')
    abs_path = os.path.abspath(html_path)
    webview.create_window('Scan Result', f'file:///{abs_path}', width=950, height=800, resizable=True)
    try:
        webview.start(gui='edgechromium')
    except Exception:
        webview.start(gui='mshtml')


if __name__ == "__main__":
    main()
