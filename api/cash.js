const { neon } = require("@neondatabase/serverless");

module.exports = async function handler(req, res) {
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
        COUNT(*) AS sales_count,
        COALESCE(SUM(total), 0) AS cash_total
      FROM sales;
    `;

    const row = result[0];

    res.status(200).json({
      salesCount: Number(row.sales_count),
      cashTotal: Number(row.cash_total)
    });

  } catch (error) {
    console.error("Cash API error:", error);

    res.status(500).json({
      error: "Database error"
    });
  }
};
