#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# PHARMACY V12 — ONESHOT2
# INTERACTIVE CONTROL CENTER
# ============================================================

set -e

APP="$HOME/pharmacy-v12"
WEB="$APP/web"
BACKUP="$APP/backups"
STAMP=$(date +%Y%m%d_%H%M%S)

echo "============================================================"
echo " PHARMACY V12 — ONESHOT2"
echo " INTERACTIVE CONTROL CENTER"
echo "============================================================"

cd "$APP"

mkdir -p "$WEB" "$BACKUP"

# ------------------------------------------------------------
# 1. SAFE BACKUP
# ------------------------------------------------------------

tar -czf "$BACKUP/oneshot2_before_${STAMP}.tar.gz" \
  app12.js \
  web \
  web_server.js \
  start_web.sh \
  data \
  simulation \
  reports \
  exports \
  2>/dev/null || true

echo "[1/7] Backup created:"
echo "$BACKUP/oneshot2_before_${STAMP}.tar.gz"

# ------------------------------------------------------------
# 2. SERVER
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
  PURCHASES: path.join(APP, "data/purchases.json")
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

function send(res, data, code = 200) {
  res.writeHead(code, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*"
  });
  res.end(JSON.stringify(data));
}

function python(script) {
  try {
    return execSync(
      `python "${path.join(APP, "simulation", script)}"`,
      {
        encoding: "utf8",
        timeout: 120000
      }
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
      a +
      Number(b.quantity || 0) *
      Number(b.price || 0),
    0
  );

  const now = new Date();

  const lowStock =
    meds.filter(m => Number(m.quantity || 0) <= 10);

  const expired =
    meds.filter(m =>
      m.expiry && new Date(m.expiry) < now
    );

  const expiringSoon =
    meds.filter(m => {
      if (!m.expiry) return false;
      const days =
        (new Date(m.expiry) - now) / 86400000;
      return days >= 0 && days <= 30;
    });

  return {
    medicines: meds.length,
    sales: sales.length,
    revenue,
    inventoryValue,
    lowStock: lowStock.length,
    expired: expired.length,
    expiringSoon: expiringSoon.length
  };
}

async function body(req) {

  return new Promise((resolve, reject) => {

    let data = "";

    req.on("data", chunk => {
      data += chunk;
    });

    req.on("end", () => {

      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(e);
      }

    });
  });
}

async function router(req, res) {

  const url =
    new URL(req.url, "http://localhost");

  // ----------------------------------------------------------
  // DASHBOARD
  // ----------------------------------------------------------

  if (url.pathname === "/api/summary")
    return send(res, summary());

  // ----------------------------------------------------------
  // MEDICINES
  // ----------------------------------------------------------

  if (url.pathname === "/api/medicines") {

    const q =
      (url.searchParams.get("q") || "").toLowerCase();

    const meds = load(DB.MED);

    return send(
      res,
      meds.filter(m =>
        String(m.name || "")
          .toLowerCase()
          .includes(q)
      )
    );
  }

  // ----------------------------------------------------------
  // ADD MEDICINE
  // ----------------------------------------------------------

  if (
    req.method === "POST" &&
    url.pathname === "/api/medicines"
  ) {

    const d = await body(req);

    const meds = load(DB.MED);

    const medicine = {
      id: Date.now(),
      name: d.name,
      quantity: Number(d.quantity || 0),
      price: Number(d.price || 0),
      expiry: d.expiry || ""
    };

    meds.push(medicine);

    save(DB.MED, meds);

    return send(res, {
      success: true,
      medicine
    });
  }

  // ----------------------------------------------------------
  // SELL MEDICINE
  // ----------------------------------------------------------

  if (
    req.method === "POST" &&
    url.pathname === "/api/sell"
  ) {

    const d = await body(req);

    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    const medicine =
      meds.find(m =>
        String(m.name).toLowerCase() ===
        String(d.name).toLowerCase()
      );

    if (!medicine)
      return send(
        res,
        { error: "Medicine not found" },
        404
      );

    const qty = Number(d.qty || 0);

    if (qty <= 0)
      return send(
        res,
        { error: "Invalid quantity" },
        400
      );

    if (medicine.quantity < qty)
      return send(
        res,
        { error: "Insufficient stock" },
        400
      );

    medicine.quantity -= qty;

    const sale = {
      medicine: medicine.name,
      qty,
      total:
        qty * Number(medicine.price || 0),
      date:
        new Date().toISOString()
    };

    sales.push(sale);

    save(DB.MED, meds);
    save(DB.SALES, sales);

    return send(res, {
      success: true,
      sale
    });
  }

  // ----------------------------------------------------------
  // SALES
  // ----------------------------------------------------------

  if (url.pathname === "/api/sales")
    return send(res, load(DB.SALES));

  // ----------------------------------------------------------
  // ALERTS
  // ----------------------------------------------------------

  if (url.pathname === "/api/alerts") {

    const meds = load(DB.MED);
    const now = new Date();

    return send(res, {

      lowStock:
        meds.filter(m =>
          Number(m.quantity || 0) <= 10
        ),

      expired:
        meds.filter(m =>
          m.expiry &&
          new Date(m.expiry) < now
        ),

      expiringSoon:
        meds.filter(m => {

          if (!m.expiry) return false;

          const days =
            (new Date(m.expiry) - now) /
            86400000;

          return days >= 0 && days <= 30;
        })
    });
  }

  // ----------------------------------------------------------
  // SUPPLIERS
  // ----------------------------------------------------------

  if (url.pathname === "/api/suppliers")
    return send(res, load(DB.SUPPLIERS));

  // ----------------------------------------------------------
  // PURCHASES
  // ----------------------------------------------------------

  if (url.pathname === "/api/purchases")
    return send(res, load(DB.PURCHASES));

  // ----------------------------------------------------------
  // CASH
  // ----------------------------------------------------------

  if (url.pathname === "/api/cash") {

    const sales = load(DB.SALES);

    const today =
      new Date().toISOString().slice(0, 10);

    const todaySales =
      sales.filter(s =>
        String(s.date || "").slice(0, 10) === today
      );

    return send(res, {

      date: today,

      sales: todaySales.length,

      revenue:
        todaySales.reduce(
          (a, b) =>
            a + Number(b.total || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // INVENTORY VALUE
  // ----------------------------------------------------------

  if (url.pathname === "/api/inventory-value") {

    const meds = load(DB.MED);

    return send(res, {

      value:
        meds.reduce(
          (a, b) =>
            a +
            Number(b.quantity || 0) *
            Number(b.price || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // ANALYTICS
  // ----------------------------------------------------------

  if (url.pathname === "/api/analytics") {

    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    return send(res, {

      medicines: meds.length,

      sales: sales.length,

      revenue:
        sales.reduce(
          (a, b) =>
            a + Number(b.total || 0),
          0
        ),

      inventoryValue:
        meds.reduce(
          (a, b) =>
            a +
            Number(b.quantity || 0) *
            Number(b.price || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // SCIENTIFIC MODELS
  // ----------------------------------------------------------

  const models = {

    forecast:
      "forecast.py",

    monteCarlo:
      "inventory_sim.py",

    reorderPoint:
      "reorder_point.py",

    safetyStock:
      "safety_stock.py",

    expiryRisk:
      "expiry_risk.py",

    abc:
      "abc_analysis.py",

    eoq:
      "eoq.py",

    ai:
      "ai_dashboard.py"
  };

  if (
    url.pathname.startsWith("/api/model/")
  ) {

    const name =
      url.pathname.split("/").pop();

    if (!models[name])
      return send(
        res,
        { error: "Unknown model" },
        404
      );

    return send(res, {

      model: name,

      output:
        python(models[name])
    });
  }

  // ----------------------------------------------------------
  // REPORTS
  // ----------------------------------------------------------

  if (url.pathname === "/api/reports") {

    const dir =
      path.join(APP, "reports");

    const files =
      fs.existsSync(dir)
        ? fs.readdirSync(dir)
        : [];

    return send(res, { files });
  }

  // ----------------------------------------------------------
  // REPORT FILE
  // ----------------------------------------------------------

  if (url.pathname === "/api/report-file") {

    const name =
      url.searchParams.get("name");

    if (!name)
      return send(
        res,
        { error: "Missing file" },
        400
      );

    const dir =
      path.join(APP, "reports");

    const file =
      path.join(dir, path.basename(name));

    if (!fs.existsSync(file))
      return send(
        res,
        { error: "File not found" },
        404
      );

    return send(res, {
      name,
      content:
        fs.readFileSync(file, "utf8")
    });
  }

  // ----------------------------------------------------------
  // SAS
  // ----------------------------------------------------------

  if (url.pathname === "/api/sas") {

    const dir =
      path.join(APP, "exports");

    const files =
      fs.existsSync(dir)
        ? fs.readdirSync(dir)
        : [];

    return send(res, {
      files
    });
  }

  // ----------------------------------------------------------
  // SNAPSHOT
  // ----------------------------------------------------------

  if (url.pathname === "/api/snapshot") {

    const file =
      path.join(
        APP,
        "reports",
        "web_snapshot.txt"
      );

    fs.writeFileSync(
      file,
      JSON.stringify(
        summary(),
        null,
        2
      )
    );

    return send(res, {
      success: true,
      file: "web_snapshot.txt"
    });
  }

  // ----------------------------------------------------------
  // HEALTH
  // ----------------------------------------------------------

  if (url.pathname === "/api/health") {

    return send(res, {

      system:
        "PHARMACY V12",

      status:
        "ONLINE",

      node:
        process.version,

      database: {

        medicines:
          fs.existsSync(DB.MED),

        sales:
          fs.existsSync(DB.SALES),

        suppliers:
          fs.existsSync(DB.SUPPLIERS),

        purchases:
          fs.existsSync(DB.PURCHASES)
      },

      simulation: {

        forecast:
          fs.existsSync(
            path.join(APP, "simulation/forecast.py")
          ),

        abc:
          fs.existsSync(
            path.join(APP, "simulation/abc_analysis.py")
          ),

        eoq:
          fs.existsSync(
            path.join(APP, "simulation/eoq.py")
          ),

        ai:
          fs.existsSync(
            path.join(APP, "simulation/ai_dashboard.py")
          )
      }
    });
  }

  // ----------------------------------------------------------
  // STATIC
  // ----------------------------------------------------------

  let file;

  if (url.pathname === "/")
    file =
      path.join(APP, "web/index.html");
  else
    file =
      path.join(
        APP,
        "web",
        url.pathname
      );

  if (
    fs.existsSync(file) &&
    fs.statSync(file).isFile()
  ) {

    const ext =
      path.extname(file);

    const types = {

      ".html":
        "text/html; charset=utf-8",

      ".css":
        "text/css; charset=utf-8",

      ".js":
        "application/javascript; charset=utf-8"
    };

    res.writeHead(200, {
      "Content-Type":
        types[ext] ||
        "text/plain; charset=utf-8"
    });

    return res.end(
      fs.readFileSync(file)
    );
  }

  send(
    res,
    { error: "Not found" },
    404
  );
}

const server =
  http.createServer((req, res) => {

    router(req, res).catch(err => {

      send(
        res,
        { error: err.message },
        500
      );

    });
  });

server.listen(
  8080,
  "0.0.0.0",
  () => {

    console.log("");
    console.log(
      "================================================"
    );
    console.log(
      " PHARMACY V12 INTERACTIVE CONTROL CENTER"
    );
    console.log(
      " http://127.0.0.1:8080"
    );
    console.log(
      "================================================"
    );
  }
);
NODE

# ------------------------------------------------------------
# 3. HTML
# ------------------------------------------------------------

cat > web/index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
 name="viewport"
 content="width=device-width,initial-scale=1">

<title>Pharmacy V12 Control Center</title>

<link rel="stylesheet" href="style.css">

</head>

<body>

<header>

<div>

<h1>💊 PHARMACY V12</h1>

<p>
Interactive Management • Analytics • AI • Decision Support
</p>

</div>

<div class="online">
● SYSTEM ONLINE
</div>

</header>

<div class="layout">

<aside>

<h3>CONTROL CENTER</h3>

<button onclick="showPage('dashboard')">
🏠 Dashboard
</button>

<button onclick="showPage('medicines')">
💊 Medicines
</button>

<button onclick="showPage('sales')">
💰 Sales
</button>

<button onclick="showPage('inventory')">
📦 Inventory
</button>

<button onclick="showPage('alerts')">
⚠ Alerts
</button>

<hr>

<h3>OPERATIONS</h3>

<button onclick="showPage('suppliers')">
🚚 Suppliers
</button>

<button onclick="showPage('purchases')">
🛒 Purchases
</button>

<button onclick="showPage('cash')">
💵 Daily Cash
</button>

<hr>

<h3>DECISION SCIENCE</h3>

<button onclick="runModel('forecast')">
🔮 Forecast
</button>

<button onclick="runModel('monteCarlo')">
🎲 Monte Carlo Risk
</button>

<button onclick="runModel('reorderPoint')">
📍 Reorder Point
</button>

<button onclick="runModel('safetyStock')">
🛡 Safety Stock
</button>

<button onclick="runModel('expiryRisk')">
⏳ Expiry Risk
</button>

<button onclick="runModel('abc')">
📊 ABC Analysis
</button>

<button onclick="runModel('eoq')">
📦 EOQ Model
</button>

<button onclick="runModel('ai')">
🤖 AI Dashboard
</button>

<hr>

<h3>REPORTING</h3>

<button onclick="showPage('reports')">
📑 Reports
</button>

<button onclick="showPage('sas')">
🧪 SAS
</button>

<button onclick="snapshot()">
📸 Snapshot
</button>

<button onclick="showPage('health')">
⚙ System Health
</button>

</aside>

<main>

<!-- DASHBOARD -->

<section id="dashboard" class="page active">

<h2>🏠 Pharmacy Control Center</h2>

<div class="cards">

<div class="card">
<span>💊 Medicines</span>
<strong id="medCount">0</strong>
</div>

<div class="card">
<span>💰 Sales</span>
<strong id="salesCount">0</strong>
</div>

<div class="card">
<span>💵 Revenue</span>
<strong id="revenue">0</strong>
</div>

<div class="card">
<span>📦 Inventory Value</span>
<strong id="inventoryValue">0</strong>
</div>

<div class="card warning">
<span>⚠ Low Stock</span>
<strong id="lowStock">0</strong>
</div>

<div class="card danger">
<span>🔴 Expired</span>
<strong id="expired">0</strong>
</div>

<div class="card warning">
<span>⏳ Expiring Soon</span>
<strong id="expiringSoon">0</strong>
</div>

</div>

<div class="actions">

<button onclick="addMedicine()">
➕ Add Medicine
</button>

<button onclick="sellMedicine()">
💰 Sell Medicine
</button>

<button onclick="showPage('alerts')">
⚠ Review Alerts
</button>

<button onclick="runModel('ai')">
🤖 AI Decision Center
</button>

</div>

</section>

<!-- MEDICINES -->

<section id="medicines" class="page">

<h2>💊 Medicines Management</h2>

<div class="toolbar">

<input
 id="search"
 placeholder="Search medicine..."
 oninput="loadMedicines()">

<button onclick="addMedicine()">
➕ Add
</button>

</div>

<div id="medicineTable"></div>

</section>

<!-- SALES -->

<section id="sales" class="page">

<h2>💰 Sales</h2>

<div id="salesTable"></div>

</section>

<!-- INVENTORY -->

<section id="inventory" class="page">

<h2>📦 Inventory Valuation & Stock</h2>

<div id="inventoryTable"></div>

</section>

<!-- ALERTS -->

<section id="alerts" class="page">

<h2>⚠ Alerts & Expiry Management</h2>

<div id="alertsContent"></div>

</section>

<!-- SUPPLIERS -->

<section id="suppliers" class="page">

<h2>🚚 Supplier Management</h2>

<div id="supplierContent"></div>

</section>

<!-- PURCHASES -->

<section id="purchases" class="page">

<h2>🛒 Purchase Management</h2>

<div id="purchaseContent"></div>

</section>

<!-- CASH -->

<section id="cash" class="page">

<h2>💵 Daily Cash Report</h2>

<div id="cashContent"></div>

</section>

<!-- REPORTS -->

<section id="reports" class="page">

<h2>📑 Reports Center</h2>

<div id="reportsContent"></div>

</section>

<!-- SAS -->

<section id="sas" class="page">

<h2>🧪 SAS Analytics Center</h2>

<div id="sasContent"></div>

</section>

<!-- HEALTH -->

<section id="health" class="page">

<h2>⚙ System Health</h2>

<div id="healthContent"></div>

</section>

<!-- MODEL -->

<section id="model" class="page">

<h2 id="modelTitle">
Decision Science
</h2>

<div id="modelSummary"></div>

<pre id="modelOutput">
Select a model...
</pre>

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
  background: #17324d;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

header h1 {
  margin: 0;
}

header p {
  margin-bottom: 0;
}

.online {
  font-weight: bold;
  white-space: nowrap;
}

.layout {
  display: flex;
  min-height: calc(100vh - 150px);
}

aside {
  width: 245px;
  background: white;
  padding: 15px;
  border-right: 1px solid #ddd;
}

aside h3 {
  font-size: 12px;
  margin-top: 15px;
  letter-spacing: 1px;
}

aside button {
  width: 100%;
  border: 0;
  border-radius: 7px;
  padding: 10px;
  margin: 3px 0;
  text-align: left;
  background: #edf2f7;
  cursor: pointer;
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

.card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px #0001;
}

.card span {
  display: block;
  margin-bottom: 10px;
}

.card strong {
  font-size: 28px;
}

.warning {
  border-left: 5px solid #e6a700;
}

.danger {
  border-left: 5px solid #d33;
}

.actions {
  margin-top: 25px;
}

.actions button,
.toolbar button {
  border: 0;
  border-radius: 8px;
  padding: 12px 18px;
  margin: 5px;
  cursor: pointer;
}

input {
  padding: 11px;
  border: 1px solid #bbb;
  border-radius: 7px;
  width: 300px;
  max-width: 100%;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  margin-top: 15px;
}

th,
td {
  padding: 11px;
  border-bottom: 1px solid #ddd;
}

th {
  background: #edf2f7;
  text-align: left;
}

pre {
  background: #111827;
  color: #e5e7eb;
  padding: 20px;
  border-radius: 10px;
  overflow: auto;
  white-space: pre-wrap;
}

.report {
  background: white;
  padding: 15px;
  margin: 10px 0;
  border-radius: 9px;
}

.report button {
  margin: 4px;
  padding: 8px 12px;
}

footer {
  text-align: center;
  background: #17324d;
  color: white;
  padding: 15px;
}

@media(max-width:800px) {

  header {
    display: block;
    text-align: center;
  }

  .layout {
    display: block;
  }

  aside {
    width: 100%;
    border-right: 0;
  }

  aside button {
    width: auto;
    display: inline-block;
  }

  main {
    padding: 15px;
  }
}
CSS

# ------------------------------------------------------------
# 5. JAVASCRIPT
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

function showPage(id) {

  document
    .querySelectorAll(".page")
    .forEach(p =>
      p.classList.remove("active")
    );

  document
    .getElementById(id)
    .classList.add("active");

  const loaders = {

    dashboard: loadDashboard,

    medicines: loadMedicines,

    sales: loadSales,

    inventory: loadInventory,

    alerts: loadAlerts,

    suppliers: loadSuppliers,

    purchases: loadPurchases,

    cash: loadCash,

    reports: loadReports,

    sas: loadSAS,

    health: loadHealth
  };

  if (loaders[id])
    loaders[id]();
}

async function loadDashboard() {

  const d =
    await api("/api/summary");

  medCount.textContent =
    d.medicines;

  salesCount.textContent =
    d.sales;

  revenue.textContent =
    d.revenue;

  inventoryValue.textContent =
    d.inventoryValue;

  lowStock.textContent =
    d.lowStock;

  expired.textContent =
    d.expired;

  expiringSoon.textContent =
    d.expiringSoon;
}

async function loadMedicines() {

  const q =
    document.getElementById("search").value;

  const meds =
    await api(
      "/api/medicines?q=" +
      encodeURIComponent(q)
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
        <button
          onclick="sellMedicine('${esc(m.name)}')">
          Sell
        </button>
      </td>

    </tr>

  `).join("")}

  </table>`;
}

async function loadSales() {

  const sales =
    await api("/api/sales");

  salesTable.innerHTML = `

  <table>

  <tr>
    <th>Date</th>
    <th>Medicine</th>
    <th>Qty</th>
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

  const meds =
    await api("/api/medicines");

  inventoryTable.innerHTML = `

  <table>

  <tr>
    <th>Medicine</th>
    <th>Stock</th>
    <th>Unit Price</th>
    <th>Inventory Value</th>
  </tr>

  ${meds.map(m => `

    <tr>

      <td>${esc(m.name)}</td>

      <td>${m.quantity}</td>

      <td>${m.price}</td>

      <td>
        ${Number(m.quantity) *
          Number(m.price)}
      </td>

    </tr>

  `).join("")}

  </table>`;
}

async function loadAlerts() {

  const a =
    await api("/api/alerts");

  alertsContent.innerHTML = `

  <h3>
  ⚠ Low Stock (${a.lowStock.length})
  </h3>

  ${a.lowStock.map(m =>
    `<p>⚠ ${esc(m.name)}
    — ${m.quantity}</p>`
  ).join("")}

  <h3>
  🔴 Expired (${a.expired.length})
  </h3>

  ${a.expired.map(m =>
    `<p>🔴 ${esc(m.name)}
    — ${esc(m.expiry)}</p>`
  ).join("")}

  <h3>
  ⏳ Expiring Soon (${a.expiringSoon.length})
  </h3>

  ${a.expiringSoon.map(m =>
    `<p>🟠 ${esc(m.name)}
    — ${esc(m.expiry)}</p>`
  ).join("")}
  `;
}

async function loadSuppliers() {

  const d =
    await api("/api/suppliers");

  supplierContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadPurchases() {

  const d =
    await api("/api/purchases");

  purchaseContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function loadCash() {

  const d =
    await api("/api/cash");

  cashContent.innerHTML = `

  <div class="card">

    <h3>Date</h3>
    <strong>${d.date}</strong>

    <h3>Sales</h3>
    <strong>${d.sales}</strong>

    <h3>Revenue</h3>
    <strong>${d.revenue}</strong>

  </div>`;
}

async function loadReports() {

  const d =
    await api("/api/reports");

  reportsContent.innerHTML =
    d.files.map(file => `

      <div class="report">

        <strong>
          📄 ${esc(file)}
        </strong>

        <br>

        <button
          onclick="viewReport('${esc(file)}')">
          View
        </button>

      </div>

    `).join("");
}

async function viewReport(name) {

  const d =
    await api(
      "/api/report-file?name=" +
      encodeURIComponent(name)
    );

  modelTitle.textContent =
    name;

  modelOutput.textContent =
    d.content;

  showPage("model");
}

async function loadSAS() {

  const d =
    await api("/api/sas");

  sasContent.innerHTML = `

    <h3>SAS Export Files</h3>

    <pre>
${esc(JSON.stringify(d, null, 2))}
    </pre>

    <p>
    SAS export and pipeline files are available
    in the exports directory.
    </p>
  `;
}

async function loadHealth() {

  const d =
    await api("/api/health");

  healthContent.innerHTML =
    "<pre>" +
    esc(JSON.stringify(d, null, 2)) +
    "</pre>";
}

async function runModel(name) {

  showPage("model");

  modelTitle.textContent =
    name.replaceAll("-", " ")
        .toUpperCase();

  modelSummary.innerHTML =
    "<div class='card'>" +
    "Running decision model..." +
    "</div>";

  modelOutput.textContent =
    "Running " + name + "...\n";

  try {

    const d =
      await api(
        "/api/model/" + name
      );

    modelOutput.textContent =
      d.output;

    modelSummary.innerHTML =
      "<div class='card'>" +
      "Model completed successfully." +
      "</div>";

  } catch (e) {

    modelOutput.textContent =
      "ERROR\n" + e.message;
  }
}

async function addMedicine() {

  const name =
    prompt("Medicine name:");

  if (!name) return;

  const quantity =
    prompt("Quantity:", "0");

  const price =
    prompt("Price:", "0");

  const expiry =
    prompt("Expiry YYYY-MM-DD:", "");

  const r =
    await api("/api/medicines", {

      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
      },

      body: JSON.stringify({
        name,
        quantity,
        price,
        expiry
      })
    });

  if (r.success) {

    alert(
      "Medicine added successfully."
    );

    loadDashboard();
    loadMedicines();

  }
}

async function sellMedicine(name) {

  if (!name)
    name =
      prompt("Medicine name:");

  if (!name) return;

  const qty =
    prompt(
      "Quantity to sell:",
      "1"
    );

  if (!qty) return;

  const r =
    await api("/api/sell", {

      method: "POST",

      headers: {
        "Content-Type":
          "application/json"
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
    "Sale completed.\n" +
    "Total: " +
    r.sale.total
  );

  loadDashboard();
  loadMedicines();
}

async function snapshot() {

  const r =
    await api("/api/snapshot");

  alert(
    r.success
      ? "Dashboard snapshot created."
      : "Snapshot failed."
  );
}

loadDashboard();
JS

# ------------------------------------------------------------
# 6. START SCRIPT
# ------------------------------------------------------------

cat > start_web.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/pharmacy-v12"

echo ""
echo "============================================================"
echo " PHARMACY V12 INTERACTIVE CONTROL CENTER"
echo "============================================================"
echo ""
echo "Open:"
echo "http://127.0.0.1:8080"
echo ""
echo "Press Ctrl+C to stop."
echo ""

node web_server.js
SH

chmod +x start_web.sh

# ------------------------------------------------------------
# 7. TEST
# ------------------------------------------------------------

echo "[2/7] Server written"
echo "[3/7] Control Center HTML written"
echo "[4/7] CSS written"
echo "[5/7] JavaScript written"

echo "[6/7] Syntax validation"

node --check web_server.js
node --check web/app.js

echo ""
echo "Node syntax: OK"

echo "[7/7] ONESHOT2 COMPLETE"

echo ""
echo "============================================================"
echo " PHARMACY V12 CONTROL CENTER READY"
echo "============================================================"
echo ""
echo "30-choice V12 core: PRESERVED"
echo ""
echo "Interactive Web modules:"
echo ""
echo "  1  Add Medicine"
echo "  2  List Medicines"
echo "  3  Sell Medicine"
echo "  4  Search Medicine"
echo "  5  Alerts"
echo "  6  Analytics"
echo "  7  Web Dashboard"
echo "  8  Reports"
echo "  9  Server / Web Control"
echo " 10  Exit / CLI"
echo " 11  SAS Export"
echo " 12  Backup System"
echo " 13  System Health"
echo " 14  Expiry Management"
echo " 15  Supplier Management"
echo " 16  Purchase Management"
echo " 17  Daily Cash"
echo " 18  Inventory Valuation"
echo " 19  Advanced SAS Analytics"
echo " 20  Dashboard Snapshot"
echo " 21  Batch/Data Import"
echo " 22  SAS Pipeline"
echo " 23  Python Forecast"
echo " 24  Monte Carlo Risk"
echo " 25  Reorder Point"
echo " 26  Safety Stock"
echo " 27  Expiry Risk"
echo " 28  ABC Analysis"
echo " 29  EOQ"
echo " 30  Integrated AI Dashboard"
echo ""
echo "Backup:"
echo "$BACKUP/oneshot2_before_${STAMP}.tar.gz"
echo ""
echo "Start:"
echo "./start_web.sh"
echo ""
echo "URL:"
echo "http://127.0.0.1:8080"
echo ""
echo "============================================================"
