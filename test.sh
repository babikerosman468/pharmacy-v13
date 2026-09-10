#!/data/data/com.termux/files/usr/bin/bash

set -u

ROOT="$HOME/pharmacy-v13"
cd "$ROOT" || exit 1

PASS=0
FAIL=0

ok() {
    echo "  ✅ $1"
    PASS=$((PASS+1))
}

fail() {
    echo "  ❌ $1"
    FAIL=$((FAIL+1))
}

check_file() {
    if [ -f "$1" ]; then
        ok "$1"
    else
        fail "Missing: $1"
    fi
}

echo "============================================================"
echo " PHARMACY MANAGEMENT SYSTEM V13"
echo " VERIFICATION TEST"
echo "============================================================"
echo

echo "[1] Core files"
check_file app12.js
check_file start.sh
check_file start_web.sh
check_file web_server.js
check_file web/index.html
check_file web/app.js
check_file web/style.css
echo

echo "[2] Data files"
check_file data/medicines.json
check_file data/sales.json
check_file data/audit.json
check_file data/suppliers.json
check_file data/purchases.json
echo

echo "[3] JSON integrity"
for f in \
    data/medicines.json \
    data/sales.json \
    data/audit.json \
    data/suppliers.json \
    data/purchases.json
do
    if node -e "JSON.parse(require('fs').readFileSync('$f','utf8'))"; then
        ok "Valid JSON: $f"
    else
        fail "Invalid JSON: $f"
    fi
done
echo

echo "[4] Node.js syntax"
if node --check app12.js; then
    ok "app12.js syntax"
else
    fail "app12.js syntax"
fi

if node --check web_server.js; then
    ok "web_server.js syntax"
else
    fail "web_server.js syntax"
fi

if node --check web/app.js; then
    ok "web/app.js syntax"
else
    fail "web/app.js syntax"
fi
echo

echo "[5] Python decision models"

for f in \
    simulation/forecast.py \
    simulation/inventory_sim.py \
    simulation/reorder_point.py \
    simulation/safety_stock.py \
    simulation/expiry_risk.py \
    simulation/abc_analysis.py \
    simulation/eoq.py \
    simulation/ai_dashboard.py
do
    if python "$f" >/dev/null 2>&1; then
        ok "Python model: $f"
    else
        fail "Python model failed: $f"
    fi
done
echo

echo "[6] Report system"
check_file compiletex-clean.sh
check_file compiletex1.sh
check_file reports/pharmacy_report.pdf
check_file reports/pharmacy_report.txt
check_file reports/pharmacy_report.tex
echo

echo "[7] Report Center routes"

if grep -q "/reports/file" web_server.js; then
    ok "Report file route"
else
    fail "Report file route"
fi

if grep -q "View PDF" web/index.html; then
    ok "View PDF link"
else
    fail "View PDF link"
fi

if grep -q "View TXT" web/index.html; then
    ok "View TXT link"
else
    fail "View TXT link"
fi

if grep -q "View TEX" web/index.html; then
    ok "View TEX link"
else
    fail "View TEX link"
fi
echo

echo "[8] Decision API mappings"

for name in \
    forecast \
    monte-carlo \
    reorder-point \
    safety-stock \
    expiry-risk \
    abc \
    eoq \
    ai
do
    if grep -q "\"$name\"" web_server.js; then
        ok "API model mapping: $name"
    else
        fail "Missing API model mapping: $name"
    fi
done

echo
echo "============================================================"
echo " RESULTS"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo

if [ "$FAIL" -eq 0 ]; then
    echo "🎉 V13 VERIFICATION: ALL TESTS PASSED"
    exit 0
else
    echo "⚠️ V13 VERIFICATION: FAILURES DETECTED"
    exit 1
fi
