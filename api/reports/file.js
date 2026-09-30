const fs = require("fs");
const { requireAuth } = require("../../lib/auth");
const path = require("path");

module.exports = (req, res) => {
  try {
    const name = String(req.query.name || "");

    const allowed = {
      "pharmacy_report.pdf": {
        type: "application/pdf"
      },
      "pharmacy_report.txt": {
        type: "text/plain; charset=utf-8"
      },
      "pharmacy_report.tex": {
        type: "text/plain; charset=utf-8"
      },

      "pharmacy_v13_system.pdf": {
        type: "application/pdf"
      },
      "pharmacy_v13_system.tex": {
        type: "text/plain; charset=utf-8"
      },

      "reem_v2_report.pdf": {
        type: "application/pdf"
      },
      "reem_v2_report.tex": {
        type: "text/plain; charset=utf-8"
      },

      "5cs_pharmacy_v13.pdf": {
        type: "application/pdf"
      },
      "5cs_pharmacy_v13.tex": {
        type: "text/plain; charset=utf-8"
      }
    };

    if (!allowed[name]) {
      return res.status(400).json({
        error: "Invalid report name"
      });
    }

    const file = path.join(process.cwd(), "reports", name);

    if (!fs.existsSync(file)) {
      return res.status(404).json({
        error: "Report not found",
        name
      });
    }

    res.setHeader("Content-Type", allowed[name].type);
    res.setHeader(
      "Content-Disposition",
      `inline; filename="${name}"`
    );

    return res.status(200).send(fs.readFileSync(file));
  } catch (error) {
    return res.status(500).json({
      error: "Report delivery failed",
      message: error.message
    });
  }
};
