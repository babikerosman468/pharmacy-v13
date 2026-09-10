#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# PHARMACY V12 — ONESHOT1
# FULL INTERACTIVE WEB PLATFORM
# ============================================================

set -e

APP="$HOME/pharmacy-v12"
WEB="$APP/web"
BACKUP="$APP/backups"
STAMP=$(date +%Y%m%d_%H%M%S)

echo "============================================================"
echo " PHARMACY V12 — ONESHOT1"
echo " FULL INTERACTIVE WEB PLATFORM"
echo "============================================================"

cd "$APP"

# ------------------------------------------------------------
# 1. BACKUP CURRENT WORKING PLATFORM
# ------------------------------------------------------------

mkdir -p "$BACKUP"

tar -czf "$BACKUP/oneshot1_before_${STAMP}.tar.gz" \
    app12.js \
    start.sh \
    web \
    web_server.js \
    start_web.sh \
    data \
    simulation \
    reports \
    exports \
    2>/dev/null || true

echo "[1/8] Backup created:"
echo "$BACKUP/oneshot1_before_${STAMP}.tar.gz"

# ------------------------------------------------------------
# 2. CREATE WEB SERVER
# ------------------------------------------------------------

cat > web_server.js <<'NODE'
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const APP = __dirname;

const DB = {
  MED: path.join(APP, "data/medicines.json"),
  SALES: path.join(APP, "data/sales.json"),
  SUPPLIERS: path.join(APP, "data/suppliers.json"),
  PURCHASES: path.join(APP, "data/purchases.json"),
  AUDIT: path.join(APP, "data/audit.json")
};

function load(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return [];
  }
}

function save(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function json(res, data, code = 200) {
  res.writeHead(code, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*"
  });
  res.end(JSON.stringify(data));
}

function body(req) {
  return new Promise((resolve, reject) => {
    let b = "";
    req.on("data", x => b += x);
    req.on("end", () => {
      try {
        resolve(b ? JSON.parse(b) : {});
      } catch (e) {
        reject(e);
      }
    });
  });
}

function runPython(script) {
  try {
    return execSync(
      `python "${path.join(APP, "simulation", script)}"`,
      { encoding: "utf8", timeout: 120000 }
    );
  } catch (e) {
    return "ERROR: " + (e.stdout || e.message);
  }
}

function summary() {
  const meds = load(DB.MED);
  const sales = load(DB.SALES);

  const revenue = sales.reduce(
    (a, b) => a + Number(b.total || 0), 0
  );

  const inventoryValue = meds.reduce(
    (a, b) =>
      a + Number(b.quantity || 0) * Number(b.price || 0),
    0
  );

  const lowStock = meds.filter(
    m => Number(m.quantity || 0) <= 10
  );

  const now = new Date();

  const expired = meds.filter(m =>
    m.expiry && new Date(m.expiry) < now
  );

  const soon = meds.filter(m => {
    if (!m.expiry) return false;
    const d = new Date(m.expiry);
    const days = (d - now) / 86400000;
    return days >= 0 && days <= 30;
  });

  return {
    medicines: meds.length,
    sales: sales.length,
    revenue,
    inventoryValue,
    lowStock: lowStock.length,
    expired: expired.length,
    expiringSoon: soon.length
  };
}

async function router(req, res) {

  const url = new URL(req.url, "http://localhost");

  // ----------------------------------------------------------
  // CORE
  // ----------------------------------------------------------

  if (url.pathname === "/api/summary") {
    return json(res, summary());
  }

  if (url.pathname === "/api/medicines") {
    const meds = load(DB.MED);
    const q = (url.searchParams.get("q") || "").toLowerCase();

    return json(
      res,
      meds.filter(m =>
        String(m.name || "").toLowerCase().includes(q)
      )
    );
  }

  if (url.pathname === "/api/sales") {
    return json(res, load(DB.SALES));
  }

  if (url.pathname === "/api/alerts") {

    const meds = load(DB.MED);
    const now = new Date();

    return json(res, {
      lowStock: meds.filter(m => Number(m.quantity || 0) <= 10),

      expired: meds.filter(m =>
        m.expiry && new Date(m.expiry) < now
      ),

      expiringSoon: meds.filter(m => {
        if (!m.expiry) return false;
        const d = new Date(m.expiry);
        const days = (d - now) / 86400000;
        return days >= 0 && days <= 30;
      })
    });
  }

  // ----------------------------------------------------------
  // ADD MEDICINE
  // ----------------------------------------------------------

  if (req.method === "POST" &&
      url.pathname === "/api/medicines") {

    const data = await body(req);

    const meds = load(DB.MED);

    const med = {
      id: Date.now(),
      name: data.name,
      quantity: Number(data.quantity || 0),
      price: Number(data.price || 0),
      expiry: data.expiry || ""
    };

    meds.push(med);
    save(DB.MED, meds);

    return json(res, {
      success: true,
      medicine: med
    });
  }

  // ----------------------------------------------------------
  // SELL
  // ----------------------------------------------------------

  if (req.method === "POST" &&
      url.pathname === "/api/sell") {

    const data = await body(req);

    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    const med = meds.find(
      m => String(m.name).toLowerCase() ===
           String(data.name).toLowerCase()
    );

    if (!med)
      return json(res, { error: "Medicine not found" }, 404);

    const qty = Number(data.qty || 0);

    if (qty <= 0)
      return json(res, { error: "Invalid quantity" }, 400);

    if (med.quantity < qty)
      return json(res, { error: "Insufficient stock" }, 400);

    med.quantity -= qty;

    const sale = {
      medicine: med.name,
      qty,
      total: qty * Number(med.price || 0),
      date: new Date().toISOString()
    };

    sales.push(sale);

    save(DB.MED, meds);
    save(DB.SALES, sales);

    return json(res, {
      success: true,
      sale
    });
  }

  // ----------------------------------------------------------
  // ANALYTICS
  // ----------------------------------------------------------

  if (url.pathname === "/api/analytics") {
    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    return json(res, {
      medicineCount: meds.length,
      salesCount: sales.length,
      revenue: sales.reduce(
        (a, b) => a + Number(b.total || 0), 0
      ),
      inventoryValue: meds.reduce(
        (a, b) =>
          a + Number(b.quantity || 0) *
              Number(b.price || 0),
        0
      )
    });
  }

  // ----------------------------------------------------------
  // SUPPLIERS
  // ----------------------------------------------------------

  if (url.pathname === "/api/suppliers") {
    return json(res, load(DB.SUPPLIERS));
  }

  // ----------------------------------------------------------
  // PURCHASES
  // ----------------------------------------------------------

  if (url.pathname === "/api/purchases") {
    return json(res, load(DB.PURCHASES));
  }

  // ----------------------------------------------------------
  // DAILY CASH
  // ----------------------------------------------------------

  if (url.pathname === "/api/cash") {

    const sales = load(DB.SALES);

    const today = new Date().toISOString().slice(0, 10);

    const todaysSales = sales.filter(
      s => String(s.date || "").slice(0, 10) === today
    );

    return json(res, {
      date: today,
      sales: todaysSales.length,
      revenue: todaysSales.reduce(
        (a, b) => a + Number(b.total || 0), 0
      )
    });
  }

  // ----------------------------------------------------------
  // INVENTORY VALUATION
  // ----------------------------------------------------------

  if (url.pathname === "/api/inventory-value") {

    const meds = load(DB.MED);

    return json(res, {
      value: meds.reduce(
        (a, b) =>
          a + Number(b.quantity || 0) *
              Number(b.price || 0),
        0
      )
    });
  }

  // ----------------------------------------------------------
  // PYTHON MODELS
  // ----------------------------------------------------------

  const models = {
    "/api/forecast": "forecast.py",
    "/api/monte-carlo": "inventory_sim.py",
    "/api/reorder-point": "reorder_point.py",
    "/api/safety-stock": "safety_stock.py",
    "/api/expiry-risk": "expiry_risk.py",
    "/api/abc": "abc_analysis.py",
    "/api/eoq": "eoq.py",
    "/api/ai": "ai_dashboard.py"
  };

  if (models[url.pathname]) {
    return json(res, {
      model: url.pathname.replace("/api/", ""),
      output: runPython(models[url.pathname])
    });
  }

  // ----------------------------------------------------------
  // SAS
  // ----------------------------------------------------------

  if (url.pathname === "/api/sas") {

    const file = path.join(
      APP,
      "exports",
      "sas_pipeline.sas"
    );

    return json(res, {
      ready: fs.existsSync(file),
      file
    });
  }

  // ----------------------------------------------------------
  // REPORTS
  // ----------------------------------------------------------

  if (url.pathname === "/api/reports") {

    const files = fs.existsSync(path.join(APP, "reports"))
      ? fs.readdirSync(path.join(APP, "reports"))
      : [];

    return json(res, { files });
  }

  // ----------------------------------------------------------
  // SYSTEM HEALTH
  // ----------------------------------------------------------

  if (url.pathname === "/api/health") {

    return json(res, {
      system: "PHARMACY V12",
      status: "ONLINE",
      node: process.version,
      time: new Date().toISOString(),
      database: {
        medicines: fs.existsSync(DB.MED),
        sales: fs.existsSync(DB.SALES),
        suppliers: fs.existsSync(DB.SUPPLIERS),
        purchases: fs.existsSync(DB.PURCHASES)
      }
    });
  }

  // ----------------------------------------------------------
  // DASHBOARD SNAPSHOT
  // ----------------------------------------------------------

  if (url.pathname === "/api/snapshot") {

    const report = JSON.stringify(summary(), null, 2);

    const file = path.join(
      APP,
      "reports",
      "web_snapshot.txt"
    );

    fs.writeFileSync(file, report);

    return json(res, {
      success: true,
      file
    });
  }

  // ----------------------------------------------------------
  // BATCH IMPORT
  // ----------------------------------------------------------

  if (req.method === "POST" &&
      url.pathname === "/api/batch-import") {

    const data = await body(req);

    const meds = load(DB.MED);

    let imported = 0;

    for (const row of data.rows || []) {

      if (!row.name) continue;

      meds.push({
        id: Date.now() + imported,
        name: row.name,
        quantity: Number(row.quantity || 0),
        price: Number(row.price || 0),
        expiry: row.expiry || ""
      });

      imported++;
    }

    save(DB.MED, meds);

    return json(res, {
      success: true,
      imported
    });
  }

  // ----------------------------------------------------------
  // STATIC WEB FILES
  // ----------------------------------------------------------

  let file;

  if (url.pathname === "/")
    file = path.join(APP, "web/index.html");
  else
    file = path.join(APP, "web", url.pathname);

  if (fs.existsSync(file) &&
      fs.statSync(file).isFile()) {

    const ext = path.extname(file);

    const types = {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".js": "application/javascript; charset=utf-8"
    };

    res.writeHead(200, {
      "Content-Type":
        types[ext] || "text/plain; charset=utf-8"
    });

    return res.end(fs.readFileSync(file));
  }

  json(res, { error: "Not found" }, 404);
}

const server = http.createServer((req, res) => {
  router(req, res).catch(err => {
    json(res, {
      error: err.message
    }, 500);
  });
});

server.listen(8080, "0.0.0.0", () => {
  console.log("");
  console.log("================================================");
  console.log(" PHARMACY V12 WEB PLATFORM");
  console.log(" http://127.0.0.1:8080");
  console.log("================================================");
});
NODE

echo "[2/8] Web server created"

# ------------------------------------------------------------
# 3. HTML
# ------------------------------------------------------------

cat > web/index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>Pharmacy V12 Interactive Platform</title>

<link rel="stylesheet" href="style.css">
</head>

<body>

<header>

<h1>💊 PHARMACY V12</h1>

<p>
Management • Analytics • AI • Decision Support
</p>

<div id="status">
● SYSTEM ONLINE
</div>

</header>

<div class="layout">

<aside>

<button onclick="show('dashboard')">🏠 Dashboard</button>

<button onclick="show('medicines')">💊 Medicines</button>

<button onclick="show('sales')">💰 Sales</button>

<button onclick="show('inventory')">📦 Inventory</button>

<button onclick="show('alerts')">⚠ Alerts</button>

<button onclick="show('analytics')">📊 Analytics</button>

<button onclick="show('suppliers')">🚚 Suppliers</button>

<button onclick="show('purchases')">🛒 Purchases</button>

<hr>

<button onclick="model('forecast')">🔮 Forecast</button>

<button onclick="model('monte-carlo')">
🎲 Monte Carlo Risk
</button>

<button onclick="model('reorder-point')">
📍 Reorder Point
</button>

<button onclick="model('safety-stock')">
🛡 Safety Stock
</button>

<button onclick="model('expiry-risk')">
⏳ Expiry Risk
</button>

<button onclick="model('abc')">
📊 ABC Analysis
</button>

<button onclick="model('eoq')">
📦 EOQ Model
</button>

<button onclick="model('ai')">
🤖 AI Dashboard
</button>

<hr>

<button onclick="show('cash')">💵 Daily Cash</button>

<button onclick="show('reports')">📑 Reports</button>

<button onclick="show('sas')">🧪 SAS</button>

<button onclick="show('health')">⚙ System Health</button>

<button onclick="snapshot()">📸 Snapshot</button>

</aside>

<main>

<section id="dashboard" class="page active">

<h2>Pharmacy Control Center</h2>

<div class="cards">

<div>
<h3>💊 Medicines</h3>
<strong id="medCount">-</strong>
</div>

<div>
<h3>💰 Sales</h3>
<strong id="salesCount">-</strong>
</div>

<div>
<h3>💵 Revenue</h3>
<strong id="revenue">-</strong>
</div>

<div>
<h3>📦 Inventory Value</h3>
<strong id="inventoryValue">-</strong>
</div>

<div>
<h3>⚠ Low Stock</h3>
<strong id="lowStock">-</strong>
</div>

<div>
<h3>⏳ Expired</h3>
<strong id="expired">-</strong>
</div>

<div>
<h3>⏰ Expiring Soon</h3>
<strong id="expiringSoon">-</strong>
</div>

</div>

<div class="quick">

<button onclick="addMedicine()">
➕ Add Medicine
</button>

<button onclick="sellMedicine()">
💰 Sell Medicine
</button>

<button onclick="loadMedicines()">
🔄 Refresh Inventory
</button>

</div>

</section>

<section id="medicines" class="page">

<h2>💊 Medicines</h2>

<div class="toolbar">

<input
id="medicineSearch"
placeholder="Search medicine..."
oninput="loadMedicines()">

<button onclick="addMedicine()">
➕ Add Medicine
</button>

</div>

<div id="medicineTable"></div>

</section>

<section id="sales" class="page">

<h2>💰 Sales</h2>

<div id="salesTable"></div>

</section>

<section id="inventory" class="page">

<h2>📦 Inventory</h2>

<div id="inventoryTable"></div>

</section>

<section id="alerts" class="page">

<h2>⚠ Alerts</h2>

<div id="alertsContent"></div>

</section>

<section id="analytics" class="page">

<h2>📊 Analytics</h2>

<div id="analyticsContent"></div>

</section>

<section id="suppliers" class="page">

<h2>🚚 Suppliers</h2>

<div id="supplierContent"></div>

</section>

<section id="purchases" class="page">

<h2>🛒 Purchases</h2>

<div id="purchaseContent"></div>

</section>

<section id="cash" class="page">

<h2>💵 Daily Cash Report</h2>

<div id="cashContent"></div>

</section>

<section id="reports" class="page">

<h2>📑 Reports</h2>

<div id="reportsContent"></div>

</section>

<section id="sas" class="page">

<h2>🧪 SAS</h2>

<div id="sasContent"></div>

</section>

<section id="health" class="page">

<h2>⚙ System Health</h2>

<div id="healthContent"></div>

</section>

<section id="model" class="page">

<h2 id="modelTitle">Analytics Model</h2>

<pre id="modelOutput"></pre>

</section>

</main>

</div>

<footer>
Pharmacy Management System V12
</footer>

<script src="app.js"></script>

</body>
</html>
HTML

echo "[3/8] Interactive HTML created"

# ------------------------------------------------------------
# 4. CSS
# ------------------------------------------------------------

cat > web/style.css <<'CSS'
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #eef4f8;
  color: #243447;
}

header {
  padding: 20px;
  text-align: center;
  background: #17324d;
  color: white;
}

header h1 {
  margin: 0;
}

#status {
  margin-top: 8px;
  font-weight: bold;
}

.layout {
  display: flex;
  min-height: calc(100vh - 150px);
}

aside {
  width: 240px;
  padding: 15px;
  background: #ffffff;
  border-right: 1px solid #ddd;
}

aside button {
  width: 100%;
  margin: 4px 0;
  padding: 11px;
  border: 0;
  border-radius: 7px;
  background: #edf2f7;
  cursor: pointer;
  text-align: left;
}

aside button:hover {
  background: #dbe7f0;
}

main {
  flex: 1;
  padding: 25px;
}

.page {
  display: none;
}

.page.active {
  display: block;
}

.cards {
  display: grid;
  grid-template-columns:
    repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
}

.cards > div {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px #0001;
}

.cards strong {
  font-size: 28px;
}

.quick {
  margin-top: 25px;
}

.quick button,
.toolbar button {
  padding: 12px 18px;
  margin: 5px;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
}

input {
  padding: 11px;
  width: 280px;
  max-width: 100%;
  border: 1px solid #bbb;
  border-radius: 7px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  margin-top: 15px;
}

th,
td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

th {
  background: #edf2f7;
}

pre {
  background: #111827;
  color: #e5e7eb;
  padding: 20px;
  border-radius: 10px;
  overflow: auto;
  white-space: pre-wrap;
}

footer {
  text-align: center;
  padding: 15px;
  background: #17324d;
  color: white;
}

@media(max-width:800px) {

  .layout {
    display: block;
  }

  aside {
    width: 100%;
    border-right: 0;
  }

  aside button {
    display: inline-block;
    width: auto;
  }

  main {
    padding: 15px;
  }
}
CSS

echo "[4/8] CSS created"

# ------------------------------------------------------------
# 5. FRONTEND JAVASCRIPT
# ------------------------------------------------------------

cat > web/app.js <<'JS'
async function api(url, options) {

  const r = await fetch(url, options);

  if (!r.ok)
    throw new Error(await r.text());

  return r.json();
}

function esc(x) {

  return String(x ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function show(id) {

  document.querySelectorAll(".page")
    .forEach(x => x.classList.remove("active"));

  document.getElementById(id)
    .classList.add("active");

  if (id === "dashboard")
    loadDashboard();

  if (id === "medicines")
    loadMedicines();

  if (id === "sales")
    loadSales();

  if (id === "inventory")
    loadInventory();

  if (id === "alerts")
    loadAlerts();

  if (id === "analytics")
    loadAnalytics();

  if (id === "suppliers")
    loadSuppliers();

  if (id === "purchases")
    loadPurchases();

  if (id === "cash")
    loadCash();

  if (id === "reports")
    loadReports();

  if (id === "sas")
    loadSAS();

  if (id === "health")
    loadHealth();
}

async function loadDashboard() {

  const d = await api("/api/summary");

  medCount.textContent = d.medicines;
  salesCount.textContent = d.sales;
  revenue.textContent = d.revenue;
  inventoryValue.textContent = d.inventoryValue;
  lowStock.textContent = d.lowStock;
  expired.textContent = d.expired;
  expiringSoon.textContent = d.expiringSoon;
}

async function loadMedicines() {

  const q = medicineSearch.value || "";

  const meds = await api(
    "/api/medicines?q=" + encodeURIComponent(q)
  );

  medicineTable.innerHTML = `
  <table>
  <tr>
    <th>Medicine</th>
    <th>Quantity</th>
    <th>Price</th>
    <th>Expiry</th>
    <th>Action</th>
  </tr>

  ${meds.map(m => `
  <tr>
    <td>${esc(m.name)}</td>
    <td>${m.quantity}</td>
    <td>${m.price}</td>
    <td>${esc(m.expiry)}</td>
    <td>
      <button onclick="sellMedicine('${esc(m.name)}')">
      Sell
      </button>
    </td>
  </tr>
  `).join("")}

  </table>`;
}

async function loadSales() {

  const sales = await api("/api/sales");

  salesTable.innerHTML = `
  <table>
  <tr>
    <th>Date</th>
    <th>Medicine</th>
    <th>Quantity</th>
    <th>Total</th>
  </tr>

  ${sales.map(s => `
  <tr>
    <td>${esc(s.date)}</td>
    <td>${esc(s.medicine)}</td>
    <td>${s.qty}</td>
    <td>${s.total}</td>
  </tr>
  `).join("")}

  </table>`;
}

async function loadInventory() {

  const meds = await api("/api/medicines");

  inventoryTable.innerHTML = `
  <table>
  <tr>
    <th>Medicine</th>
    <th>Stock</th>
    <th>Unit Price</th>
    <th>Value</th>
  </tr>

  ${meds.map(m => `
  <tr>
    <td>${esc(m.name)}</td>
    <td>${m.quantity}</td>
    <td>${m.price}</td>
    <td>${Number(m.quantity) * Number(m.price)}</td>
  </tr>
  `).join("")}

  </table>`;
}

async function loadAlerts() {

  const a = await api("/api/alerts");

  alertsContent.innerHTML = `
  <h3>Low Stock: ${a.lowStock.length}</h3>

  ${a.lowStock.map(m =>
    `<p>⚠ ${esc(m.name)} — ${m.quantity}</p>`
  ).join("")}

  <h3>Expired: ${a.expired.length}</h3>

  ${a.expired.map(m =>
    `<p>🔴 ${esc(m.name)} — ${esc(m.expiry)}</p>`
  ).join("")}

  <h3>Expiring Soon: ${a.expiringSoon.length}</h3>

  ${a.expiringSoon.map(m =>
    `<p>🟠 ${esc(m.name)} — ${esc(m.expiry)}</p>`
  ).join("")}
  `;
}

async function loadAnalytics() {

  const d = await api("/api/analytics");

  analyticsContent.innerHTML = `
  <h3>Medicines: ${d.medicineCount}</h3>
  <h3>Sales: ${d.salesCount}</h3>
  <h3>Revenue: ${d.revenue}</h3>
  <h3>Inventory Value: ${d.inventoryValue}</h3>
  `;
}

async function loadSuppliers() {

  const d = await api("/api/suppliers");

  supplierContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadPurchases() {

  const d = await api("/api/purchases");

  purchaseContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadCash() {

  const d = await api("/api/cash");

  cashContent.innerHTML = `
  <h3>Date: ${d.date}</h3>
  <h3>Sales: ${d.sales}</h3>
  <h3>Revenue: ${d.revenue}</h3>
  `;
}

async function loadReports() {

  const d = await api("/api/reports");

  reportsContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadSAS() {

  const d = await api("/api/sas");

  sasContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadHealth() {

  const d = await api("/api/health");

  healthContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function model(name) {

  show("model");

  modelTitle.textContent =
    name.toUpperCase();

  modelOutput.textContent =
    "Running " + name + "...\n";

  try {

    const d = await api("/api/" + name);

    modelOutput.textContent = d.output;

  } catch (e) {

    modelOutput.textContent =
      "ERROR\n" + e.message;
  }
}

async function addMedicine() {

  const name = prompt("Medicine name:");

  if (!name) return;

  const quantity =
    prompt("Quantity:", "0");

  const price =
    prompt("Price:", "0");

  const expiry =
    prompt("Expiry YYYY-MM-DD:", "");

  const r = await api("/api/medicines", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      name,
      quantity,
      price,
      expiry
    })
  });

  alert(
    r.success
      ? "Medicine added successfully"
      : "Error"
  );

  loadDashboard();
  loadMedicines();
}

async function sellMedicine(name) {

  if (!name)
    name = prompt("Medicine name:");

  if (!name) return;

  const qty =
    prompt("Quantity to sell:", "1");

  if (!qty) return;

  const r = await api("/api/sell", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      name,
      qty
    })
  });

  if (r.error) {

    alert(r.error);
    return;
  }

  alert(
    "Sale completed\nTotal: " +
    r.sale.total
  );

  loadDashboard();
  loadMedicines();
}

async function snapshot() {

  const r = await api("/api/snapshot");

  alert(
    r.success
      ? "Dashboard snapshot created"
      : "Snapshot failed"
  );
}

loadDashboard();
JS

echo "[5/8] Frontend JavaScript created"

# ------------------------------------------------------------
# 6. START SCRIPT
# ------------------------------------------------------------

cat > start_web.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/pharmacy-v12"

echo "============================================================"
echo " PHARMACY V12 WEB PLATFORM"
echo "============================================================"
echo "URL: http://127.0.0.1:8080"
echo ""
echo "Press Ctrl+C to stop the web server."
echo ""

node web_server.js
SH

chmod +x start_web.sh

echo "[6/8] Start script ready"

# ------------------------------------------------------------
# 7. VALIDATE
# ------------------------------------------------------------

echo "[7/8] Validating..."

node --check web_server.js
node --check web/app.js

echo "Node syntax: OK"

# ------------------------------------------------------------
# 8. SUMMARY
# ------------------------------------------------------------

echo "[8/8] ONESHOT1 COMPLETE"

echo ""
echo "============================================================"
echo " PHARMACY V12 — FULL INTERACTIVE PLATFORM READY"
echo "============================================================"
echo ""
echo "Core preserved:"
echo "  app12.js                 ✅"
echo ""
echo "Interactive modules:"
echo "  Medicines               ✅"
echo "  Sales                   ✅"
echo "  Inventory               ✅"
echo "  Alerts                  ✅"
echo "  Analytics               ✅"
echo "  Suppliers               ✅"
echo "  Purchases               ✅"
echo "  Daily Cash              ✅"
echo "  Forecast                ✅"
echo "  Monte Carlo Risk        ✅"
echo "  Reorder Point           ✅"
echo "  Safety Stock            ✅"
echo "  Expiry Risk             ✅"
echo "  ABC Analysis            ✅"
echo "  EOQ                     ✅"
echo "  AI Dashboard            ✅"
echo "  Reports                 ✅"
echo "  SAS                     ✅"
echo "  Dashboard Snapshot      ✅"
echo "  Batch Import API        ✅"
echo "  System Health           ✅"
echo ""
echo "Backup:"
echo "$BACKUP/oneshot1_before_${STAMP}.tar.gz"
echo ""
echo "Start:"
echo "cd $APP"
echo "./start_web.sh"
echo ""
echo "Open:"
echo "http://127.0.0.1:8080"
echo ""
echo "============================================================"
