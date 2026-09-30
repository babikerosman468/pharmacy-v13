const { neon } = require("@neondatabase/serverless");
const {
  login,
  me
} = require("../lib/auth");

module.exports = async function handler(req, res) {
  const started = Date.now();

  try {

    if (req.query.route === "auth-login") {
      return login(req, res);
    }

    if (req.query.route === "auth-me") {
      return me(req, res);
    }

    if (req.query.route === "cash") {

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

      return res.status(200).json({
        salesCount: Number(row.sales_count),
        cashTotal: Number(row.cash_total)
      });
    }

    if (req.method !== "GET") {
      res.setHeader("Allow", "GET");

      return res.status(405).json({
        error: "Method not allowed"
      });
    }

    const sql = neon(process.env.DATABASE_URL);

    const result = await sql`
      SELECT
        current_database() AS database_name,
        current_user AS database_user,
        current_timestamp AS server_time,
        (SELECT COUNT(*) FROM medicines) AS medicines,
        (SELECT COUNT(*) FROM sales) AS sales,
        (SELECT COUNT(*) FROM suppliers) AS suppliers,
        (SELECT COUNT(*) FROM purchases) AS purchases;
    `;

    const row = result[0];

    res.status(200).json({
      status: "healthy",
      service: "Pharmacy V13 Cloud API",
      version: "13.0.0",
      database: {
        connected: true,
        name: row.database_name,
        user: row.database_user
      },
      data: {
        medicines: Number(row.medicines),
        sales: Number(row.sales),
        suppliers: Number(row.suppliers),
        purchases: Number(row.purchases)
      },
      serverTime: row.server_time,
      responseTimeMs: Date.now() - started
    });

  } catch (error) {

    console.error("Health/Auth API error:", error);

    res.status(500).json({
      error: "API error",
      responseTimeMs: Date.now() - started
    });
  }
};
