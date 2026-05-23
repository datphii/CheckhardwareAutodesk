import {
  Activity,
  CheckCircle2,
  Cpu,
  Download,
  ExternalLink,
  FileSearch,
  HardDrive,
  HelpCircle,
  Languages,
  Network,
  PlayCircle,
  RefreshCw,
  Server,
  ShieldAlert,
  XCircle
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const emptyOptions = { products: [], versions: {} };

const productDisplayNames = {
  autocad: "AutoCAD",
  inventor: "Inventor Professional",
  revit: "Revit",
  civil_3d: "Civil 3D",
  civil3d: "Civil 3D",
  navisworks: "Navisworks Manage",
  infraworks: "InfraWorks"
};

function displayProductName(product) {
  const key = String(product || "").toLowerCase();
  if (productDisplayNames[key]) return productDisplayNames[key];
  return String(product || "")
    .replace(/[_-]+/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

const copy = {
  en: {
    appName: "Autodesk Scanner",
    appTag: "Hardware & license readiness",
    title: "Workstation Readiness",
    subtitle: "Run one full readiness check, then review hardware and network details by tab.",
    hardware: "Hardware",
    network: "Network",
    help: "Help",
    hardwareTitle: "Hardware Compatibility",
    hardwareText: "Compare this workstation with Autodesk requirement rules by product version.",
    networkTitle: "Autodesk Connectivity",
    networkText: "Check DNS, TCP and HTTPS reachability for Autodesk licensing and identity endpoints.",
    product: "Product",
    version: "Version",
    runAll: "Run Full Check",
    runningAll: "Checking...",
    runHardwareOnly: "Scan Hardware",
    runNetworkOnly: "Check Network",
    exportPdf: "Export PDF",
    language: "Tiếng Việt",
    agentOnline: "Agent online",
    agentStarting: "Agent starting",
    check: "Check",
    actual: "Actual",
    minimum: "Minimum",
    recommended: "Recommended",
    impact: "Impact",
    status: "Status",
    endpoint: "Endpoint",
    category: "Category",
    helpTitle: "Help",
    versionInfo: "Version in use",
    configExplain: "Config is the JSON data that defines product rules and Autodesk network endpoints. The update screen was removed from the ribbon because it is an admin function, not a normal user workflow.",
    noResult: "Run a full check before exporting a PDF.",
    exportDone: "PDF exported.",
    exportCanceled: "PDF export canceled.",
    startupSync: "Loading remote configuration...",
    loadingRule: "Loading product rule file",
    hardwareScan: "Collecting Windows hardware data",
    dxdiag: "Running DirectX diagnostics",
    evaluating: "Evaluating hardware checks",
    hardwareDone: "Hardware check completed",
    endpointConfig: "Loading endpoint config",
    dns: "Checking DNS resolution",
    tcp: "Checking TCP ports",
    https: "Checking HTTPS responses",
    networkDone: "Network check completed",
    remoteReady: "Remote config ready",
    remoteFallback: "Remote config unavailable. Using cached or bundled config.",
    remoteHelp: "Use a raw GitHub URL that points to manifest.json or an all-in-one Autodesk spec JSON. The app downloads the latest config before each full check.",
    dataTitle: "Check Data In Use",
    dataSource: "Data source",
    dataVersion: "Data version",
    dataDate: "Data date",
    dataLoadedAt: "Last loaded by app",
    dataRules: "Test sets loaded",
    dataSourceRemote: "GitHub file",
    dataSourceFallback: "Built-in backup",
    notLoaded: "Not loaded yet"
  },
  vi: {
    appName: "Autodesk Scanner",
    appTag: "Kiểm tra máy & license",
    title: "Kiểm tra máy trạm",
    subtitle: "Bấm một nút để kiểm tra tổng thể, sau đó xem chi tiết phần cứng và mạng theo từng tab.",
    hardware: "Phần cứng",
    network: "Mạng",
    help: "Help",
    hardwareTitle: "Tương thích phần cứng",
    hardwareText: "So sánh máy hiện tại với bộ rule Autodesk theo sản phẩm và phiên bản.",
    networkTitle: "Kết nối Autodesk",
    networkText: "Kiểm tra DNS, TCP và HTTPS tới các endpoint license và identity của Autodesk.",
    product: "Sản phẩm",
    version: "Phiên bản",
    runAll: "Chạy kiểm tra tổng thể",
    runningAll: "Đang kiểm tra...",
    runHardwareOnly: "Quét cấu hình",
    runNetworkOnly: "Kiểm tra mạng",
    exportPdf: "Xuất PDF",
    language: "English",
    agentOnline: "Agent sẵn sàng",
    agentStarting: "Agent đang khởi động",
    check: "Hạng mục",
    actual: "Thực tế",
    minimum: "Tối thiểu",
    recommended: "Khuyến nghị",
    impact: "Tác động",
    status: "Trạng thái",
    endpoint: "Endpoint",
    category: "Nhóm",
    helpTitle: "Help",
    versionInfo: "Phiên bản đang sử dụng",
    configExplain: "Config là các file JSON định nghĩa rule sản phẩm và danh sách endpoint Autodesk. Màn hình update Config đã được bỏ khỏi ribbon vì đây là chức năng quản trị, không phải thao tác thường ngày của user.",
    noResult: "Hãy chạy kiểm tra tổng thể trước khi xuất PDF.",
    exportDone: "Đã xuất PDF.",
    exportCanceled: "Đã hủy xuất PDF.",
    startupSync: "Đang tải cấu hình từ xa...",
    loadingRule: "Đang tải file rule sản phẩm",
    hardwareScan: "Đang đọc thông tin phần cứng Windows",
    dxdiag: "Đang chạy chẩn đoán DirectX",
    evaluating: "Đang đánh giá các hạng mục",
    hardwareDone: "Đã hoàn tất kiểm tra phần cứng",
    endpointConfig: "Đang tải file endpoint",
    dns: "Đang kiểm tra DNS",
    tcp: "Đang kiểm tra cổng TCP",
    https: "Đang kiểm tra HTTPS",
    networkDone: "Đã hoàn tất kiểm tra mạng",
    remoteReady: "Cấu hình từ xa đã sẵn sàng",
    remoteFallback: "Không tải được cấu hình từ xa. Đang dùng cache hoặc cấu hình đóng gói.",
    remoteHelp: "Dùng raw GitHub URL trỏ tới file manifest.json hoặc file Autodesk spec JSON all-in-one. App sẽ tải cấu hình mới nhất trước mỗi lần kiểm tra tổng thể.",
    dataTitle: "Dữ liệu kiểm tra đang dùng",
    dataSource: "Nguồn dữ liệu",
    dataVersion: "Phiên bản dữ liệu",
    dataDate: "Ngày cập nhật dữ liệu",
    dataLoadedAt: "Lần gần nhất app tải",
    dataRules: "Số bộ kiểm tra đã tải",
    dataSourceRemote: "File GitHub",
    dataSourceFallback: "Dữ liệu dự phòng trong app",
    notLoaded: "Chưa tải"
  }
};

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function statusTone(status) {
  if (["Ready", "PASS"].includes(status) || status === true) return "ok";
  if (["Needs Upgrade", "WARN"].includes(status)) return "warn";
  return "fail";
}

function StatusBadge({ value }) {
  const tone = statusTone(value);
  const Icon = tone === "ok" ? CheckCircle2 : tone === "warn" ? ShieldAlert : XCircle;
  return (
    <span className={`status ${tone}`}>
      <Icon size={16} />
      {String(value)}
    </span>
  );
}

function ProgressLine({ progress }) {
  if (!progress) return null;
  return (
    <div className="progressBox" aria-live="polite">
      <div className="progressMeta">
        <span>{progress.message}</span>
        <strong>{progress.percent}%</strong>
      </div>
      <div className="progressTrack">
        <div style={{ width: `${progress.percent}%` }} />
      </div>
      <div className="runningFile">
        <FileSearch size={15} />
        <span>{progress.file}</span>
      </div>
    </div>
  );
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="metric">
      <Icon size={18} />
      <div>
        <span>{label}</span>
        <strong>{value ?? "N/A"}</strong>
      </div>
    </div>
  );
}

function HardwareSummary({ facts }) {
  if (!facts) return null;
  return (
    <div className="metrics">
      <Metric icon={Cpu} label="CPU" value={facts.cpu?.name || `${facts.cpu?.logical_processors || "N/A"} threads`} />
      <Metric icon={Activity} label="RAM" value={`${facts.ram?.total_gb ?? "N/A"} GB`} />
      <Metric icon={HardDrive} label="Storage Free" value={`${facts.storage?.free_gb ?? "N/A"} GB`} />
      <Metric icon={Server} label="GPU VRAM" value={`${facts.gpu?.vram_gb ?? "N/A"} GB`} />
    </div>
  );
}

function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

async function runHardwareCheck({ t, product, version, setHardwareState }) {
  const ruleFile = `scanner/rules/${String(product).toLowerCase()}_${version}.json`;
  const steps = [
    { percent: 12, message: t.loadingRule, file: ruleFile },
    { percent: 32, message: t.hardwareScan, file: "Win32_OperatingSystem, Win32_VideoController, Win32_LogicalDisk" },
    { percent: 58, message: t.dxdiag, file: "%TEMP%/autodesk-hwscanner-dxdiag-*.txt" },
    { percent: 78, message: t.evaluating, file: ruleFile }
  ];
  setHardwareState((current) => ({ ...current, loading: true, result: null, progress: steps[0] }));
  let stepIndex = 0;
  const timer = window.setInterval(() => {
    stepIndex = Math.min(stepIndex + 1, steps.length - 1);
    setHardwareState((current) => ({ ...current, progress: steps[stepIndex] }));
  }, 1400);
  try {
    await delay(80);
    const result = await window.autodeskAgent.softwareCheck({ product, version });
    setHardwareState({ loading: false, result, progress: { percent: 100, message: t.hardwareDone, file: ruleFile } });
  } finally {
    window.clearInterval(timer);
    setHardwareState((current) => ({ ...current, loading: false }));
  }
}

async function runNetworkCheck({ t, setNetworkState }) {
  const endpointFile = "scanner/network_endpoints/autodesk.json";
  const steps = [
    { percent: 15, message: t.endpointConfig, file: endpointFile },
    { percent: 36, message: t.dns, file: endpointFile },
    { percent: 62, message: t.tcp, file: endpointFile },
    { percent: 84, message: t.https, file: endpointFile }
  ];
  setNetworkState((current) => ({ ...current, loading: true, result: null, progress: steps[0] }));
  let stepIndex = 0;
  const timer = window.setInterval(() => {
    stepIndex = Math.min(stepIndex + 1, steps.length - 1);
    setNetworkState((current) => ({ ...current, progress: steps[stepIndex] }));
  }, 1400);
  try {
    await delay(80);
    const result = await window.autodeskAgent.networkCheck();
    setNetworkState({ loading: false, result, progress: { percent: 100, message: t.networkDone, file: endpointFile } });
  } finally {
    window.clearInterval(timer);
    setNetworkState((current) => ({ ...current, loading: false }));
  }
}

function SoftwarePanel({ t, options, product, setProduct, version, setVersion, state, onRunHardware, disabled }) {
  const versions = options.versions[product] || [];

  return (
    <section className="panel report-section">
      <div className="panelHeader">
        <div>
          <h2>{t.hardwareTitle}</h2>
          <p>{t.hardwareText}</p>
        </div>
        {state.result?.overall && <StatusBadge value={state.result.overall} />}
      </div>

      <div className="toolbar no-print compactToolbar">
        <label>
          {t.product}
          <select value={product} onChange={(event) => setProduct(event.target.value)} disabled={state.loading}>
            {options.products.map((item) => (
              <option key={item} value={item}>
                {displayProductName(item)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t.version}
          <select value={version} onChange={(event) => setVersion(event.target.value)} disabled={state.loading}>
            {versions.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <button className="primary" onClick={onRunHardware} disabled={!product || !version || state.loading || disabled}>
          <RefreshCw size={16} className={state.loading ? "spin" : ""} />
          {t.runHardwareOnly}
        </button>
      </div>

      <ProgressLine progress={state.progress} />
      <HardwareSummary facts={state.result?.facts} />

      {state.result && (
        <table>
          <thead>
            <tr>
              <th>{t.check}</th>
              <th>{t.actual}</th>
              <th>{t.minimum}</th>
              <th>{t.recommended}</th>
              <th>{t.impact}</th>
              <th>{t.status}</th>
            </tr>
          </thead>
          <tbody>
            {state.result.details.checks.map((check) => (
              <tr key={check.id}>
                <td>
                  <strong>{check.id}</strong>
                  <span>{check.target}</span>
                </td>
                <td>{`${check.actual ?? "N/A"} ${check.unit || ""}`}</td>
                <td>{`${check.min ?? "N/A"} ${check.unit || ""}`}</td>
                <td>{`${check.recommended ?? "N/A"} ${check.unit || ""}`}</td>
                <td>{check.impact || check.severity}</td>
                <td>
                  <StatusBadge value={check.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

function NetworkPanel({ t, state, onRunNetwork, disabled }) {
  async function openEndpoint(url) {
    await window.autodeskAgent.openUrl(url);
  }

  return (
    <section className="panel report-section">
      <div className="panelHeader">
        <div>
          <h2>{t.networkTitle}</h2>
          <p>{t.networkText}</p>
        </div>
        {state.result?.overall && <StatusBadge value={state.result.overall} />}
      </div>

      <div className="toolbar no-print compactToolbar">
        <button className="primary" onClick={onRunNetwork} disabled={state.loading || disabled}>
          <Network size={16} />
          {t.runNetworkOnly}
        </button>
        {state.result?.config_version && <span className="muted">Config {state.result.config_version}</span>}
      </div>
      <ProgressLine progress={state.progress} />

      {state.result && (
        <table>
          <thead>
            <tr>
              <th>{t.endpoint}</th>
              <th>{t.category}</th>
              <th>DNS</th>
              <th>TCP</th>
              <th>HTTPS</th>
              <th>{t.status}</th>
            </tr>
          </thead>
          <tbody>
            {state.result.results.map((endpoint) => (
              <tr key={endpoint.id}>
                <td>
                  <strong>{endpoint.name}</strong>
                  <button className="linkButton" onClick={() => openEndpoint(endpoint.url)}>
                    <span>{endpoint.url}</span>
                    <ExternalLink size={13} />
                  </button>
                </td>
                <td>{endpoint.category}</td>
                <td>{endpoint.checks.dns?.ok ? `${endpoint.checks.dns.elapsed_ms} ms` : endpoint.checks.dns?.error}</td>
                <td>{endpoint.checks.tcp?.ok ? `${endpoint.checks.tcp.elapsed_ms} ms` : endpoint.checks.tcp?.error}</td>
                <td>{endpoint.checks.https?.status || endpoint.checks.https?.error || ""}</td>
                <td>
                  <StatusBadge value={endpoint.ok ? "PASS" : "FAIL"} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

function HelpPanel({ t, appInfo, exportStatus, remoteStatus, remoteMetadata }) {
  const hasRemoteData = Boolean(remoteMetadata?.source);
  return (
    <section className="panel">
      <div className="panelHeader">
        <div>
          <h2>{t.helpTitle}</h2>
          <p>{t.configExplain}</p>
        </div>
      </div>
      <div className="helpGrid">
        <div>
          <span>{t.versionInfo}</span>
          <strong>{appInfo?.version || "0.1.0"}</strong>
        </div>
        <div>
          <span>Build</span>
          <strong>{appInfo?.packaged ? "Packaged EXE" : "Development"}</strong>
        </div>
      </div>
      <div className="dataSummary">
        <h3>{t.dataTitle}</h3>
        <div>
          <span>{t.dataSource}</span>
          <strong>{hasRemoteData ? t.dataSourceRemote : t.dataSourceFallback}</strong>
        </div>
        <div>
          <span>{t.dataVersion}</span>
          <strong>{remoteMetadata?.version || t.notLoaded}</strong>
        </div>
        <div>
          <span>{t.dataDate}</span>
          <strong>{remoteMetadata?.last_updated || t.notLoaded}</strong>
        </div>
        <div>
          <span>{t.dataLoadedAt}</span>
          <strong>{remoteMetadata?.updatedAt ? formatDateTime(remoteMetadata.updatedAt) : t.notLoaded}</strong>
        </div>
        <div>
          <span>{t.dataRules}</span>
          <strong>{remoteMetadata?.rules ?? t.notLoaded}</strong>
        </div>
      </div>
      {remoteStatus && <p className="muted no-print">{remoteStatus}</p>}
      {exportStatus && <p className="muted">{exportStatus}</p>}
    </section>
  );
}

export function App() {
  const [activeTab, setActiveTab] = useState("hardware");
  const [language, setLanguage] = useState("vi");
  const [agentOnline, setAgentOnline] = useState(false);
  const [options, setOptions] = useState(emptyOptions);
  const [product, setProduct] = useState("");
  const [version, setVersion] = useState("");
  const [appInfo, setAppInfo] = useState(null);
  const [exportStatus, setExportStatus] = useState("");
  const [remoteStatus, setRemoteStatus] = useState("");
  const [remoteMetadata, setRemoteMetadata] = useState(null);
  const [runningAll, setRunningAll] = useState(false);
  const [hardwareState, setHardwareState] = useState({ loading: false, progress: null, result: null });
  const [networkState, setNetworkState] = useState({ loading: false, progress: null, result: null });
  const t = copy[language];
  const hasResult = Boolean(hardwareState.result || networkState.result);
  const tabs = useMemo(
    () => [
      { id: "hardware", label: t.hardware, icon: Cpu },
      { id: "network", label: t.network, icon: Network },
      { id: "help", label: t.help, icon: HelpCircle }
    ],
    [t]
  );

  async function syncRemoteOptions(currentProduct = product, currentVersion = version) {
    let selectedProduct = currentProduct;
    let selectedVersion = currentVersion;
    const update = await window.autodeskAgent.updateConfig();
      if (update.ok) {
        setRemoteStatus(t.remoteReady);
        setRemoteMetadata(update.metadata);
        setOptions(update.options);
      } else if (update.message) {
        setRemoteStatus(`${t.remoteFallback} ${update.message}`);
        setRemoteMetadata(update.metadata || null);
        setOptions(update.options);
      }
      if (update.options?.products?.length && !update.options.products.includes(selectedProduct)) {
        selectedProduct = update.options.products[0];
        selectedVersion = update.options.versions[selectedProduct]?.[0] || "";
        setProduct(selectedProduct);
        setVersion(selectedVersion);
      } else if (update.options?.versions?.[selectedProduct] && !update.options.versions[selectedProduct].includes(selectedVersion)) {
        selectedVersion = update.options.versions[selectedProduct][0] || "";
        setVersion(selectedVersion);
      }
    return { selectedProduct, selectedVersion };
  }

  async function runHardwareOnly() {
    if (!product || !version || runningAll || hardwareState.loading) return;
    const { selectedProduct, selectedVersion } = await syncRemoteOptions();
    if (!selectedProduct || !selectedVersion) return;
    await runHardwareCheck({ t, product: selectedProduct, version: selectedVersion, setHardwareState });
  }

  async function runNetworkOnly() {
    if (runningAll || networkState.loading) return;
    await syncRemoteOptions();
    await runNetworkCheck({ t, setNetworkState });
  }

  async function runFullCheck() {
    if (!product || !version || runningAll) return;
    setRunningAll(true);
    setActiveTab("hardware");
    try {
      const { selectedProduct, selectedVersion } = await syncRemoteOptions();
      if (!selectedProduct || !selectedVersion) return;
      await runHardwareCheck({ t, product: selectedProduct, version: selectedVersion, setHardwareState });
      setActiveTab("network");
      await runNetworkCheck({ t, setNetworkState });
    } finally {
      setRunningAll(false);
    }
  }

  async function exportPdf() {
    if (!hasResult) {
      setExportStatus(t.noResult);
      return;
    }
    const result = await window.autodeskAgent.exportPdf(`autodesk-hardware-scanner-${activeTab}`);
    setExportStatus(result.ok ? t.exportDone : t.exportCanceled);
  }

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      setRemoteStatus(t.startupSync);
      const [health, info, config] = await Promise.all([
        window.autodeskAgent.health(),
        window.autodeskAgent.appInfo(),
        window.autodeskAgent.getConfig()
      ]);
      const update = await window.autodeskAgent.updateConfig();
      const nextOptions = update.options || (await window.autodeskAgent.options());
      if (cancelled) return;
      setAgentOnline(Boolean(health.ok));
      setOptions(nextOptions);
      setAppInfo(info);
      setRemoteMetadata(update.metadata || config.metadata || null);
      if (update.ok) setRemoteStatus(`${t.remoteReady}: ${update.metadata?.updatedAt || ""}`);
      else if (update.message) setRemoteStatus(`${t.remoteFallback} ${update.message}`);
      else if (config.metadata?.updatedAt) setRemoteStatus(`${t.remoteReady}: ${config.metadata.updatedAt}`);
      const firstProduct = nextOptions.products[0] || "";
      setProduct(firstProduct);
      setVersion(nextOptions.versions[firstProduct]?.[0] || "");
    }

    boot().catch(() => {
      if (!cancelled) setAgentOnline(false);
    });
    return () => {
      cancelled = true;
    };
  }, [t.remoteReady]);

  useEffect(() => {
    const versions = options.versions[product] || [];
    if (!versions.includes(version)) setVersion(versions[0] || "");
  }, [options, product, version]);

  return (
    <div className="app">
      <aside className="no-print">
        <div className="brand">
          <Server size={22} />
          <div>
            <strong>{t.appName}</strong>
            <span>{t.appTag}</span>
          </div>
        </div>
        <nav>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} className={activeTab === tab.id ? "active" : ""} onClick={() => setActiveTab(tab.id)}>
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </nav>
        <div className={`agent ${agentOnline ? "ok" : "fail"}`}>
          <span />
          {agentOnline ? t.agentOnline : t.agentStarting}
        </div>
      </aside>

      <main>
        <header>
          <div>
            <h1>{t.title}</h1>
            <p>{t.subtitle}</p>
          </div>
          <div className="headerActions no-print">
            <button className="primary runAllButton" onClick={runFullCheck} disabled={!product || !version || runningAll}>
              {runningAll ? <RefreshCw size={16} className="spin" /> : <PlayCircle size={16} />}
              {runningAll ? t.runningAll : t.runAll}
            </button>
            <button onClick={() => setLanguage(language === "vi" ? "en" : "vi")}>
              <Languages size={16} />
              {t.language}
            </button>
            <button onClick={exportPdf} disabled={!hasResult}>
              <Download size={16} />
              {t.exportPdf}
            </button>
          </div>
        </header>

        {activeTab === "hardware" && (
          <SoftwarePanel
            t={t}
            options={options}
            product={product}
            setProduct={setProduct}
            version={version}
            setVersion={setVersion}
            state={hardwareState}
            onRunHardware={runHardwareOnly}
            disabled={runningAll}
          />
        )}
        {activeTab === "network" && <NetworkPanel t={t} state={networkState} onRunNetwork={runNetworkOnly} disabled={runningAll} />}
        {activeTab === "help" && (
          <HelpPanel
            t={t}
            appInfo={appInfo}
            exportStatus={exportStatus}
            remoteStatus={remoteStatus}
            remoteMetadata={remoteMetadata}
          />
        )}
      </main>
    </div>
  );
}
