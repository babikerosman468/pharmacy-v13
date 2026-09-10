#!/data/data/com.termux/files/usr/bin/bash

set -e

ROOT="$HOME/pharmacy-v12"
cd "$ROOT"

STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="backups/oneshot4_$STAMP"

echo "============================================================"
echo " PHARMACY V12 — ONESHOT4"
echo " REPORT CENTER UI CLEANUP"
echo "============================================================"

echo "[1/4] Backup..."
mkdir -p "$BACKUP"
cp web/app.js "$BACKUP/web_app.js"
cp web/index.html "$BACKUP/index.html"
cp web_server.js "$BACKUP/web_server.js"

echo "Backup: $BACKUP"

echo "[2/4] Locating legacy report renderer..."

grep -n -B 5 -A 20 "reportsContent" web/app.js || true

echo "[3/4] Replacing only the legacy Reports renderer..."

python - <<'PY'
from pathlib import Path
import re

p = Path("web/app.js")
s = p.read_text(encoding="utf-8")

# Find the function/handler that writes to reportsContent.
# We replace its old dynamic file-list rendering with a no-op,
# because the official Report Center is already in index.html.

patterns = [
    r'function\s+\w*Reports?\w*\s*\([^)]*\)\s*\{.*?reportsContent.*?\n\}',
    r'async\s+function\s+\w*Reports?\w*\s*\([^)]*\)\s*\{.*?reportsContent.*?\n\}',
]

for pattern in patterns:
    m = re.search(pattern, s, re.S)
    if m:
        old = m.group(0)

        if "reportsContent" in old and (
            "pharmacy_report.pdf" in old or
            "data.files" in old or
            "files.map" in old
        ):
            name = re.search(r'(?:function|async function)\s+(\w+)', old)
            fn = name.group(1) if name else "renderReports"

            replacement = f'''function {fn}() {{
    // Official Report Center is rendered directly in index.html.
    // Do not replace it with the legacy dynamic file list.
}}
'''
            s = s[:m.start()] + replacement + s[m.end():]
            p.write_text(s, encoding="utf-8")
            print("Replaced legacy renderer:", fn)
            break
else:
    print("Legacy renderer pattern not automatically matched.")
    print("No destructive change made.")

PY

echo "[4/4] Verification..."

node --check web/app.js
node --check web_server.js

echo
echo "Report Center references:"
grep -n "reportsContent\|pharmacy_report.pdf\|View PDF" web/app.js web/index.html | head -30 || true

echo
echo "============================================================"
echo " ONESHOT4 COMPLETE"
echo "============================================================"
echo "Backup: $BACKUP"
echo "Official Report Center preserved."
echo "Backend unchanged."
echo "============================================================"
