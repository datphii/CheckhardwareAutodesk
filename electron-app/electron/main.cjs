const { app, BrowserWindow, Menu, dialog, ipcMain, shell } = require("electron");
const dns = require("node:dns/promises");
const fs = require("node:fs/promises");
const https = require("node:https");
const net = require("node:net");
const os = require("node:os");
const path = require("node:path");
const { tmpdir } = require("node:os");
const { execFile } = require("node:child_process");

const DEFAULT_REMOTE_CONFIG_URL = "https://raw.githubusercontent.com/datphii/hardwareAutodesk/refs/heads/main/autodesk_spec_config.json";

function repoRoot() {
  return path.resolve(__dirname, "..", "..");
}

function resourcePath(...parts) {
  if (app.isPackaged) return path.join(process.resourcesPath, ...parts);
  return path.join(repoRoot(), ...parts);
}

function userConfigPath(...parts) {
  return path.join(app.getPath("userData"), "remote-config", ...parts);
}

function settingsFile() {
  return path.join(app.getPath("userData"), "settings.json");
}

function rulesDir() {
  return userConfigPath("rules");
}

function bundledRulesDir() {
  return app.isPackaged ? resourcePath("config", "rules") : resourcePath("scanner", "rules");
}

function endpointsFile() {
  return userConfigPath("network_endpoints", "autodesk.json");
}

function bundledEndpointsFile() {
  return app.isPackaged
    ? resourcePath("config", "network_endpoints", "autodesk.json")
    : resourcePath("scanner", "network_endpoints", "autodesk.json");
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function activeRulesDir() {
  return (await pathExists(rulesDir())) ? rulesDir() : bundledRulesDir();
}

async function activeEndpointsFile() {
  return (await pathExists(endpointsFile())) ? endpointsFile() : bundledEndpointsFile();
}

async function readSettings() {
  try {
    return { remoteConfigUrl: DEFAULT_REMOTE_CONFIG_URL, ...JSON.parse(await fs.readFile(settingsFile(), "utf8")) };
  } catch {
    return { remoteConfigUrl: DEFAULT_REMOTE_CONFIG_URL };
  }
}

async function writeSettings(nextSettings) {
  await fs.mkdir(path.dirname(settingsFile()), { recursive: true });
  await fs.writeFile(settingsFile(), JSON.stringify(nextSettings, null, 2), "utf8");
  return nextSettings;
}

function resolveRemoteUrl(baseUrl, target) {
  if (!target) return null;
  return new URL(target, baseUrl).toString();
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      "Accept": "application/json",
      "User-Agent": "AutodeskHWScanner/1.0"
    }
  });
  if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
  return response.json();
}

function ruleEntries(manifest) {
  if (Array.isArray(manifest.rules)) {
    return manifest.rules.map((item) => ({
      file: item.file || `${String(item.product).toLowerCase()}_${item.version}.json`,
      url: item.url || item.path || item.file
    }));
  }
  if (manifest.rules && typeof manifest.rules === "object") {
    return Object.entries(manifest.rules).map(([key, value]) => ({
      file: key.endsWith(".json") ? key : `${key}.json`,
      url: value
    }));
  }
  return [];
}

function makeRequirementRule(product, version, requirement) {
  const minimum = requirement.minimum || {};
  const recommended = requirement.recommended || {};
  const checks = [
    {
      id: "os_win64",
      target: "os.version",
      operator: "windows_any",
      min: minimum.os || [],
      recommended: recommended.os || minimum.os || [],
      unit: "",
      severity: "critical"
    },
    {
      id: "cpu_speed",
      target: "cpu.speed_ghz",
      operator: ">=num",
      min: minimum.cpu_speed_ghz,
      recommended: recommended.cpu_speed_ghz,
      unit: "GHz",
      severity: "recommended"
    },
    {
      id: "ram_total",
      target: "ram.total_gb",
      operator: ">=num",
      min: minimum.ram_gb,
      recommended: recommended.ram_gb,
      unit: "GB",
      severity: "required"
    },
    {
      id: "gpu_vram",
      target: "gpu.vram_gb",
      operator: ">=num",
      min: minimum.gpu_vram_gb,
      recommended: recommended.gpu_vram_gb,
      unit: "GB",
      severity: "required"
    },
    {
      id: "directx_min",
      target: "gpu.directx_feature_level",
      operator: ">=num",
      min: minimum.gpu_directx,
      recommended: recommended.gpu_directx,
      unit: "",
      severity: "required"
    },
    {
      id: "directx_recommended",
      target: "gpu.directx_feature_level",
      operator: ">=num",
      min: recommended.gpu_directx,
      recommended: recommended.gpu_directx,
      unit: "",
      severity: "recommended"
    },
    {
      id: "storage_free",
      target: "storage.free_gb",
      operator: ">=num",
      min: minimum.storage_gb,
      recommended: recommended.storage_gb,
      unit: "GB",
      severity: "required"
    }
  ].filter((check) => check.min !== undefined && check.min !== null);

  return {
    product,
    version,
    checks,
    notes: `Remote configuration generated from Autodesk spec config for ${product} ${version}.`
  };
}

function isHttpUrl(value) {
  try {
    const parsed = new URL(String(value));
    return ["http:", "https:"].includes(parsed.protocol);
  } catch {
    return false;
  }
}

function normalizeEndpointItem(item, fallbackCategory = "Autodesk") {
  if (typeof item === "string") {
    if (!isHttpUrl(item)) return null;
    const parsed = new URL(item);
    return {
      id: parsed.hostname.replace(/[^a-z0-9]+/gi, "_").toLowerCase(),
      name: parsed.hostname,
      category: fallbackCategory,
      url: item,
      required: true,
      checks: ["dns", "tcp", "https"]
    };
  }
  if (!item || typeof item !== "object") return null;
  const url = item.url || item.link || item.href || item.endpoint;
  if (!isHttpUrl(url)) return null;
  const parsed = new URL(url);
  return {
    id: item.id || item.name || parsed.hostname,
    name: item.name || item.label || item.service || parsed.hostname,
    category: item.category || item.group || fallbackCategory,
    url,
    port: item.port,
    required: item.required !== false,
    checks: item.checks || ["dns", "tcp", "https"]
  };
}

function collectEndpointItems(source, fallbackCategory = "Autodesk") {
  if (!source) return [];
  if (Array.isArray(source)) {
    return source.flatMap((item) => collectEndpointItems(item, fallbackCategory));
  }
  if (typeof source === "string") {
    const endpoint = normalizeEndpointItem(source, fallbackCategory);
    return endpoint ? [endpoint] : [];
  }
  if (typeof source !== "object") return [];

  const direct = normalizeEndpointItem(source, fallbackCategory);
  if (direct) return [direct];

  const results = [];
  for (const [key, value] of Object.entries(source)) {
    if (["version", "last_updated", "timeout_seconds"].includes(key)) continue;
    results.push(...collectEndpointItems(value, key));
  }
  return results;
}

function normalizeEndpointConfig(endpointConfig, config) {
  if (!endpointConfig) return null;
  const endpoints = collectEndpointItems(endpointConfig);
  if (!endpoints.length) return null;
  return {
    version: endpointConfig.version || config.config_version || "remote",
    last_updated: endpointConfig.last_updated || config.last_updated,
    timeout_seconds: endpointConfig.timeout_seconds || config.timeout_seconds || 8,
    endpoints
  };
}

async function writeAllInOneConfig(config, remoteConfigUrl) {
  const nextRoot = userConfigPath();
  const nextRulesDir = userConfigPath("rules");
  const nextEndpointsDir = userConfigPath("network_endpoints");
  const requirements = config.software_requirements || {};
  let rules = 0;

  await fs.mkdir(nextRulesDir, { recursive: true });
  await fs.mkdir(nextEndpointsDir, { recursive: true });

  for (const [product, versions] of Object.entries(requirements)) {
    for (const [version, requirement] of Object.entries(versions || {})) {
      const fileName = `${String(product).toLowerCase()}_${version}.json`;
      const rule = makeRequirementRule(product, version, requirement);
      await fs.writeFile(path.join(nextRulesDir, fileName), JSON.stringify(rule, null, 2), "utf8");
      rules += 1;
    }
  }

  const endpointConfig =
    config.network_endpoints ||
    config.autodesk_endpoints ||
    config.endpoints ||
    null;
  const normalized = normalizeEndpointConfig(endpointConfig, config);
  if (normalized) {
    await fs.writeFile(path.join(nextEndpointsDir, "autodesk.json"), JSON.stringify(normalized, null, 2), "utf8");
  }

  const meta = {
    ok: true,
    format: "all-in-one",
    version: config.config_version || null,
    last_updated: config.last_updated || null,
    updatedAt: new Date().toISOString(),
    rules,
    endpoints: Boolean(normalized),
    source: remoteConfigUrl
  };
  await fs.writeFile(path.join(nextRoot, "metadata.json"), JSON.stringify(meta, null, 2), "utf8");
  return meta;
}

async function updateRemoteConfig(remoteConfigUrl) {
  if (!remoteConfigUrl) {
    return { ok: false, skipped: true, message: "Remote config URL is empty" };
  }
  const manifest = await fetchJson(remoteConfigUrl);
  if (manifest.software_requirements) {
    return writeAllInOneConfig(manifest, remoteConfigUrl);
  }
  const nextRoot = userConfigPath();
  const nextRulesDir = userConfigPath("rules");
  const nextEndpointsDir = userConfigPath("network_endpoints");
  const rules = ruleEntries(manifest);
  const endpointsTarget =
    manifest.endpoints?.url ||
    manifest.endpoints?.path ||
    manifest.endpoints ||
    manifest.network_endpoints?.url ||
    manifest.network_endpoints?.path ||
    manifest.network_endpoints;

  await fs.mkdir(nextRulesDir, { recursive: true });
  await fs.mkdir(nextEndpointsDir, { recursive: true });

  for (const rule of rules) {
    const ruleUrl = resolveRemoteUrl(remoteConfigUrl, rule.url);
    if (!ruleUrl) continue;
    const data = await fetchJson(ruleUrl);
    await fs.writeFile(path.join(nextRulesDir, path.basename(rule.file)), JSON.stringify(data, null, 2), "utf8");
  }

  if (endpointsTarget) {
    const endpointsUrl = resolveRemoteUrl(remoteConfigUrl, endpointsTarget);
    const data = await fetchJson(endpointsUrl);
    await fs.writeFile(path.join(nextEndpointsDir, "autodesk.json"), JSON.stringify(data, null, 2), "utf8");
  }

  const meta = {
    ok: true,
    version: manifest.version || null,
    updatedAt: new Date().toISOString(),
    rules: rules.length,
    endpoints: Boolean(endpointsTarget),
    source: remoteConfigUrl
  };
  await fs.writeFile(path.join(nextRoot, "metadata.json"), JSON.stringify(meta, null, 2), "utf8");
  return meta;
}

async function remoteMetadata() {
  try {
    return JSON.parse(await fs.readFile(userConfigPath("metadata.json"), "utf8"));
  } catch {
    return null;
  }
}

function runPowerShell(script, timeout = 20000) {
  return new Promise((resolve) => {
    execFile(
      "powershell.exe",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
      { timeout, windowsHide: true },
      (error, stdout) => {
        if (error) {
          resolve(null);
          return;
        }
        try {
          resolve(JSON.parse(stdout));
        } catch {
          resolve(null);
        }
      }
    );
  });
}

function runDxdiag() {
  return new Promise((resolve) => {
    const output = path.join(tmpdir(), `autodesk-hwscanner-dxdiag-${Date.now()}.txt`);
    execFile(
      "dxdiag.exe",
      ["/whql:off", "/t", output],
      { timeout: 30000, windowsHide: true },
      async () => {
        try {
          const text = await fs.readFile(output, "utf16le");
          await fs.unlink(output).catch(() => {});
          const match = text.match(/Feature Levels:\s*([^\r\n]+)/i);
          if (!match) {
            resolve(null);
            return;
          }
          const levels = match[1]
            .split(",")
            .map((item) => Number(item.trim().split("_")[0]))
            .filter((item) => Number.isFinite(item));
          resolve(levels.length ? Math.max(...levels) : null);
        } catch {
          resolve(null);
        }
      }
    );
  });
}

function toArray(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

async function discoverOptions() {
  const files = await fs.readdir(await activeRulesDir());
  const versions = {};
  for (const file of files) {
    const match = file.match(/^(\w+)_(\d{4})\.json$/);
    if (!match) continue;
    const [, product, version] = match;
    versions[product] = versions[product] || [];
    versions[product].push(version);
  }
  for (const product of Object.keys(versions)) versions[product].sort();
  return { products: Object.keys(versions).sort(), versions };
}

async function loadRules(product, version) {
  const file = path.join(await activeRulesDir(), `${String(product).toLowerCase()}_${version}.json`);
  return JSON.parse(await fs.readFile(file, "utf8"));
}

function valueByPath(data, keyPath) {
  return keyPath.split(".").reduce((current, key) => current && current[key], data);
}

function windowsMajor(value) {
  const match = String(value || "").match(/(\d+)/);
  return match ? Number(match[1]) : 0;
}

function compare(actual, operator, min, target) {
  if (actual === undefined || actual === null) return false;
  if (operator === ">=num") return Number(actual) >= Number(min);
  if (operator === "in") return Array.isArray(min) && min.includes(actual);
  if (operator === "windows_any") {
    const actualMajor = windowsMajor(actual);
    const allowed = toArray(min).map((item) => String(item).toLowerCase());
    if (allowed.some((item) => item.includes("windows 11")) && actualMajor >= 11) return true;
    if (allowed.some((item) => item.includes("windows 10")) && actualMajor >= 10) return true;
    return false;
  }
  if (operator === ">=str") {
    if (target === "os.version" || String(target).toLowerCase().includes("windows")) {
      return windowsMajor(actual) >= windowsMajor(min);
    }
    return String(actual) >= String(min);
  }
  return false;
}

function evaluate(rules, facts) {
  let hasCriticalFailure = false;
  let hasActionableFailure = false;
  const checks = rules.checks.map((check) => {
    const actual = valueByPath(facts, check.target);
    const passed = compare(actual, check.operator, check.min, check.target);
    const isCritical = check.severity === "critical" || check.blocking === true;
    let status = "PASS";
    if (!passed) {
      status = check.severity === "recommended" ? "WARN" : "FAIL";
      if (isCritical) hasCriticalFailure = true;
      else hasActionableFailure = true;
    }
    return {
      id: check.id,
      target: check.target,
      actual,
      min: check.min,
      recommended: check.recommended,
      unit: check.unit || "",
      severity: check.severity,
      status,
      impact: isCritical ? "Blocks support" : check.severity === "required" ? "Needs upgrade" : "Recommended"
    };
  });
  const overall = hasCriticalFailure ? "Not Supported" : hasActionableFailure ? "Needs Upgrade" : "Ready";
  return { overall, details: { checks, notes: rules.notes || "" } };
}

async function collectHardware() {
  const ps = `
    $ErrorActionPreference = 'SilentlyContinue'
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 Name,MaxClockSpeed
    $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1 Name,AdapterRAM,DriverVersion
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    [pscustomobject]@{
      os = [pscustomobject]@{ Caption = $os.Caption; Version = $os.Version; BuildNumber = $os.BuildNumber; Hostname = $env:COMPUTERNAME }
      cpu = $cpu
      gpu = $gpu
      disk = [pscustomobject]@{ FreeSpace = $disk.FreeSpace; Size = $disk.Size }
    } | ConvertTo-Json -Depth 5
  `;
  const [data, directxFeatureLevel] = await Promise.all([runPowerShell(ps), runDxdiag()]);
  const cpus = os.cpus();
  const gpuRamBytes = Number(data?.gpu?.AdapterRAM || 0);
  return {
    os: {
      version: data?.os?.Caption || os.version(),
      build: data?.os?.BuildNumber,
      hostname: data?.os?.Hostname || os.hostname(),
      arch: os.arch()
    },
    cpu: {
      name: cpus[0]?.model || "Unknown CPU",
      logical_processors: cpus.length,
      speed_ghz: data?.cpu?.MaxClockSpeed ? Math.round((Number(data.cpu.MaxClockSpeed) / 1000) * 10) / 10 : null
    },
    ram: {
      total_gb: Math.round((os.totalmem() / 1024 ** 3) * 10) / 10
    },
    gpu: {
      name: data?.gpu?.Name || "Unknown GPU",
      vram_gb: gpuRamBytes ? Math.round((gpuRamBytes / 1024 ** 3) * 10) / 10 : null,
      directx_feature_level: directxFeatureLevel,
      driver_version: data?.gpu?.DriverVersion
    },
    storage: {
      free_gb: data?.disk?.FreeSpace ? Math.round((Number(data.disk.FreeSpace) / 1024 ** 3) * 10) / 10 : null,
      total_gb: data?.disk?.Size ? Math.round((Number(data.disk.Size) / 1024 ** 3) * 10) / 10 : null
    }
  };
}

async function softwareCheck({ product, version }) {
  const facts = await collectHardware();
  const rules = await loadRules(product, version);
  const result = evaluate(rules, facts);
  return { product, version, ...result, facts };
}

function tcpConnect(host, port, timeout) {
  return new Promise((resolve) => {
    const start = performance.now();
    const socket = net.createConnection({ host, port, timeout: timeout * 1000 });
    const finish = (ok, error = null) => {
      socket.destroy();
      resolve({ ok, elapsed_ms: Math.round((performance.now() - start) * 100) / 100, error });
    };
    socket.once("connect", () => finish(true));
    socket.once("timeout", () => finish(false, "timeout"));
    socket.once("error", (error) => finish(false, error.message));
  });
}

function httpsRequest(url, timeout) {
  return new Promise((resolve) => {
    const start = performance.now();
    const req = https.get(url, { timeout: timeout * 1000, headers: { "User-Agent": "AutodeskHWScanner/1.0" } }, (res) => {
      res.resume();
      resolve({
        ok: res.statusCode >= 200 && res.statusCode < 500,
        status: res.statusCode,
        elapsed_ms: Math.round((performance.now() - start) * 100) / 100,
        error: null
      });
    });
    req.once("timeout", () => {
      req.destroy();
      resolve({ ok: false, status: null, elapsed_ms: Math.round((performance.now() - start) * 100) / 100, error: "timeout" });
    });
    req.once("error", (error) => {
      resolve({ ok: false, status: null, elapsed_ms: Math.round((performance.now() - start) * 100) / 100, error: error.message });
    });
  });
}

async function testEndpoint(endpoint, timeout) {
  const parsed = new URL(endpoint.url);
  const host = parsed.hostname;
  const port = Number(parsed.port || endpoint.port || (parsed.protocol === "https:" ? 443 : 80));
  const checks = endpoint.checks || ["dns", "tcp", "https"];
  const result = {
    id: endpoint.id,
    name: endpoint.name,
    category: endpoint.category,
    url: endpoint.url,
    host,
    port,
    required: endpoint.required !== false,
    checks: {},
    ok: true
  };
  if (checks.includes("dns")) {
    const start = performance.now();
    try {
      const addresses = await dns.lookup(host, { all: true });
      result.checks.dns = { ok: true, addresses: addresses.map((item) => item.address), elapsed_ms: Math.round((performance.now() - start) * 100) / 100, error: null };
    } catch (error) {
      result.checks.dns = { ok: false, addresses: [], elapsed_ms: Math.round((performance.now() - start) * 100) / 100, error: error.message };
    }
  }
  if (checks.includes("tcp")) result.checks.tcp = await tcpConnect(host, port, timeout);
  if (checks.includes("https") && parsed.protocol === "https:") result.checks.https = await httpsRequest(endpoint.url, timeout);
  result.ok = Object.values(result.checks).every((check) => check.ok);
  return result;
}

async function networkCheck() {
  const config = JSON.parse(await fs.readFile(await activeEndpointsFile(), "utf8"));
  const timeout = Number(config.timeout_seconds || 8);
  const results = [];
  for (const endpoint of toArray(config.endpoints)) {
    results.push(await testEndpoint(endpoint, timeout));
  }
  const requiredFailures = results.filter((item) => item.required && !item.ok);
  const optionalFailures = results.filter((item) => !item.required && !item.ok);
  const overall = requiredFailures.length ? "FAIL" : optionalFailures.length ? "WARN" : "PASS";
  return { overall, config_version: config.version, last_updated: config.last_updated, results };
}

function registerIpc() {
  ipcMain.handle("agent:health", () => ({ ok: true, service: "electron-native" }));
  ipcMain.handle("app:info", () => ({
    name: app.getName(),
    version: app.getVersion(),
    packaged: app.isPackaged
  }));
  ipcMain.handle("app:export-pdf", async (event, title = "autodesk-hardware-scanner-report") => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (!win) return { ok: false, message: "No active window" };
    const { canceled, filePath } = await dialog.showSaveDialog(win, {
      title: "Export PDF",
      defaultPath: `${title}.pdf`,
      filters: [{ name: "PDF", extensions: ["pdf"] }]
    });
    if (canceled || !filePath) return { ok: false, canceled: true };
    const data = await win.webContents.printToPDF({
      printBackground: true,
      margins: { marginType: "default" }
    });
    await fs.writeFile(filePath, data);
    return { ok: true, filePath };
  });
  ipcMain.handle("app:open-url", async (_event, url) => {
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) return { ok: false, message: "Unsupported URL" };
      await shell.openExternal(parsed.toString());
      return { ok: true };
    } catch (error) {
      return { ok: false, message: error.message };
    }
  });
  ipcMain.handle("config:get", async () => ({
    settings: await readSettings(),
    metadata: await remoteMetadata()
  }));
  ipcMain.handle("config:set", async (_event, settings) => {
    const current = await readSettings();
    const next = await writeSettings({
      ...current,
      remoteConfigUrl: String(settings?.remoteConfigUrl || "").trim()
    });
    return { settings: next, metadata: await remoteMetadata() };
  });
  ipcMain.handle("config:update", async () => {
    const settings = await readSettings();
    try {
      const metadata = await updateRemoteConfig(settings.remoteConfigUrl);
      return { ok: true, metadata, options: await discoverOptions() };
    } catch (error) {
      return {
        ok: false,
        message: error.message,
        metadata: await remoteMetadata(),
        options: await discoverOptions()
      };
    }
  });
  ipcMain.handle("agent:options", discoverOptions);
  ipcMain.handle("agent:hardware", async () => ({ facts: await collectHardware() }));
  ipcMain.handle("agent:software-check", (_event, body) => softwareCheck(body));
  ipcMain.handle("agent:network-check", networkCheck);
  ipcMain.handle("agent:network-config", async () => JSON.parse(await fs.readFile(await activeEndpointsFile(), "utf8")));
  ipcMain.handle("agent:update-network", async () => updateRemoteConfig((await readSettings()).remoteConfigUrl));
  ipcMain.handle("agent:update-all", async () => updateRemoteConfig((await readSettings()).remoteConfigUrl));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1180,
    height: 760,
    minWidth: 980,
    minHeight: 640,
    title: "Autodesk Hardware Scanner",
    backgroundColor: "#f5f7fb",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (process.env.NODE_ENV === "development") {
    win.loadURL("http://127.0.0.1:5173");
  } else {
    win.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
}

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);
  registerIpc();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
