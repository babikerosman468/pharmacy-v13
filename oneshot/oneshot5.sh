#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "============================================================"
echo " PHARMACY V13 — DASHBOARD SUMMARY UPGRADE"
echo "============================================================"

STAMP=$(date +%Y%m%d_%H%M%S)

echo
echo "[1/6] Backup web_server.js"
cp web_server.js "backups/web_server.js.dashboard_$STAMP"

echo
echo "[2/6] Patching summary()"

python - <<'PY'
from pathlib import Path

p = Path("web_server.js")
s = p.read_text()

old = '''function summary() {
    const medicines = readJSON(path.join(DATA, "medicines.json"));
    const sales = readJSON(path.join(DATA, "sales.json"));

    const revenue = sales.reduce(
        (sum, s) => sum + Number(s.total || 0),
        0
    );

    const inventoryValue = medicines.reduce(
        (sum, m) =>
            sum +
            Number(m.price || 0) *
            Number(m.quantity || 0),
        0
    );

    const lowStock = medicines.filter(
        m => Number(m.quantity || 0) <= 10
    ).length;

    return {
        medicines: medicines.length,
        sales: sales.length,
        revenue,
        inventoryValue,
        lowStock
    };
}'''

new = '''function summary() {
    const medicines = readJSON(path.join(DATA, "medicines.json"));
    const sales = readJSON(path.join(DATA, "sales.json"));

    const revenue = sales.reduce(
        (sum, s) => sum + Number(s.total || 0),
        0
    );

    const inventoryValue = medicines.reduce(
        (sum, m) =>
            sum +
            Number(m.price || 0) *
            Number(m.quantity || 0),
        0
    );

    const lowStock = medicines.filter(
        m => Number(m.quantity || 0) <= 10
    ).length;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const ninetyDays = new Date(today);
    ninetyDays.setDate(ninetyDays.getDate() + 90);

    const expired = medicines.filter(m => {
        if (!m.expiry) return false;
        const expiry = new Date(m.expiry + "T00:00:00");
        return expiry < today;
    }).length;

    const expiringSoon = medicines.filter(m => {
        if (!m.expiry) return false;
        const expiry = new Date(m.expiry + "T00:00:00");
        return expiry >= today && expiry <= ninetyDays;
    }).length;

    return {
        medicines: medicines.length,
        sales: sales.length,
        revenue,
        inventoryValue,
        lowStock,
        expired,
        expiringSoon
    };
}'''

if old not in s:
    raise SystemExit("ERROR: expected summary() block not found")

p.write_text(s.replace(old, new))

print("summary() upgraded successfully.")
PY

echo
echo "[3/6] Node syntax check"
node --check web_server.js

echo
echo "[4/6] Test summary calculation"
node - <<'NODE'
const fs = require('fs');

const medicines =
    JSON.parse(fs.readFileSync('data/medicines.json', 'utf8'));

const today = new Date();
today.setHours(0, 0, 0, 0);

const ninetyDays = new Date(today);
ninetyDays.setDate(ninetyDays.getDate() + 90);

const expired = medicines.filter(m => {
    if (!m.expiry) return false;
    return new Date(m.expiry + "T00:00:00") < today;
}).length;

const expiringSoon = medicines.filter(m => {
    if (!m.expiry) return false;
    const d = new Date(m.expiry + "T00:00:00");
    return d >= today && d <= ninetyDays;
}).length;

console.log("Medicines:", medicines.length);
console.log("Expired:", expired);
console.log("Expiring Soon (90 days):", expiringSoon);
NODE

echo
echo "[5/6] Check required summary fields"
grep -n -A55 '^function summary' web_server.js | \
    grep -E 'expired|expiringSoon|return|lowStock'

echo
echo "[6/6] Dashboard upgrade complete"
echo
echo "Backup:"
echo "backups/web_server.js.dashboard_$STAMP"
echo
echo "============================================================"
echo " V13 DASHBOARD SUMMARY: PASS"
echo "============================================================"
