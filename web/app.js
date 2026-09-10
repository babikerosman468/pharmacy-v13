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

  const inventoryStatus =
    document.getElementById("inventoryStatus");

  const stockStatus =
    document.getElementById("stockStatus");

  const expiryStatus =
    document.getElementById("expiryStatus");

  if (inventoryStatus) {
    inventoryStatus.textContent =
      `${d.medicines} medicines • ${Number(d.inventoryValue || 0).toLocaleString()} value`;
  }

  if (stockStatus) {
    stockStatus.textContent =
      d.lowStock > 0
        ? `⚠ ${d.lowStock} low-stock item(s)`
        : "✓ Stock levels normal";
  }

  if (expiryStatus) {
    const totalExpiry =
      Number(d.expired || 0) +
      Number(d.expiringSoon || 0);

    expiryStatus.textContent =
      totalExpiry > 0
        ? `⚠ ${totalExpiry} expiry alert(s)`
        : "✓ No expiry alerts";
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
  await loadDashboard();
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
    <strong>${d.date}</strong>

    <h3>Sales</h3>
    <strong>${d.sales}</strong>

    <h3>Revenue</h3>
    <strong>${d.revenue}</strong>

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
      suppliers,
      readiness,
      unmatched
    ] = await Promise.all([

      api("/api/intelligence/summary"),
      api("/api/intelligence/drugs"),
      api("/api/intelligence/suppliers"),
      api("/api/intelligence/readiness"),
      api("/api/intelligence/unmatched")

    ]);
document.getElementById("reemObservationDays").textContent =
  summary.SalesObservationDays ?? "—";

document.getElementById("reemMatchedSoldUnits").textContent =
  summary.SoldUnits ?? "—";

document.getElementById("reemObservationStart").textContent =
  summary.SalesObservationStart ?? "—";

document.getElementById("reemObservationEnd").textContent =
  summary.SalesObservationEnd ?? "—";

    const value = (x) =>
      Number(x || 0).toLocaleString();

    box.innerHTML = `

<div class="card">

  <h3>🧭 Management Interpretation</h3>

  <ul>

    <li>
      Inventory is currently large relative to observed sales.
    </li>

    <li>
      Demand evidence is still limited to the current
      observation window.
    </li>

    <li>
      No critical expiry items are currently identified.
    </li>

    <li>
      No reorder review is currently triggered.
    </li>

    <li>
      One sales transaction requires data-quality review.
    </li>

    <li>
      Advanced inventory optimization requires additional
      historical data and parameters.
    </li>

  </ul>

</div>

      <div class="cards">

        <div class="card">
          <span>💊 Medicines</span>
          <strong>${value(summary.MedicineCount)}</strong>
        </div>

        <div class="card">
          <span>📦 Current Stock</span>
          <strong>${value(summary.CurrentStockUnits)}</strong>
        </div>

        <div class="card">
          <span>💰 Inventory Value</span>
          <strong>${value(summary.CurrentStockValue)}</strong>
        </div>

        <div class="card">
          <span>🛒 Purchased</span>
          <strong>${value(summary.PurchasedUnits)}</strong>
        </div>

        <div class="card">
          <span>💵 Sales Revenue</span>
          <strong>${value(summary.SalesRevenue)}</strong>
        </div>

        <div class="card warning">
          <span>🔎 Unmatched Sales</span>
          <strong>${value(summary.UnmatchedSalesRecords)}</strong>
        </div>

      </div>

      <div class="card">

        <h3>📅 Evidence Window</h3>

        <p>
          Sales observation:
          <strong>
            ${esc(summary.SalesObservationStart)}
            →
            ${esc(summary.SalesObservationEnd)}
          </strong>
        </p>

        <p>
          Observation period:
          <strong>${value(summary.SalesObservationDays)} days</strong>
        </p>

        <p>
          ⚠ Demand and ABC results are based on observed sales
          and should be considered preliminary until mature
          historical data are available.
        </p>

      </div>

      <div class="card">

        <h3>📊 Observed-Sales ABC</h3>

        <div style="overflow-x:auto">

        <table>

          <tr>
            <th>Medicine</th>
            <th>Sold</th>
            <th>Revenue</th>
            <th>ABC</th>
            <th>Stock Days</th>
            <th>Expiry</th>
          </tr>

          ${drugs
            .filter(d => d.SoldQty !== "0.0")
            .map(d => `

              <tr>

                <td>${esc(d.DrugName)}</td>

                <td>${esc(d.SoldQty)}</td>

                <td>${esc(d.Revenue)}</td>

                <td>
                  <strong>${esc(d.ABC_Class)}</strong>
                </td>

                <td>${esc(d.StockDays)}</td>

                <td>${esc(d.ExpiryStatus)}</td>

              </tr>

            `).join("")}

        </table>

        </div>

        <p>
          <small>
            ABC method: Observed-Sales ABC — preliminary.
          </small>
        </p>

      </div>

      <div class="card">

        <h3>🚚 Supplier Intelligence</h3>

        <table>

          <tr>
            <th>Supplier</th>
            <th>Purchased Qty</th>
            <th>Procurement Cost</th>
          </tr>

          ${suppliers.map(s => `

            <tr>

              <td>${esc(s.SupplierName)}</td>

              <td>${esc(s.PurchasedQty)}</td>

              <td>${esc(s.ProcurementCost)}</td>

            </tr>

          `).join("")}

        </table>

      </div>

      <div class="card">

        <h3>🧪 Model Readiness</h3>

        <table>

          <tr>
            <th>Model</th>
            <th>Status</th>
            <th>Evidence / Requirement</th>
          </tr>

          ${readiness.map(r => `

            <tr>

              <td>${esc(r.Model)}</td>

              <td>
                <strong>${esc(r.Status)}</strong>
              </td>

              <td>${esc(r.Basis)}</td>

            </tr>

          `).join("")}

        </table>

      </div>

      <div class="card warning">

        <h3>🔎 Data Quality Review</h3>

        ${
          unmatched.length
            ? `
              <table>

                <tr>
                  <th>Medicine</th>
                  <th>Quantity</th>
                  <th>Revenue</th>
                  <th>Date</th>
                </tr>

                ${unmatched.map(u => `

                  <tr>

                    <td>${esc(u.Medicine)}</td>
                    <td>${esc(u.Quantity)}</td>
                    <td>${esc(u.Revenue)}</td>
                    <td>${esc(u.Date)}</td>

                  </tr>

                `).join("")}

              </table>
            `
            : `<p>✓ No unmatched sales records.</p>`
        }

        <p>
          Unmatched transactions require data-quality review.
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
    await fetch("/api/snapshot");

  const text =
    await r.text();

  const box =
    document.getElementById("snapshotContent");

  if (box) {
    box.textContent = text;
  }

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
