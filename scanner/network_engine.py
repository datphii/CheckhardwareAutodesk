import socket
import ssl
import time
import urllib.request
from typing import Any, Dict, List
from urllib.parse import urlparse

from scanner.config_manager import load_json_config


DEFAULT_ENDPOINT_CONFIG = "scanner/network_endpoints/autodesk.json"


def load_endpoint_config() -> Dict[str, Any]:
    return load_json_config(DEFAULT_ENDPOINT_CONFIG)


def _dns_lookup(host: str) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        infos = socket.getaddrinfo(host, None)
        addresses = sorted({item[4][0] for item in infos})
        return {
            "ok": True,
            "addresses": addresses,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "addresses": [],
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": str(exc),
        }


def _tcp_connect(host: str, port: int, timeout: float) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return {
            "ok": True,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": str(exc),
        }


def _https_request(url: str, timeout: float) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "AutodeskHWScanner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
            status = getattr(res, "status", None)
            return {
                "ok": 200 <= int(status or 0) < 500,
                "status": status,
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
                "error": None,
            }
    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
            "error": str(exc),
        }


def test_endpoint(endpoint: Dict[str, Any], timeout: float = 8.0) -> Dict[str, Any]:
    url = endpoint["url"]
    parsed = urlparse(url)
    host = parsed.hostname or url
    scheme = parsed.scheme or endpoint.get("protocol", "https")
    port = int(parsed.port or endpoint.get("port") or (443 if scheme == "https" else 80))
    checks = endpoint.get("checks", ["dns", "tcp", "https"])

    result = {
        "id": endpoint.get("id"),
        "name": endpoint.get("name"),
        "category": endpoint.get("category"),
        "url": url,
        "host": host,
        "port": port,
        "protocol": scheme,
        "required": bool(endpoint.get("required", True)),
        "checks": {},
        "ok": True,
    }

    if "dns" in checks:
        result["checks"]["dns"] = _dns_lookup(host)
    if "tcp" in checks:
        result["checks"]["tcp"] = _tcp_connect(host, port, timeout)
    if "https" in checks and scheme == "https":
        result["checks"]["https"] = _https_request(url, timeout)

    result["ok"] = all(item.get("ok") for item in result["checks"].values())
    return result


def run_network_tests(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cfg = config or load_endpoint_config()
    timeout = float(cfg.get("timeout_seconds", 8))
    endpoints: List[Dict[str, Any]] = cfg.get("endpoints", [])
    results = [test_endpoint(endpoint, timeout=timeout) for endpoint in endpoints]
    required_failures = [r for r in results if r.get("required") and not r.get("ok")]
    optional_failures = [r for r in results if not r.get("required") and not r.get("ok")]
    overall = "PASS" if not required_failures else "FAIL"
    if overall == "PASS" and optional_failures:
        overall = "WARN"
    return {
        "overall": overall,
        "config_version": cfg.get("version"),
        "config_source": cfg.get("_source"),
        "last_updated": cfg.get("last_updated"),
        "results": results,
    }
