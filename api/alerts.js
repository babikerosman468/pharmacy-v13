const { neon } = require("@neondatabase/serverless");
const { requireAuth } = require("../lib/auth");

module.exports = async function handler(req, res) {
  const user = requireAuth(req, res, [
    "administrator",
    "manager",
    "analyst",
    "viewer"
  ]);

  if (!user) return;


  try {
    if (req.method !== "GET") {
      res.setHeader("Allow", "GET");
      return res.status(405).json({
        error: "Method not allowed"
      });
    }

    const sql = neon(process.env.DATABASE_URL);

    const result = await sql`
      SELECT
        COUNT(*) FILTER (
          WHERE quantity <= 10
        ) AS low_stock,

        COUNT(*) FILTER (
          WHERE expiry < CURRENT_DATE
        ) AS expired,

        COUNT(*) FILTER (
          WHERE expiry >= CURRENT_DATE
            AND expiry <= CURRENT_DATE + INTERVAL '90 days'
        ) AS expiring_soon

      FROM medicines;
    `;

    const row = result[0];

    res.status(200).json({
      lowStock: Number(row.low_stock),
      expired: Number(row.expired),
      expiringSoon: Number(row.expiring_soon)
    });

  } catch (error) {
    console.error("Alerts API error:", error);

    res.status(500).json({
      error: "Database error"
    });
  }
};
