#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# PHARMACY V12 — ONESHOT3
# PDF-FIRST REPORT CENTER
# ============================================================

set -e

ROOT="$HOME/pharmacy-v12"
cd "$ROOT"

echo
echo "============================================================"
echo " PHARMACY V12 — ONESHOT3"
echo " PDF-FIRST REPORT CENTER"
echo "============================================================"
echo

# ------------------------------------------------------------
# 1. BACKUP
# ------------------------------------------------------------

STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="$ROOT/backups/oneshot3_$STAMP"

mkdir -p "$BACKUP"

echo "[1/7] Creating backup..."
cp -f web_server.js "$BACKUP/" 2>/dev/null || true
cp -rf web "$BACKUP/" 2>/dev/null || true
cp -f start_web.sh "$BACKUP/" 2>/dev/null || true

echo "Backup: $BACKUP"

# ------------------------------------------------------------
# 2. VERIFY LATEX SCRIPTS
# ------------------------------------------------------------

echo
echo "[2/7] Checking LaTeX compilation scripts..."

if [ -f "$ROOT/compiletex-clean.sh" ]; then
    echo "OK: compiletex-clean.sh"
else
    echo "WARNING: compiletex-clean.sh not found"
fi

if [ -f "$ROOT/compiletex1.sh" ]; then
    echo "OK: compiletex1.sh"
else
    echo "WARNING: compiletex1.sh not found"
fi

chmod +x "$ROOT/compiletex-clean.sh" "$ROOT/compiletex1.sh" 2>/dev/null || true

# ------------------------------------------------------------
# 3. ENSURE REPORT DIRECTORY
# ------------------------------------------------------------

echo
echo "[3/7] Preparing reports directory..."

mkdir -p "$ROOT/reports"

# ------------------------------------------------------------
# 4. CREATE PDF-FIRST WEB SERVER
# ------------------------------------------------------------

echo
echo "[4/7] Updating web server..."

cat > "$ROOT/web_server.js" <<'EOF'
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = __dirname;
const WEB = path.join(ROOT, "web");
const DATA = path.join(ROOT, "data");
const REPORTS = path.join(ROOT, "reports");
const SIMULATION = path.join(ROOT, "simulation");

const PORT = Number(process.env.PORT || 8080);

function readJSON(file, fallback = []) {
    try {
        return JSON.parse(fs.readFileSync(file, "utf8"));
    } catch {
        return fallback;
    }
}

function send(res, status, body, type = "text/html; charset=utf-8") {
    res.writeHead(status, {
        "Content-Type": type,
        "Cache-Control": "no-store"
    });
    res.end(body);
}

function json(res, data, status = 200) {
    send(res, status, JSON.stringify(data, null, 2), "application/json; charset=utf-8");
}

function safeName(name) {
    return path.basename(String(name || ""));
}

function reportFile(name) {
    const allowed = [
        "pharmacy_report.pdf",
        "pharmacy_report.txt",
        "pharmacy_report.tex",
        "snap.txt"
    ];

    const clean = safeName(name);

    if (!allowed.includes(clean)) {
        return null;
    }

    return path.join(REPORTS, clean);
}

function runPython(script) {
    try {
        return execFileSync(
            "python",
            [path.join(SIMULATION, script)],
            {
                cwd: ROOT,
                encoding: "utf8",
                timeout: 120000
            }
        );
    } catch (e) {
        return e.stdout || e.stderr || String(e);
    }
}

function compileReport() {
    const clean = path.join(ROOT, "compiletex-clean.sh");
    const compile = path.join(ROOT, "compiletex1.sh");

    if (!fs.existsSync(clean)) {
        return {
            ok: false,
            message: "compiletex-clean.sh not found"
        };
    }

    if (!fs.existsSync(compile)) {
        return {
            ok: false,
            message: "compiletex1.sh not found"
        };
    }

    try {
        execFileSync("bash", [clean], {
            cwd: ROOT,
            encoding: "utf8",
            timeout: 120000
        });

        execFileSync("bash", [compile], {
            cwd: ROOT,
            encoding: "utf8",
            timeout: 120000
        });

        const pdf = path.join(REPORTS, "pharmacy_report.pdf");

        if (!fs.existsSync(pdf)) {
            return {
                ok: false,
                message: "Compilation finished but PDF was not created"
            };
        }

        return {
            ok: true,
            message: "PDF generated successfully",
            file: "pharmacy_report.pdf"
        };

    } catch (e) {
        return {
            ok: false,
            message: e.stdout || e.stderr || e.message || String(e)
        };
    }
}

function summary() {
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
}

function reportCenter() {
    const files = [
        "pharmacy_report.pdf",
        "pharmacy_report.txt",
        "pharmacy_report.tex",
        "snap.txt"
    ];

    return {
        files: files.filter(
            f => fs.existsSync(path.join(REPORTS, f))
        ),
        primary: "pharmacy_report.pdf"
    };
}

function serveStatic(req, res) {
    let pathname = decodeURIComponent(
        new URL(req.url, `http://${req.headers.host}`).pathname
    );

    if (pathname === "/") {
        pathname = "/index.html";
    }

    const relative = pathname.replace(/^\/+/, "");
    const file = path.resolve(WEB, relative);

    if (!file.startsWith(path.resolve(WEB))) {
        return send(res, 403, "Forbidden");
    }

    if (!fs.existsSync(file)) {
        return send(res, 404, "Not Found");
    }

    const ext = path.extname(file).toLowerCase();

    const types = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".txt": "text/plain; charset=utf-8"
    };

    send(
        res,
        200,
        fs.readFileSync(file),
        types[ext] || "application/octet-stream"
    );
}

const server = http.createServer((req, res) => {

    const url = new URL(
        req.url,
        `http://${req.headers.host}`
    );

    // --------------------------------------------------------
    // SUMMARY
    // --------------------------------------------------------

    if (req.method === "GET" && url.pathname === "/api/summary") {
        return json(res, summary());
    }

    // --------------------------------------------------------
    // REPORT CENTER
    // --------------------------------------------------------

    if (req.method === "GET" && url.pathname === "/api/reports") {
        return json(res, reportCenter());
    }

    // --------------------------------------------------------
    // COMPILE REPORT
    // --------------------------------------------------------

    if (
        req.method === "POST" &&
        url.pathname === "/api/reports/compile"
    ) {
        return json(res, compileReport());
    }

    // --------------------------------------------------------
    // SERVE REPORT FILES
    // --------------------------------------------------------

    if (
        req.method === "GET" &&
        url.pathname === "/reports/file"
    ) {
        const file = reportFile(url.searchParams.get("name"));

        if (!file) {
            return send(res, 400, "Invalid report file");
        }

        if (!fs.existsSync(file)) {
            return send(res, 404, "Report file not found");
        }

        const ext = path.extname(file).toLowerCase();

        let type = "application/octet-stream";

        if (ext === ".pdf") {
            type = "application/pdf";
        } else if (ext === ".txt" || ext === ".tex") {
            type = "text/plain; charset=utf-8";
        }

        return send(res, 200, fs.readFileSync(file), type);
    }

    // --------------------------------------------------------
    // EXISTING / CORE API
    // --------------------------------------------------------

    if (req.method === "GET" && url.pathname === "/api/medicines") {
        return json(
            res,
            readJSON(path.join(DATA, "medicines.json"))
        );
    }

    if (req.method === "GET" && url.pathname === "/api/sales") {
        return json(
            res,
            readJSON(path.join(DATA, "sales.json"))
        );
    }

    if (req.method === "GET" && url.pathname === "/api/alerts") {
        const medicines = readJSON(
            path.join(DATA, "medicines.json")
        );

        return json(
            res,
            medicines.filter(
                m => Number(m.quantity || 0) <= 10
            )
        );
    }

    if (req.method === "GET" && url.pathname === "/api/snapshot") {
        const file = path.join(REPORTS, "snap.txt");

        if (!fs.existsSync(file)) {
            return send(res, 404, "Snapshot not found");
        }

        return send(
            res,
            200,
            fs.readFileSync(file),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/forecast") {
        return send(
            res,
            200,
            runPython("forecast.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/monte-carlo") {
        return send(
            res,
            200,
            runPython("inventory_sim.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/reorder-point") {
        return send(
            res,
            200,
            runPython("reorder_point.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/safety-stock") {
        return send(
            res,
            200,
            runPython("safety_stock.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/expiry-risk") {
        return send(
            res,
            200,
            runPython("expiry_risk.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/abc") {
        return send(
            res,
            200,
            runPython("abc_analysis.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/eoq") {
        return send(
            res,
            200,
            runPython("eoq.py"),
            "text/plain; charset=utf-8"
        );
    }

    if (req.method === "GET" && url.pathname === "/api/ai") {
        return send(
            res,
            200,
            runPython("ai_dashboard.py"),
            "text/plain; charset=utf-8"
        );
    }

    // --------------------------------------------------------
    // STATIC WEB
    // --------------------------------------------------------

    return serveStatic(req, res);
});

server.listen(PORT, () => {
    console.log("");
    console.log("============================================================");
    console.log(" PHARMACY V12 WEB PLATFORM");
    console.log("============================================================");
    console.log(` http://127.0.0.1:${PORT}`);
    console.log("");
});
EOF

# ------------------------------------------------------------
# 5. UPDATE REPORT CENTER UI
# ------------------------------------------------------------

echo
echo "[5/7] Updating Report Center UI..."

python - <<'PY'
from pathlib import Path

p = Path("web/index.html")

if p.exists():
    text = p.read_text(encoding="utf-8")

    marker = '<section id="reports-section"'

    if marker not in text:
        block = r'''
<section id="reports-section" class="panel">
    <h2>📑 REPORT CENTER</h2>

    <div class="report-card">
        <h3>📕 Pharmacy Report</h3>
        <p>Primary official report — PDF</p>

        <div class="report-actions">
            <a
                class="button"
                href="/reports/file?name=pharmacy_report.pdf"
                target="_blank"
            >
                View PDF
            </a>

            <a
                class="button"
                href="/reports/file?name=pharmacy_report.txt"
                target="_blank"
            >
                View TXT
            </a>

            <a
                class="button"
                href="/reports/file?name=pharmacy_report.tex"
                target="_blank"
            >
                View TEX
            </a>
        </div>

        <button onclick="compilePharmacyReport()">
            Generate / Recompile Report
        </button>

        <pre id="reportCompileStatus"></pre>
    </div>

    <div class="report-card">
        <h3>📸 Dashboard Snapshot</h3>

        <a
            class="button"
            href="/reports/file?name=snap.txt"
            target="_blank"
        >
            View Snapshot
        </a>
    </div>

    <div class="report-card">
        <h3>ℹ️ Report Policy</h3>
        <p>
            PDF is the primary report.
            Auxiliary LaTeX files (.aux, .log, .out)
            are intentionally excluded from the Report Center.
        </p>
    </div>
</section>
'''

        text = text.replace("</body>", block + "\n</body>")

    p.write_text(text, encoding="utf-8")

# Add compile function to web app JS
js = Path("web/app.js")

if js.exists():
    text = js.read_text(encoding="utf-8")

    if "compilePharmacyReport" not in text:
        text += r'''

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
'''

    js.write_text(text, encoding="utf-8")

PY

# ------------------------------------------------------------
# 6. REMOVE AUXILIARY REPORT FILES FROM OLD REPORT LISTING
# ------------------------------------------------------------

echo
echo "[6/7] Cleaning visible report artifacts..."

# We do NOT delete the .tex source.
# Remove only generated auxiliary files.

rm -f \
    "$ROOT/reports/pharmacy_report.aux" \
    "$ROOT/reports/pharmacy_report.log" \
    "$ROOT/reports/pharmacy_report.out"

echo "Auxiliary files removed from reports/."

# ------------------------------------------------------------
# 7. TEST
# ------------------------------------------------------------

echo
echo "[7/7] Testing..."

node --check "$ROOT/web_server.js"

if [ -f "$ROOT/web/index.html" ]; then
    echo "OK: web/index.html"
fi

if [ -f "$ROOT/web/app.js" ]; then
    echo "OK: web/app.js"
fi

echo
echo "============================================================"
echo " ONESHOT3 COMPLETE"
echo "============================================================"
echo
echo "Report Center:"
echo "  PDF  : reports/pharmacy_report.pdf"
echo "  TXT  : reports/pharmacy_report.txt"
echo "  TEX  : reports/pharmacy_report.tex"
echo "  SNAP : reports/snap.txt"
echo
echo "Excluded:"
echo "  *.aux"
echo "  *.log"
echo "  *.out"
echo
echo "Compilation:"
echo "  ./compiletex-clean.sh"
echo "  ./compiletex1.sh"
echo
echo "Start web platform:"
echo "  ./start_web.sh"
echo
echo "Open:"
echo "  http://127.0.0.1:8080"
echo
echo "============================================================"

