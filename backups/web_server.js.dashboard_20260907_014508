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
    // DECISION MODELS
    // --------------------------------------------------------

    if (
        req.method === "GET" &&
        url.pathname.startsWith("/api/model/")
    ) {

        const name =
            url.pathname
                .replace("/api/model/", "")
                .replace(/^\/+|\/+$/g, "");

        const models = {
            "forecast": "forecast.py",
            "monte-carlo": "inventory_sim.py",
            "monteCarlo": "inventory_sim.py",
            "reorder-point": "reorder_point.py",
            "reorderPoint": "reorder_point.py",
            
"safety-stock": "safety_stock.py",
"safetyStock": "safety_stock.py",
           
		"expiry-risk": "expiry_risk.py",

"expiry-risk": "expiry_risk.py",
"expiryRisk": "expiry_risk.py",

            "abc": "abc_analysis.py",
            "eoq": "eoq.py",
            "ai": "ai_dashboard.py"
        };

        const script = models[name];

        if (!script) {
            return json(
                res,
                {
                    error: "Unknown decision model",
                    model: name
                },
                404
            );
        }

        const output =
            runPython(script);

        return json(res, {
            model: name,
            script,
            output
        });
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
