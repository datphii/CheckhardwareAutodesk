# Autodesk Hardware Scanner Desktop

Electron + React desktop app for Autodesk hardware and connectivity checks.

## Development

From `electron-app`:

```powershell
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run electron:dev
```

The desktop app runs checks in the Electron main process. React talks to it through the preload IPC bridge.

## Build EXE

Build the Electron app:

```powershell
cd electron-app
& "C:\Program Files\nodejs\npm.cmd" run dist
```

Output is written to `electron-app\release`.

## Data model

- Hardware rules stay as JSON files in `scanner\rules`.
- Autodesk connectivity endpoints stay in `scanner\network_endpoints\autodesk.json`.
- Electron main process keeps Windows hardware, DNS, TCP and HTTPS checks.
- React owns the desktop interface.
