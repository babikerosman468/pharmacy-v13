function getAuthToken() {
  return localStorage.getItem("pharmacy_v13_token") || "";
}

function logout() {
  localStorage.removeItem("pharmacy_v13_token");
  localStorage.removeItem("pharmacy_v13_user");
  window.location.reload();
}

async function api(url, options = {}) {

  const token = getAuthToken();

  const headers = {
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = "Bearer " + token;
  }

  const r = await fetch(url, {
    ...options,
    headers
  });

  if (r.status === 401) {
    logout();
    throw new Error("Authentication required");
  }

  if (!r.ok)
    throw new Error(await r.text());

  return r.json();
}

async function snapshot() {
  const data = await api("/api/intelligence?mode=snapshot");
  const box = document.getElementById("snapshotContent");
  if (box) box.textContent = JSON.stringify(data, null, 2);
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

    intelligence: loadIntelligence,

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

  const medicines = await api("/api/medicines");
  const sales = await api("/api/sales");
  const alerts = await api("/api/alerts");

  const calculatedInventoryValue =
    medicines.reduce(
      (sum, m) =>
        sum +
        (Number(m.quantity) || 0) *
        (Number(m.price) || 0),
      0
    );

  const calculatedRevenue =
    sales.reduce(
      (sum, s) =>
        sum + (Number(s.total) || 0),
      0
    );

  const d = {
    medicines: medicines.length,
    sales: sales.length,
    revenue: calculatedRevenue,
    inventoryValue: calculatedInventoryValue,
    lowStock: Number(alerts.lowStock || 0),
    expired: Number(alerts.expired || 0),
    expiringSoon: Number(alerts.expiringSoon || 0)
  };

  medCount.textContent =
    d.medicines;

  salesCount.textContent =
    d.sales;

  revenue.textContent =
    d.revenue.toLocaleString();

  inventoryValue.textContent =
    d.inventoryValue.toLocaleString();

  lowStock.textContent =
    d.lowStock;

  expired.textContent =
    d.expired;

  expiringSoon.textContent =
    d.expiringSoon;

  const inventoryStatus =
    document.getElementById("inventoryStatus");

  const stockStatus =
    document.getElementById("stockStatus");

  const expiryStatus =
    document.getElementById("expiryStatus");

  if (inventoryStatus) {
    inventoryStatus.textContent =
      `${d.medicines} medicines • ${d.inventoryValue.toLocaleString()} value`;
  }

  if (stockStatus) {
    stockStatus.textContent =
      d.lowStock > 0
        ? `⚠ ${d.lowStock} low-stock item(s)`
        : "✓ Stock levels normal";
  }

  if (expiryStatus) {
    const totalExpiry =
      d.expired + d.expiringSoon;

    expiryStatus.textContent =
      totalExpiry > 0
        ? `⚠ ${totalExpiry} expiry item(s) require attention`
        : "✓ Expiry status normal";
  }
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

  <h3>📦 Inventory Operations</h3>

  <div style="margin-bottom:15px">

    <button onclick="inventoryStockIn()">
      ➕ Stock-In
    </button>

    <button onclick="inventoryStockOut()">
      ➖ Stock-Out
    </button>

  </div>

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


async function inventoryStockIn() {

  const meds =
    await api("/api/medicines");

  const name =
    prompt("Medicine name:");

  if (!name)
    return;

  const medicine =
    meds.find(
      m => m.name.toLowerCase() ===
           name.toLowerCase()
    );

  if (!medicine) {
    alert("Medicine not found");
    return;
  }

  const quantity =
    Number(prompt("Quantity to add:"));

  if (!Number.isFinite(quantity) || quantity <= 0) {
    alert("Invalid quantity");
    return;
  }

  const result =
    await api(
      "/api/inventory/stock-in",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          medicineId: medicine.id,
          supplierId: 1,
          quantity,
          unitCost: medicine.price,
          batchNumber: "WEB-STOCK-IN",
          expiry: medicine.expiry
        })
      }
    );

  alert(
    "Stock-In successful\n\n" +
    medicine.name +
    "\nAdded: " +
    quantity
  );

  await loadInventory();
}

async function inventoryStockOut() {
  const meds =
    await api("/api/medicines");

  const name =
    prompt("Medicine name:");

  if (!name)
    return;

  const medicine =
    meds.find(
      m => m.name.toLowerCase() ===
           name.toLowerCase()
    );

  if (!medicine) {
    alert("Medicine not found");
    return;
  }

  const quantity =
    Number(prompt("Quantity to remove:"));

  if (!Number.isFinite(quantity) || quantity <= 0) {
    alert("Invalid quantity");
    return;
  }

  const result =
    await api(
      "/api/inventory/stock-out",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          medicineId: medicine.id,
          quantity
        })
      }
    );

  alert(
    "Stock-Out successful\n\n" +
    medicine.name +
    "\nRemoved: " +
    quantity
  );

  await loadInventory();
  await loadDashboard();
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

  supplierContent.innerHTML = `

  <h3>🚚 Supplier Management</h3>

  <div style="margin-bottom:15px">

    <button onclick="addSupplier()">
      ➕ Add Supplier
    </button>

  </div>

  <table>

  <tr>
    <th>Name</th>
    <th>Phone</th>
    <th>Address</th>
  </tr>

  ${d.map(s => `

    <tr>

      <td>${esc(s.name)}</td>

      <td>${esc(s.phone)}</td>

      <td>${esc(s.address)}</td>

    </tr>

  `).join("")}

  </table>`;
}


async function addSupplier() {

  const name =
    prompt("Supplier name:");

  if (!name)
    return;

  const phone =
    prompt("Phone:");

  if (!phone)
    return;

  const address =
    prompt("Address:");

  if (!address)
    return;

  await api(
    "/api/suppliers",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        phone,
        address
      })
    }
  );

  alert("Supplier added successfully");

  await loadSuppliers();
}

async function loadPurchases() {

  const d =
    await api("/api/purchases");

  purchaseContent.innerHTML = `

  <h3>🛒 Purchase Management</h3>

  <div style="margin-bottom:15px">

    <button onclick="addPurchase()">
      ➕ New Purchase
    </button>

  </div>

  <table>

  <tr>
    <th>Supplier</th>
    <th>Medicine</th>
    <th>Quantity</th>
    <th>Unit Cost</th>
    <th>Total Cost</th>
    <th>Batch</th>
    <th>Expiry</th>
    <th>Date</th>
  </tr>

  ${d.map(p => `

    <tr>

      <td>${esc(p.supplierName)}</td>

      <td>${esc(p.medicineName)}</td>

      <td>${p.quantity}</td>

      <td>${p.unitCost}</td>

      <td>${p.totalCost}</td>

      <td>${esc(p.batchNumber)}</td>

      <td>${esc(p.expiry)}</td>

      <td>${esc(p.date)}</td>

    </tr>

  `).join("")}

  </table>`;
}


async function addPurchase() {

  const suppliers =
    await api("/api/suppliers");

  const medicines =
    await api("/api/medicines");

  if (!suppliers.length) {
    alert("No suppliers available");
    return;
  }

  const supplierName =
    prompt(
      "Supplier name:\n\n" +
      suppliers.map(s => s.name).join("\n")
    );

  if (!supplierName)
    return;

  const supplier =
    suppliers.find(
      s => s.name.toLowerCase() ===
           supplierName.toLowerCase()
    );

  if (!supplier) {
    alert("Supplier not found");
    return;
  }

  const medicineName =
    prompt(
      "Medicine name:\n\n" +
      medicines.slice(0, 20)
        .map(m => m.name)
        .join("\n") +
      "\n\n(Type the exact medicine name)"
    );

  if (!medicineName)
    return;

  const medicine =
    medicines.find(
      m => m.name.toLowerCase() ===
           medicineName.toLowerCase()
    );

  if (!medicine) {
    alert("Medicine not found");
    return;
  }

  const quantity =
    Number(prompt("Quantity to purchase:"));

  if (!Number.isFinite(quantity) || quantity <= 0) {
    alert("Invalid quantity");
    return;
  }

  const unitCost =
    Number(
      prompt(
        "Unit cost:",
        medicine.price
      )
    );

  if (!Number.isFinite(unitCost) || unitCost < 0) {
    alert("Invalid unit cost");
    return;
  }

  const batchNumber =
    prompt("Batch number:", "WEB-PURCHASE");

  if (batchNumber === null)
    return;

  const expiry =
    prompt("Expiry date:", medicine.expiry);

  if (expiry === null)
    return;

  await api(
    "/api/inventory/stock-in",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        supplierId: supplier.id,
        medicineId: medicine.id,
        quantity,
        unitCost,
        batchNumber,
        expiry
      })
    }
  );

  alert(
    "Purchase successful\n\n" +
    "Supplier: " + supplier.name +
    "\nMedicine: " + medicine.name +
    "\nQuantity: " + quantity +
    "\nUnit cost: " + unitCost +
    "\nTotal cost: " +
    (quantity * unitCost)
  );

  await loadPurchases();
  await loadInventory();
  await loadDashboard();
}

async function loadCash() {

  const d =
    await api("/api/cash");

  cashContent.innerHTML = `

  <div class="card">

    <h3>Date</h3>
<strong>${new Date().toLocaleDateString()}</strong>
    <h3>Sales</h3>
<strong>${d.salesCount}</strong>

    <h3>Revenue</h3>
<strong>${d.cashTotal}</strong>
  </div>`;
}

async function loadReports() {
    // Official Report Center is rendered directly in index.html.
    // Do not replace it with the legacy dynamic file list.
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

async function loadIntelligence() {

  const box =
    document.getElementById("intelligenceContent");

  if (!box)
    return;

  try {

    const [
      summary,
      drugs,
      readiness,
      unmatched
    ] = await Promise.all([

      api("/api/intelligence?mode=summary"),
      api("/api/intelligence?mode=drugs"),
      api("/api/intelligence?mode=readiness"),
      api("/api/intelligence?mode=unmatched")

    ]);

    const value = (x) =>
      Number(x || 0).toLocaleString();

    const decisions =
      drugs.decisions || [];

    const priority =
      summary.priorityCounts || {};

    const signals =
      summary.signalCounts || {};

    const files =
      readiness.files || {};

    const readyFiles =
      Object.values(files)
        .filter(Boolean)
        .length;

    box.innerHTML = `

      <div class="card">

        <h3>🤖 REEM V2 Decision Intelligence</h3>

        <p>
          <strong>REEM calculates evidence → AI interprets evidence
          → Management decides.</strong>
        </p>

        <p>
          Data Source:
          <strong>${esc(summary.dataSource)}</strong>
        </p>

        <p>
          Data Status:
          <strong>${esc(summary.dataStatus)}</strong>
        </p>

        <p>
          Operational Use:
          <strong>${esc(summary.operationalUse)}</strong>
        </p>

        <p>
          System Status:
          <strong>${esc(summary.status)}</strong>
        </p>

      </div>

      <div class="cards">

        <div class="card">
          <span>💊 REEM Medicines</span>
          <strong>${value(summary.medicineCount)}</strong>
        </div>

        <div class="card">
          <span>🔴 HIGH Priority</span>
          <strong>${value(priority.HIGH)}</strong>
        </div>

        <div class="card">
          <span>🟠 MEDIUM Priority</span>
          <strong>${value(priority.MEDIUM)}</strong>
        </div>

        <div class="card">
          <span>🟢 LOW Priority</span>
          <strong>${value(priority.LOW)}</strong>
        </div>

        <div class="card">
          <span>🧠 Models Integrated</span>
          <strong>${value(summary.modelsIntegrated)}</strong>
        </div>

        <div class="card">
          <span>📁 Files Ready</span>
          <strong>${readyFiles}</strong>
        </div>

      </div>

      <div class="card">

        <h3>📊 Management Signals</h3>

        <table>

          <tr>
            <th>Signal</th>
            <th>Count</th>
          </tr>

          ${Object.entries(signals)
            .map(([name, count]) => `

              <tr>
                <td>${esc(name)}</td>
                <td><strong>${value(count)}</strong></td>
              </tr>

            `).join("")}

        </table>

      </div>

      <div class="card">

        <h3>🧭 AI Management Decisions</h3>

        ${
          decisions.length
            ? `

              <div style="overflow-x:auto">

              <table>

                <tr>
                  <th>Drug</th>
                  <th>Priority</th>
                  <th>Primary Signal</th>
                  <th>Evidence</th>
                  <th>Recommended Action</th>
                </tr>

                ${decisions.map(d => {

                  const e =
                    d.Evidence || {};

                  const interpretation =
                    d.Interpretation || [];

                  const actions =
                    d.RecommendedAction || [];

                  return `

                    <tr>

                      <td>
                        <strong>
                          ${esc(d.DrugID)}
                        </strong>
                      </td>

                      <td>
                        <strong>
                          ${esc(d.Priority)}
                        </strong>
                      </td>

                      <td>
                        ${esc(d.PrimarySignal)}
                      </td>

                      <td>

                        Forecast:
                        ${esc(e.ForecastDailyDemand)}

                        <br>

                        Stock:
                        ${esc(e.CurrentStock)}

                        <br>

                        Coverage:
                        ${esc(e.CoverageDays)} days

                        <br>

                        ROP:
                        ${esc(e.ReorderPoint)}

                        <br>

                        Expired:
                        ${esc(e.ExpiredBatches)}

                        <br>

                        Critical expiry:
                        ${esc(e.CriticalExpiryBatches)}

                      </td>

                      <td>

                        ${
                          actions.length
                            ? actions
                                .map(a =>
                                  `<div>• ${esc(a)}</div>`
                                )
                                .join("")
                            : "No immediate action."
                        }

                      </td>

                    </tr>

                    <tr>

                      <td colspan="5">

                        <small>

                          <strong>
                            Interpretation:
                          </strong>

                          ${
                            interpretation.length
                              ? interpretation
                                  .map(i =>
                                    `<div>• ${esc(i)}</div>`
                                  )
                                  .join("")
                              : "None"
                          }

                        </small>

                      </td>

                    </tr>

                  `;

                }).join("")}

              </table>

              </div>

            `
            : `<p>No AI decisions available.</p>`
        }

      </div>

      <div class="card">

        <h3>🧪 REEM V2 Readiness</h3>

        <p>
          Status:
          <strong>${esc(readiness.status)}</strong>
        </p>

        <p>
          Models Integrated:
          <strong>${value(readiness.modelsIntegrated)}</strong>
        </p>

        <table>

          <tr>
            <th>REEM Evidence File</th>
            <th>Status</th>
          </tr>

          ${Object.entries(files)
            .map(([file, ok]) => `

              <tr>

                <td>${esc(file)}</td>

                <td>
                  <strong>
                    ${ok ? "READY" : "MISSING"}
                  </strong>
                </td>

              </tr>

            `).join("")}

        </table>

      </div>

      <div class="card warning">

        <h3>🔎 Data Quality Review</h3>

        <p>
          Unmatched records:
          <strong>${value(unmatched.count)}</strong>
        </p>

        ${
          unmatched.count > 0
            ? `

              <table>

                <tr>
                  <th>Medicine</th>
                  <th>Quantity</th>
                  <th>Revenue</th>
                  <th>Date</th>
                  <th>Status</th>
                </tr>

                ${(unmatched.unmatched || [])
                  .map(u => `

                    <tr>

                      <td>${esc(u.medicine)}</td>
                      <td>${esc(u.qty)}</td>
                      <td>${esc(u.total)}</td>
                      <td>${esc(u.date)}</td>
                      <td>${esc(u.status)}</td>

                    </tr>

                  `).join("")}

              </table>

            `
            : `<p>✓ No unmatched records.</p>`
        }

        <p>
          No DrugID is inferred automatically.
        </p>

      </div>

    `;

  } catch (err) {

    box.innerHTML = `

      <div class="card danger">

        <h3>⚠ Intelligence Unavailable</h3>

        <p>${esc(err.message)}</p>

      </div>

    `;
  }
}

window.runModel = async function(name) {
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
    "/api/intelligence?mode=" + name
  );
    modelOutput.textContent =
      JSON.stringify(d, null, 2);

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

(async function () {

  const token = getAuthToken();

  if (!token) {

    document.body.innerHTML = `
      <div style="
        min-height:100vh;
        display:flex;
        align-items:center;
        justify-content:center;
        background:#0b1220;
        color:#eef4ff;
        font-family:system-ui,sans-serif;
        padding:20px;
      ">
        <form id="loginForm" style="
          width:min(420px,100%);
          background:#111a2b;
          border:1px solid #263650;
          border-radius:18px;
          padding:32px;
          box-shadow:0 18px 50px rgba(0,0,0,.35);
        ">
          <h1>💊 PHARMACY V13</h1>
          <p style="color:#91a0b8">Secure Management Login</p>

          <label>Username</label>
          <input id="loginUsername" autocomplete="username" required
            style="width:100%;margin:8px 0 18px;padding:12px">

          <label>Password</label>
          <input id="loginPassword" type="password"
            autocomplete="current-password" required
            style="width:100%;margin:8px 0 18px;padding:12px">

          <button type="submit"
            style="width:100%;padding:13px;border:0;border-radius:9px;
                   background:#1769aa;color:white;font-weight:700">
            Sign in
          </button>

          <div id="loginError"
            style="margin-top:15px;color:#ff6262"></div>
        </form>
      </div>
    `;

    document.getElementById("loginForm")
      .addEventListener("submit", async function (e) {

        e.preventDefault();

        const error = document.getElementById("loginError");
        error.textContent = "Signing in...";

        try {

          const response = await fetch(
            "/api/auth/login",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                username:
                  document.getElementById("loginUsername").value,
                password:
                  document.getElementById("loginPassword").value
              })
            }
          );

          const result = await response.json();

          if (!response.ok)
            throw new Error(result.error || "Login failed");

          localStorage.setItem(
            "pharmacy_v13_token",
            result.token
          );

          localStorage.setItem(
            "pharmacy_v13_user",
            JSON.stringify(result.user)
          );
window.location.href = "/professional.html";

        } catch (err) {
          error.textContent = err.message || "Login failed";
        }
      });

    return;
  }

  loadDashboard();

})();

async function compilePharmacyReport() {
    const box = document.getElementById("reportCompileStatus");

    if (box) {
        box.textContent = "Compiling report...";
    }

    try {
        const response = await fetch("/api/reports/compile", {
            method: "POST"
        });

        const result = await response.json();

        if (box) {
            box.textContent = result.ok
                ? "✅ " + result.message
                : "❌ " + result.message;
        }

        if (result.ok) {
            setTimeout(() => {
                window.open(
                    "/api/reports/file?name=pharmacy_report.pdf",
                    "_blank"
                );
            }, 500);
        }

    } catch (error) {
        if (box) {
            box.textContent = "❌ " + error;
        }
    }
}
