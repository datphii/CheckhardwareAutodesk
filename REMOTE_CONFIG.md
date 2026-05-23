# Remote Configuration

Desktop app can load Autodesk rules and endpoint definitions from remote JSON before each full check.

Default remote config URL:

```text
https://raw.githubusercontent.com/datphii/hardwareAutodesk/refs/heads/main/autodesk_spec_config.json
```

This all-in-one format is supported directly:

```json
{
  "config_version": "1.0.0",
  "last_updated": "2026-05-23",
  "software_requirements": {
    "AutoCAD": {
      "2026": {
        "minimum": {
          "os": ["Windows 10 64-bit v22H2", "Windows 11"],
          "cpu_speed_ghz": 2.5,
          "ram_gb": 16,
          "gpu_vram_gb": 2,
          "gpu_directx": 11,
          "storage_gb": 12
        },
        "recommended": {
          "os": ["Windows 10 64-bit v22H2", "Windows 11"],
          "cpu_speed_ghz": 3.0,
          "ram_gb": 32,
          "gpu_vram_gb": 8,
          "gpu_directx": 12,
          "storage_gb": 12
        }
      }
    }
  }
}
```

Optional endpoint keys are also supported when present:

- `network_endpoints`
- `autodesk_endpoints`
- `endpoints`

## GitHub repository structure

```text
autodesk-hwscanner-config/
  manifest.json
  rules/
    autocad_2026.json
    revit_2026.json
    inventor_2026.json
  network_endpoints/
    autodesk.json
```

## manifest.json

Use raw GitHub URLs in the app, for example:

```text
https://raw.githubusercontent.com/<user>/<repo>/main/manifest.json
```

Example manifest:

```json
{
  "version": "2026.05.23",
  "rules": {
    "autocad_2026.json": "rules/autocad_2026.json",
    "revit_2026.json": "rules/revit_2026.json",
    "inventor_2026.json": "rules/inventor_2026.json"
  },
  "endpoints": "network_endpoints/autodesk.json"
}
```

Relative paths are resolved from `manifest.json`.

## Behavior

- When the user clicks `Chạy kiểm tra tổng thể`, the app downloads `manifest.json`.
- It then downloads every rule JSON and `network_endpoints/autodesk.json`.
- Downloaded files are cached under the app user data folder.
- If GitHub is unavailable, the app uses the last cached config.
- If there is no cache yet, the app falls back to the config bundled inside the EXE.
