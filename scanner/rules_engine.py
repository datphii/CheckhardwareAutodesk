import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple


def _get_rules_dir() -> Path:
    """Hỗ trợ khi chạy trong PyInstaller (sys._MEIPASS)"""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / "scanner" / "rules"


def load_rules(product: str, version: str) -> Dict[str, Any]:
    fname = f"{product.lower()}_{version}.json"
    path = _get_rules_dir() / fname
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_value_by_path(data: Dict[str, Any], path: str):
    # path ví dụ "gpu.vram_gb"
    cur = data
    for key in path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def is_windows_version_at_least(actual_version: str, min_version: str) -> bool:
    # Trích số version từ chuỗi, ví dụ: 'Microsoft Windows 11 Pro' -> 11, 'Windows 10 1809' -> 10
    import re
    def extract_major(v):
        m = re.search(r'(\d+)', v)
        return int(m.group(1)) if m else 0
    actual_major = extract_major(actual_version)
    min_major = extract_major(min_version)
    return actual_major >= min_major


def compare(actual, operator, min_value, target="") -> bool:
    if actual is None:
        return False
    if operator == ">=num":
        try:
            return float(actual) >= float(min_value)
        except:  # noqa: E722
            return False
    if operator == "in":
        return actual in min_value
    if operator == ">=str":
        # Đặc biệt so sánh version Windows
        if (target == "os.version") or ("windows" in str(target).lower()):
            return is_windows_version_at_least(str(actual), str(min_value))
        return str(actual) >= str(min_value)
    return False


def evaluate(rules: Dict[str, Any], facts: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    results = []
    overall = "Ready"
    for chk in rules["checks"]:
        actual = get_value_by_path(facts, chk["target"])
        passed_min = compare(actual, chk["operator"], chk["min"], chk["target"])
        status = "PASS" if passed_min else "FAIL"
        if status == "FAIL" and chk["severity"] == "recommended":
            status = "WARN"
        if status == "FAIL" and chk["severity"] == "required":
            overall = "Not Supported"
        elif status == "WARN" and overall != "Not Supported":
            overall = "Needs Upgrade"
        results.append({
            "id": chk["id"],
            "target": chk["target"],
            "actual": actual,
            "min": chk["min"],
            "recommended": chk.get("recommended"),
            "unit": chk.get("unit", ""),
            "severity": chk["severity"],
            "status": status
        })
    return overall, {"checks": results, "notes": rules.get("notes", "")}


