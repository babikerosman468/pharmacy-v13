#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "============================================================"
echo " PHARMACY V13 — WEB LAUNCHER FIX"
echo "============================================================"

STAMP=$(date +%Y%m%d_%H%M%S)

echo
echo "[1/5] Backup start_web.sh"
cp start_web.sh "backups/start_web.sh.before_v13_fix_$STAMP"

echo
echo "[2/5] Fixing V12 → V13 path"

python - <<'PY'
from pathlib import Path

p = Path("start_web.sh")
s = p.read_text()

s = s.replace(
    'cd "$HOME/pharmacy-v12"',
    'cd "$HOME/pharmacy-v13"'
)

s = s.replace(
    'PHARMACY V12 INTERACTIVE CONTROL CENTER',
    'PHARMACY V13 INTERACTIVE CONTROL CENTER'
)

s = s.replace(
    'PHARMACY V12 WEB PLATFORM',
    'PHARMACY V13 WEB PLATFORM'
)

p.write_text(s)

print("V13 launcher updated.")
PY

echo
echo "[3/5] Verify launcher"
grep -n -E 'cd |PHARMACY V' start_web.sh

echo
echo "[4/5] Syntax check"
bash -n start_web.sh
node --check web_server.js

echo
echo "[5/5] PASS"
echo "Backup: backups/start_web.sh.before_v13_fix_$STAMP"

echo
echo "============================================================"
echo " V13 WEB LAUNCHER: PASS"
echo "============================================================"
