const fs = require("fs");
const path = require("path");

module.exports = (req, res) => {
  try {
    const dir = path.join(process.cwd(), "exports");

    const files = fs.readdirSync(dir)
      .filter(name => name.endsWith(".sas"));

    res.status(200).json({
      files,
      directory: "exports"
    });

  } catch (err) {
    res.status(500).json({
      error: "SAS export directory unavailable",
      detail: err.message
    });
  }
};
