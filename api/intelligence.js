const fs = require("fs");
const { requireAuth } = require("../lib/auth");
const path = require("path");

const BASE = path.join(
  process.cwd(),
  "reem",
  "reem_v2"
);

function readJSON(file) {
  return JSON.parse(
    fs.readFileSync(
      path.join(BASE, file),
      "utf8"
    )
  );
}

function fileExists(file) {
  return fs.existsSync(
    path.join(BASE, file)
  );
}

function readCSV(file) {
  const full = path.join(BASE, file);

  if (!fs.existsSync(full)) {
    return [];
  }

  const text = fs.readFileSync(
    full,
    "utf8"
  ).trim();

  if (!text) {
    return [];
  }

  const lines = text.split(/\r?\n/);

  if (lines.length < 2) {
    return [];
  }

  const headers = lines[0]
    .split(",")
    .map(x => x.trim());

  return lines.slice(1).map(line => {
    const values = line.split(",");
    const row = {};

    headers.forEach((header, i) => {
      row[header] =
        values[i] === undefined
          ? ""
          : values[i].trim();
    });

    return row;
  });
}

function send(res, status, data) {
  return res.status(status).json(data);
}

module.exports = async function handler(req, res) {
  const user = requireAuth(req, res, [
    "administrator",
    "manager",
    "analyst",
    "viewer"
  ]);

  if (!user) return;



  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");

    return send(res, 405, {
      error: "Method not allowed"
    });
  }

  try {

    const mode =
      req.query.mode ||
      req.query.action ||
      "summary";

    /*
     * ---------------------------------------------------------
     * PHARMACY V13 SUMMARY
     * ---------------------------------------------------------
     */

    if (mode === "summary") {

      const medicines = readJSON(
        "ai_intelligence_context.json"
      );

      const decisions = readJSON(
        "ai_management_decisions.json"
      );

      return send(res, 200, {
        system: "Pharmacy V13",
        layer: "REEM V2",
        dataSource: decisions.data_source,
        dataStatus: decisions.data_status,
        operationalUse: decisions.operational_use,
        medicineCount:
          medicines.summary &&
          medicines.summary.medicine_count
            ? medicines.summary.medicine_count
            : decisions.medicine_count,
        priorityCounts:
          decisions.priority_counts || {},
        signalCounts:
          medicines.summary &&
          medicines.summary.signal_counts
            ? medicines.summary.signal_counts
            : {},
        modelsIntegrated: 8,
        status: "READY"
      });
    }

    /*
     * ---------------------------------------------------------
     * PHARMACY V13 SNAPSHOT
     * ---------------------------------------------------------
     */

    if (mode === "snapshot") {

      const context = readJSON(
        "ai_intelligence_context.json"
      );

      const decisions = readJSON(
        "ai_management_decisions.json"
      );

      return send(res, 200, {
        system: "Pharmacy V13",
        layer: "REEM V2",
        snapshot: {
          medicineCount:
            decisions.medicine_count,
          priorityCounts:
            decisions.priority_counts || {},
          signalCounts:
            context.summary &&
            context.summary.signal_counts
              ? context.summary.signal_counts
              : {}
        },
        evidence: {
          dataSource:
            decisions.data_source,
          dataStatus:
            decisions.data_status,
          operationalUse:
            decisions.operational_use
        },
        modelsIntegrated: 8,
        status: "READY"
      });
    }

    /*
     * ---------------------------------------------------------
     * REEM DRUG INTELLIGENCE
     * ---------------------------------------------------------
     */

    if (mode === "drugs") {

      const data = readJSON(
        "ai_management_decisions.json"
      );

      return send(res, 200, {
        system: "REEM V2",
        layer: "AI Decision Intelligence",
        dataSource: data.data_source,
        dataStatus: data.data_status,
        operationalUse: data.operational_use,
        medicineCount: data.medicine_count,
        priorityCounts:
          data.priority_counts || {},
        decisions:
          data.decisions || []
      });
    }

    /*
     * ---------------------------------------------------------
     * REEM READINESS
     * ---------------------------------------------------------
     */

    
if (mode === "suppliers") {

  const file =
    "reem/reem_v2/supplier_intelligence.csv";

  const csv =
    fs.readFileSync(file, "utf8").trim();

  const lines = csv.split(/\r?\n/);

  const headers =
    lines.shift().split(",");

  const suppliers =
    lines.map(line => {

      const values = line.split(",");

      const row = {};

      headers.forEach((header, i) => {
        row[header] = values[i];
      });

      return row;
    });

  return send(res, 200, {
    system: "Pharmacy V13",
    layer: "REEM V2",
    model: "Supplier Intelligence",
    dataSource: "SIMULATED_REEM_V2",
    dataStatus: "DEVELOPMENT",
    operationalUse: "PROHIBITED",
    supplierCount: suppliers.length,
    suppliers
  });
}

if (mode === "readiness") {

      const required = [
        "reem_management_intelligence.csv",
        "ai_intelligence_context.json",
        "ai_management_decisions.json",
        "demand_model.csv",
        "abc_intelligence.csv",
        "expiry_intelligence.csv",
        "stock_coverage.csv",
        "supplier_intelligence.csv",
        "rop_intelligence.csv",
        "safety_stock_intelligence.csv",
        "eoq_intelligence.csv"
      ];

      const files = {};

      for (const file of required) {
        files[file] =
          fileExists(file);
      }

      const ready =
        Object.values(files)
          .every(Boolean);

      return send(res, 200, {
        system: "REEM V2",
        status:
          ready
            ? "READY"
            : "INCOMPLETE",
        dataSource:
          "SIMULATED_REEM_V2",
        dataStatus:
          "DEVELOPMENT",
        operationalUse:
          "PROHIBITED",
        modelsIntegrated: 8,
        files
      });
    }


    /*
     * ---------------------------------------------------------
     * REEM V2 FORECAST
     * ---------------------------------------------------------
     */

    if (mode === "forecast") {

      const rows =
        readCSV("demand_model.csv");

      return send(res, 200, {
        system: "Pharmacy V13",
        layer: "REEM V2",
        model: "Demand Forecasting",
        dataSource: "SIMULATED_REEM_V2",
        dataStatus: "DEVELOPMENT",
        operationalUse: "PROHIBITED",
        medicineCount: rows.length,
        forecasts: rows
      });
    }

    /*
     * ---------------------------------------------------------
     * REEM UNMATCHED
     * ---------------------------------------------------------
     */

    if (
      mode === "monteCarlo" ||
      mode === "reorderPoint" ||
      mode === "safetyStock" ||
      mode === "expiryRisk" ||
      mode === "abc" ||
      mode === "eoq" ||
      mode === "ai"
    ) {

      const files = {
        monteCarlo: "risk.csv",
        reorderPoint: "rop_intelligence.csv",
        safetyStock: "safety_stock_intelligence.csv",
        expiryRisk: "expiry_intelligence.csv",
        abc: "abc_intelligence.csv",
        eoq: "eoq_intelligence.csv"
      };

      if (mode === "ai") {
        return send(res, 200, {
          system: "Pharmacy V13",
          layer: "REEM V2",
          model: "AI Management Intelligence",
          dataSource: "SIMULATED_REEM_V2",
          dataStatus: "DEVELOPMENT",
          operationalUse: "PROHIBITED",
          data: readJSON(
            "ai_management_decisions.json"
          )
        });
      }

      const rows =
        readCSV(
          files[mode]
        );

      return send(res, 200, {
        system: "Pharmacy V13",
        layer: "REEM V2",
        model: mode,
        dataSource: "SIMULATED_REEM_V2",
        dataStatus: "DEVELOPMENT",
        operationalUse: "PROHIBITED",
        recordCount: rows.length,
        data: rows
      });
    }

    if (mode === "unmatched") {

      const rows =
        readCSV("unmatched.csv");

      return send(res, 200, {
        system: "REEM V2",
        dataSource:
          "SIMULATED_REEM_V2",
        dataStatus:
          "DEVELOPMENT",
        operationalUse:
          "PROHIBITED",
        count: rows.length,
        unmatched: rows
      });
    }

    return send(res, 400, {
      error:
        "Unknown intelligence mode",

      allowedModes: [
        "summary",
        "snapshot",
        "drugs",
        "readiness",
        "forecast",
        "unmatched"
      ]
    });

  } catch (error) {

    console.error(
      "V13 INTELLIGENCE ERROR",
      error
    );

    return send(res, 500, {
      error:
        "V13 intelligence unavailable",
      message:
        error.message
    });
  }
};
