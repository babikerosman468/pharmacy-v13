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
                    "/reports/file?name=pharmacy_report.pdf",
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
