#!/data/data/com.termux/files/usr/bin/bash

set -e

ROOT="$HOME/pharmacy-v12"
cd "$ROOT"

STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="backups/oneshot4_$STAMP"

echo "============================================================"
echo " PHARMACY V12 — ONESHOT4"
echo " REMOVE DUPLICATE LEGACY REPORT LIST"
echo "============================================================"

echo "[1/4] Backup..."
mkdir -p "$BACKUP"
cp web/app.js "$BACKUP/web_app.js" 2>/dev/null || true
cp web/index.html "$BACKUP/index.html" 2>/dev/null || true
cp web_server.js "$BACKUP/web_server.js" 2>/dev/null || true
echo "Backup: $BACKUP"

echo "[2/4] Removing legacy Reports Center renderer..."

python - <<'PY'
from pathlib import Path

p = Path("web/app.js")

if not p.exists():
    print("web/app.js not found")
    raise SystemExit(0)

s = p.read_text(encoding="utf-8")

# Remove the old report-list rendering function if present.
start_markers = [
    "## Reports Center",
    "pharmacy_report.pdf",
]

if "## Reports Center" in s and "pharmacy_report.pdf" in s:
    print("Legacy report renderer detected.")

    # Remove complete template/function containing the old block.
    lines = s.splitlines()
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if "## Reports Center" in line:
            # Skip the old HTML template block until its template closes.
            # Usually this is inside an innerHTML/template literal.
            quote_count = line.count("`")
            i += 1

            while i < len(lines):
                result_line = lines[i]
                quote_count += result_line.count("`")

                if quote_count % 2 == 1:
                    i += 1
                    break

                i += 1

            continue

        result.append(line)
        i += 1

    p.write_text("\n".join(result) + "\n", encoding="utf-8")
    print("Legacy block removed.")
else:
    print("Legacy block not found in web/app.js.")

PY

echo "[3/4] Removing exact legacy text from HTML if present..."

python - <<'PY'
from pathlib import Path

for name in ["web/index.html", "web/app.js"]:
    p = Path(name)

    if not p.exists():
        continue

    s = p.read_text(encoding="utf-8")

    # Exact old visible block.
    old = """## Reports Center
**📄 pharmacy_report.pdf**View
**📄 pharmacy_report.txt**View
**📄 pharmacy_report.tex**View"""

    if old in s:
        s = s.replace(old, "")
        p.write_text(s, encoding="utf-8")
        print("Removed exact block from", name)
PY

echo "[4/4] Verification..."

echo
echo "Remaining references:"
grep -Rni "## Reports Center" web 2>/dev/null || true

echo
echo "Working Report Center links:"
grep -Rni "View PDF\|View TXT\|View TEX" web web_server.js 2>/dev/null || true

echo
echo "============================================================"
echo " ONESHOT4 COMPLETE"
echo "============================================================"
echo "Backup: $BACKUP"
echo "============================================================"
