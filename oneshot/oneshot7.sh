#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "============================================================"
echo " PHARMACY V13 — PROFESSIONAL DASHBOARD UI"
echo "============================================================"

STAMP=$(date +%Y%m%d_%H%M%S)

echo
echo "[1/6] Backup dashboard files"

cp web/index.html "backups/index.html.dashboard_$STAMP"
cp web/app.js "backups/app.js.dashboard_$STAMP"

echo
echo "[2/6] Add operational status panel"

python - <<'PY'
from pathlib import Path

p = Path("web/index.html")
s = p.read_text()

marker = '''</div>

</section>

<!-- MEDICINES -->'''

insert = '''</div>

<div class="dashboard-status">

<h3>📊 Operational Status</h3>

<div class="status-grid">

<div>
<strong>Inventory</strong>
<span id="inventoryStatus">Loading...</span>
</div>

<div>
<strong>Stock Alerts</strong>
<span id="stockStatus">Loading...</span>
</div>

<div>
<strong>Expiry Status</strong>
<span id="expiryStatus">Loading...</span>
</div>

<div>
<strong>Decision Support</strong>
<span>🤖 AI Ready</span>
</div>

</div>

</div>

</section>

<!-- MEDICINES -->'''

if marker not in s:
    raise SystemExit("Dashboard insertion point not found")

s = s.replace(marker, insert, 1)

p.write_text(s)
print("Operational status panel added.")
PY

echo
echo "[3/6] Add dashboard status logic"

python - <<'PY'
from pathlib import Path

p = Path("web/app.js")
s = p.read_text()

old = '''  expiringSoon.textContent =
    d.expiringSoon;
}'''

new = '''  expiringSoon.textContent =
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
}'''

if old not in s:
    raise SystemExit("loadDashboard() insertion point not found")

p.write_text(s.replace(old, new, 1))
print("Dashboard status logic added.")
PY

echo
echo "[4/6] Add dashboard styling"

cat >> web/style.css <<'CSS'

/* ============================================================
   PHARMACY V13 — PROFESSIONAL DASHBOARD
   ============================================================ */

.dashboard-status {
  margin-top: 24px;
  padding: 20px;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}

.dashboard-status h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.status-grid > div {
  padding: 14px;
  border-radius: 10px;
  background: #f7f9fb;
}

.status-grid strong {
  display: block;
  margin-bottom: 7px;
}

.status-grid span {
  font-size: 14px;
}

@media (max-width: 800px) {
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
}

CSS

echo
echo "[5/6] Syntax verification"

node --check web/app.js
node --check web_server.js
bash -n start_web.sh

echo
echo "[6/6] Dashboard UI upgrade complete"

echo
echo "Backup files:"
echo "  backups/index.html.dashboard_$STAMP"
echo "  backups/app.js.dashboard_$STAMP"

echo
echo "============================================================"
echo " V13 PROFESSIONAL DASHBOARD: PASS"
echo "============================================================"
