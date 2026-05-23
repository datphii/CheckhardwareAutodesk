# Web Local Agent Architecture

## Goal

The product runs as a web UI, but hardware and network checks are executed by a local Windows agent.

Browser-only web apps cannot reliably read WMI, dxdiag, Registry, GPU VRAM, DirectX feature level, DNS, TCP, firewall, or proxy details. The local agent keeps those capabilities while the user experience stays web-based.

## Runtime

Start the agent:

```powershell
python -m scanner.main --agent --port 17890
```

Then open:

```text
http://127.0.0.1:17890
```

The packaged EXE uses the same command:

```powershell
AutodeskHWScanner.exe --agent
```

## API

- `GET /api/health`
- `GET /api/options`
- `GET /api/hardware`
- `POST /api/software-check`
- `GET /api/network-config`
- `POST /api/network-check`
- `GET /api/settings`
- `POST /api/config/network/update`
- `POST /api/config/rules/{product}/{version}/update`
- `POST /api/config/update-all`

## Config Strategy

No hardware rules or Autodesk network endpoints should be hardcoded in Python.

Bundled defaults:

- `scanner/rules/*.json`
- `scanner/network_endpoints/autodesk.json`
- `scanner/config/settings.json`

User override location:

```text
%LOCALAPPDATA%\AutodeskHWScanner\
```

The loader checks the user override first, then falls back to the bundled files inside the EXE/source tree.

## Keeping Rules And URLs Updated

Recommended production setup:

1. Host rule files on a trusted HTTPS endpoint.
2. Host the Autodesk endpoint manifest on a trusted HTTPS endpoint.
3. Configure `scanner/config/settings.json`:

```json
{
  "version": "2026.05.23",
  "update": {
    "network_endpoints_url": "https://your-domain.example/config/autodesk-endpoints.json",
    "rules_base_url": "https://your-domain.example/config/rules",
    "check_on_startup": true
  }
}
```

The rules base URL is expected to contain files like:

- `revit_2026.json`
- `autocad_2026.json`
- `inventor_2026.json`

The endpoint manifest format is the same as:

```text
scanner/network_endpoints/autodesk.json
```

For stricter production security, add manifest signing before trusting downloaded configs.
