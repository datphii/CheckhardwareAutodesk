import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


APP_DIR = "AutodeskHWScanner"


def bundled_base() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))


def user_config_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_DIR
    return Path.home() / f".{APP_DIR.lower()}"


def bundled_path(*parts: str) -> Path:
    return bundled_base().joinpath(*parts)


def override_path(*parts: str) -> Path:
    return user_config_dir().joinpath(*parts)


def load_json_config(relative_path: str) -> Dict[str, Any]:
    parts = tuple(relative_path.replace("\\", "/").split("/"))
    override = override_path(*parts)
    source = override if override.exists() else bundled_path(*parts)
    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["_source"] = str(source)
    return data


def save_override_json(relative_path: str, data: Dict[str, Any]) -> Path:
    parts = tuple(relative_path.replace("\\", "/").split("/"))
    path = override_path(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def fetch_json(url: str, timeout: int = 15) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "AutodeskHWScanner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        charset = res.headers.get_content_charset() or "utf-8"
        return json.loads(res.read().decode(charset))


def update_json_config(relative_path: str, url: Optional[str]) -> Dict[str, Any]:
    if not url:
        raise ValueError("Missing update URL")
    data = fetch_json(url)
    path = save_override_json(relative_path, data)
    return {"updated": True, "path": str(path), "config": data}


def load_settings() -> Dict[str, Any]:
    return load_json_config("scanner/config/settings.json")
