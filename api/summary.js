const { neon } = require("@neondatabase/serverless");

module.exports = async function handler(req, res) {
  try {
    const sql = neon(process.env.DATABASE_URL);

    const result = await sql`
      SELECT
        (SELECT COUNT(*) FROM medicines) AS medicines,
        (SELECT COUNT(*) FROM sales) AS sales,
        (SELECT COALESCE(SUM(total), 0) FROM sales) AS revenue,
        (
          SELECT COALESCE(SUM(quantity * price), 0)
          FROM medicines
        ) AS "inventoryValue",
        (
          SELECT COUNT(*)
          FROM medicines
          WHERE quantity <= 10
        ) AS "lowStock",
        (
          SELECT COUNT(*)
          FROM medicines
          WHERE expiry < CURRENT_DATE
        ) AS expired,
        (
          SELECT COUNT(*)
          FROM medicines
          WHERE expiry >= CURRENT_DATE
            AND expiry <= CURRENT_DATE + INTERVAL '30 days'
        ) AS "expiringSoon";
    `;

    const row = result[0];

    res.status(200).json({
      medicines: Number(row.medicines),
      sales: Number(row.sales),
      revenue: Number(row.revenue),
      inventoryValue: Number(row.inventoryValue),
      lowStock: Number(row.lowStock),
      expired: Number(row.expired),
      expiringSoon: Number(row.expiringSoon)
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({
      error: "Database error"
    });
  }
};
