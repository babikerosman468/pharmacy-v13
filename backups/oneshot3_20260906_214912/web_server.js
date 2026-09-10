const http = require("http");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const APP = __dirname;

const DB = {
  MED: path.join(APP, "data/medicines.json"),
  SALES: path.join(APP, "data/sales.json"),
  SUPPLIERS: path.join(APP, "data/suppliers.json"),
  PURCHASES: path.join(APP, "data/purchases.json")
};

function load(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return [];
  }
}

function save(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function send(res, data, code = 200) {
  res.writeHead(code, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*"
  });
  res.end(JSON.stringify(data));
}

function python(script) {
  try {
    return execSync(
      `python "${path.join(APP, "simulation", script)}"`,
      {
        encoding: "utf8",
        timeout: 120000
      }
    );
  } catch (e) {
    return "ERROR: " + (e.stdout || e.message);
  }
}

function summary() {

  const meds = load(DB.MED);
  const sales = load(DB.SALES);

  const revenue = sales.reduce(
    (a, b) => a + Number(b.total || 0), 0
  );

  const inventoryValue = meds.reduce(
    (a, b) =>
      a +
      Number(b.quantity || 0) *
      Number(b.price || 0),
    0
  );

  const now = new Date();

  const lowStock =
    meds.filter(m => Number(m.quantity || 0) <= 10);

  const expired =
    meds.filter(m =>
      m.expiry && new Date(m.expiry) < now
    );

  const expiringSoon =
    meds.filter(m => {
      if (!m.expiry) return false;
      const days =
        (new Date(m.expiry) - now) / 86400000;
      return days >= 0 && days <= 30;
    });

  return {
    medicines: meds.length,
    sales: sales.length,
    revenue,
    inventoryValue,
    lowStock: lowStock.length,
    expired: expired.length,
    expiringSoon: expiringSoon.length
  };
}

async function body(req) {

  return new Promise((resolve, reject) => {

    let data = "";

    req.on("data", chunk => {
      data += chunk;
    });

    req.on("end", () => {

      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(e);
      }

    });
  });
}

async function router(req, res) {

  const url =
    new URL(req.url, "http://localhost");

  // ----------------------------------------------------------
  // DASHBOARD
  // ----------------------------------------------------------

  if (url.pathname === "/api/summary")
    return send(res, summary());

  // ----------------------------------------------------------
  // MEDICINES
  // ----------------------------------------------------------

  if (url.pathname === "/api/medicines") {

    const q =
      (url.searchParams.get("q") || "").toLowerCase();

    const meds = load(DB.MED);

    return send(
      res,
      meds.filter(m =>
        String(m.name || "")
          .toLowerCase()
          .includes(q)
      )
    );
  }

  // ----------------------------------------------------------
  // ADD MEDICINE
  // ----------------------------------------------------------

  if (
    req.method === "POST" &&
    url.pathname === "/api/medicines"
  ) {

    const d = await body(req);

    const meds = load(DB.MED);

    const medicine = {
      id: Date.now(),
      name: d.name,
      quantity: Number(d.quantity || 0),
      price: Number(d.price || 0),
      expiry: d.expiry || ""
    };

    meds.push(medicine);

    save(DB.MED, meds);

    return send(res, {
      success: true,
      medicine
    });
  }

  // ----------------------------------------------------------
  // SELL MEDICINE
  // ----------------------------------------------------------

  if (
    req.method === "POST" &&
    url.pathname === "/api/sell"
  ) {

    const d = await body(req);

    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    const medicine =
      meds.find(m =>
        String(m.name).toLowerCase() ===
        String(d.name).toLowerCase()
      );

    if (!medicine)
      return send(
        res,
        { error: "Medicine not found" },
        404
      );

    const qty = Number(d.qty || 0);

    if (qty <= 0)
      return send(
        res,
        { error: "Invalid quantity" },
        400
      );

    if (medicine.quantity < qty)
      return send(
        res,
        { error: "Insufficient stock" },
        400
      );

    medicine.quantity -= qty;

    const sale = {
      medicine: medicine.name,
      qty,
      total:
        qty * Number(medicine.price || 0),
      date:
        new Date().toISOString()
    };

    sales.push(sale);

    save(DB.MED, meds);
    save(DB.SALES, sales);

    return send(res, {
      success: true,
      sale
    });
  }

  // ----------------------------------------------------------
  // SALES
  // ----------------------------------------------------------

  if (url.pathname === "/api/sales")
    return send(res, load(DB.SALES));

  // ----------------------------------------------------------
  // ALERTS
  // ----------------------------------------------------------

  if (url.pathname === "/api/alerts") {

    const meds = load(DB.MED);
    const now = new Date();

    return send(res, {

      lowStock:
        meds.filter(m =>
          Number(m.quantity || 0) <= 10
        ),

      expired:
        meds.filter(m =>
          m.expiry &&
          new Date(m.expiry) < now
        ),

      expiringSoon:
        meds.filter(m => {

          if (!m.expiry) return false;

          const days =
            (new Date(m.expiry) - now) /
            86400000;

          return days >= 0 && days <= 30;
        })
    });
  }

  // ----------------------------------------------------------
  // SUPPLIERS
  // ----------------------------------------------------------

  if (url.pathname === "/api/suppliers")
    return send(res, load(DB.SUPPLIERS));

  // ----------------------------------------------------------
  // PURCHASES
  // ----------------------------------------------------------

  if (url.pathname === "/api/purchases")
    return send(res, load(DB.PURCHASES));

  // ----------------------------------------------------------
  // CASH
  // ----------------------------------------------------------

  if (url.pathname === "/api/cash") {

    const sales = load(DB.SALES);

    const today =
      new Date().toISOString().slice(0, 10);

    const todaySales =
      sales.filter(s =>
        String(s.date || "").slice(0, 10) === today
      );

    return send(res, {

      date: today,

      sales: todaySales.length,

      revenue:
        todaySales.reduce(
          (a, b) =>
            a + Number(b.total || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // INVENTORY VALUE
  // ----------------------------------------------------------

  if (url.pathname === "/api/inventory-value") {

    const meds = load(DB.MED);

    return send(res, {

      value:
        meds.reduce(
          (a, b) =>
            a +
            Number(b.quantity || 0) *
            Number(b.price || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // ANALYTICS
  // ----------------------------------------------------------

  if (url.pathname === "/api/analytics") {

    const meds = load(DB.MED);
    const sales = load(DB.SALES);

    return send(res, {

      medicines: meds.length,

      sales: sales.length,

      revenue:
        sales.reduce(
          (a, b) =>
            a + Number(b.total || 0),
          0
        ),

      inventoryValue:
        meds.reduce(
          (a, b) =>
            a +
            Number(b.quantity || 0) *
            Number(b.price || 0),
          0
        )
    });
  }

  // ----------------------------------------------------------
  // SCIENTIFIC MODELS
  // ----------------------------------------------------------

  const models = {

    forecast:
      "forecast.py",

    monteCarlo:
      "inventory_sim.py",

    reorderPoint:
      "reorder_point.py",

    safetyStock:
      "safety_stock.py",

    expiryRisk:
      "expiry_risk.py",

    abc:
      "abc_analysis.py",

    eoq:
      "eoq.py",

    ai:
      "ai_dashboard.py"
  };

  if (
    url.pathname.startsWith("/api/model/")
  ) {

    const name =
      url.pathname.split("/").pop();

    if (!models[name])
      return send(
        res,
        { error: "Unknown model" },
        404
      );

    return send(res, {

      model: name,

      output:
        python(models[name])
    });
  }

  // ----------------------------------------------------------
  // REPORTS
  // ----------------------------------------------------------

  if (url.pathname === "/api/reports") {

    const dir =
      path.join(APP, "reports");

    const files =
      fs.existsSync(dir)
        ? fs.readdirSync(dir)
        : [];

    return send(res, { files });
  }

  // ----------------------------------------------------------
  // REPORT FILE
  // ----------------------------------------------------------

  if (url.pathname === "/api/report-file") {

    const name =
      url.searchParams.get("name");

    if (!name)
      return send(
        res,
        { error: "Missing file" },
        400
      );

    const dir =
      path.join(APP, "reports");

    const file =
      path.join(dir, path.basename(name));

    if (!fs.existsSync(file))
      return send(
        res,
        { error: "File not found" },
        404
      );

    return send(res, {
      name,
      content:
        fs.readFileSync(file, "utf8")
    });
  }

  // ----------------------------------------------------------
  // SAS
  // ----------------------------------------------------------

  if (url.pathname === "/api/sas") {

    const dir =
      path.join(APP, "exports");

    const files =
      fs.existsSync(dir)
        ? fs.readdirSync(dir)
        : [];

    return send(res, {
      files
    });
  }

  // ----------------------------------------------------------
  // SNAPSHOT
  // ----------------------------------------------------------

  if (url.pathname === "/api/snapshot") {

    const file =
      path.join(
        APP,
        "reports",
        "web_snapshot.txt"
      );

    fs.writeFileSync(
      file,
      JSON.stringify(
        summary(),
        null,
        2
      )
    );

    return send(res, {
      success: true,
      file: "web_snapshot.txt"
    });
  }

  // ----------------------------------------------------------
  // HEALTH
  // ----------------------------------------------------------

  if (url.pathname === "/api/health") {

    return send(res, {

      system:
        "PHARMACY V12",

      status:
        "ONLINE",

      node:
        process.version,

      database: {

        medicines:
          fs.existsSync(DB.MED),

        sales:
          fs.existsSync(DB.SALES),

        suppliers:
          fs.existsSync(DB.SUPPLIERS),

        purchases:
          fs.existsSync(DB.PURCHASES)
      },

      simulation: {

        forecast:
          fs.existsSync(
            path.join(APP, "simulation/forecast.py")
          ),

        abc:
          fs.existsSync(
            path.join(APP, "simulation/abc_analysis.py")
          ),

        eoq:
          fs.existsSync(
            path.join(APP, "simulation/eoq.py")
          ),

        ai:
          fs.existsSync(
            path.join(APP, "simulation/ai_dashboard.py")
          )
      }
    });
  }

  // ----------------------------------------------------------
  // STATIC
  // ----------------------------------------------------------

  let file;

  if (url.pathname === "/")
    file =
      path.join(APP, "web/index.html");
  else
    file =
      path.join(
        APP,
        "web",
        url.pathname
      );

  if (
    fs.existsSync(file) &&
    fs.statSync(file).isFile()
  ) {

    const ext =
      path.extname(file);

    const types = {

      ".html":
        "text/html; charset=utf-8",

      ".css":
        "text/css; charset=utf-8",

      ".js":
        "application/javascript; charset=utf-8"
    };

    res.writeHead(200, {
      "Content-Type":
        types[ext] ||
        "text/plain; charset=utf-8"
    });

    return res.end(
      fs.readFileSync(file)
    );
  }

  send(
    res,
    { error: "Not found" },
    404
  );
}

const server =
  http.createServer((req, res) => {

    router(req, res).catch(err => {

      send(
        res,
        { error: err.message },
        500
      );

    });
  });

server.listen(
  8080,
  "0.0.0.0",
  () => {

    console.log("");
    console.log(
      "================================================"
    );
    console.log(
      " PHARMACY V12 INTERACTIVE CONTROL CENTER"
    );
    console.log(
      " http://127.0.0.1:8080"
    );
    console.log(
      "================================================"
    );
  }
);
