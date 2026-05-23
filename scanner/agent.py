import json
import re
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scanner.config_manager import bundled_path, load_settings, update_json_config
from scanner.main import collect_all
from scanner.network_engine import DEFAULT_ENDPOINT_CONFIG, load_endpoint_config, run_network_tests
from scanner.rules_engine import load_rules, evaluate


class SoftwareCheckRequest(BaseModel):
    product: str
    version: str


class ConfigUpdateRequest(BaseModel):
    url: str


def discover_options() -> Dict[str, Any]:
    rules_dir = bundled_path("scanner", "rules")
    mapping: Dict[str, list[str]] = {}
    for path in rules_dir.glob("*.json"):
        match = re.match(r"(\w+)_(\d{4})\.json$", path.name)
        if not match:
            continue
        product, version = match.group(1), match.group(2)
        mapping.setdefault(product, []).append(version)
    for product in mapping:
        mapping[product] = sorted(mapping[product])
    return {"products": sorted(mapping.keys()), "versions": mapping}


def update_configs_from_settings() -> Dict[str, Any]:
    settings = load_settings()
    update_settings = settings.get("update", {})
    results: Dict[str, Any] = {}

    network_url = update_settings.get("network_endpoints_url")
    if network_url:
        results["network"] = update_json_config(DEFAULT_ENDPOINT_CONFIG, network_url)

    rules_base_url = (update_settings.get("rules_base_url") or "").rstrip("/")
    if rules_base_url:
        options = discover_options()
        rules_results = []
        for product, versions in options["versions"].items():
            for version in versions:
                name = f"{product.lower()}_{version}.json"
                url = f"{rules_base_url}/{name}"
                rules_results.append(update_json_config(f"scanner/rules/{name}", url))
        results["rules"] = rules_results

    if not results:
        return {"updated": False, "message": "No update URLs configured"}
    return {"updated": True, "results": results}


def create_app() -> FastAPI:
    app = FastAPI(title="Autodesk Hardware Scanner Agent", version="2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:17890",
            "http://localhost:17890",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    web_dir = bundled_path("web")
    if web_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(web_dir)), name="assets")

    @app.get("/")
    def index():
        index_path = web_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Autodesk Hardware Scanner Agent"}

    @app.get("/api/health")
    def health():
        return {"ok": True, "service": "autodesk-hwscanner-agent"}

    @app.get("/api/options")
    def options():
        return discover_options()

    @app.get("/api/hardware")
    def hardware():
        return {"facts": collect_all()}

    @app.post("/api/software-check")
    def software_check(req: SoftwareCheckRequest):
        product = req.product.lower().strip()
        version = req.version.strip()
        try:
            facts = collect_all()
            rules = load_rules(product, version)
            overall, details = evaluate(rules, facts)
            return {
                "product": product,
                "version": version,
                "overall": overall,
                "details": details,
                "facts": facts,
                "rules_source": rules.get("_source"),
            }
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Rules not found")

    @app.get("/api/network-config")
    def network_config():
        return load_endpoint_config()

    @app.get("/api/settings")
    def settings():
        return load_settings()

    @app.post("/api/network-check")
    def network_check():
        return run_network_tests()

    @app.post("/api/config/network/update")
    def update_network_config(req: ConfigUpdateRequest):
        return update_json_config(DEFAULT_ENDPOINT_CONFIG, req.url)

    @app.post("/api/config/rules/{product}/{version}/update")
    def update_rules_config(product: str, version: str, req: ConfigUpdateRequest):
        name = f"{product.lower()}_{version}.json"
        return update_json_config(f"scanner/rules/{name}", req.url)

    @app.post("/api/config/update-all")
    def update_all_configs():
        return update_configs_from_settings()

    return app


def main(host: str = "127.0.0.1", port: int = 17890, open_browser: bool = True):
    try:
        settings = load_settings()
        if settings.get("update", {}).get("check_on_startup"):
            update_configs_from_settings()
    except Exception:
        pass
    import os
    if os.environ.get("AUTODESK_HWSCANNER_NO_BROWSER") == "1":
        open_browser = False
    if open_browser:
        webbrowser.open(f"http://{host}:{port}")
    uvicorn.run(create_app(), host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
