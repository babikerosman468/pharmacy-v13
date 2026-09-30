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

    const sales = await sql`
      SELECT
        id,
        medicine_id,
        medicine_name,
        quantity,
        unit_price,
        total,
        sold_at
      FROM sales
      ORDER BY sold_at DESC, id DESC;
    `;

    res.status(200).json(
      sales.map(row => ({
        id: Number(row.id),
        medicine_id: row.medicine_id === null
          ? null
          : Number(row.medicine_id),
        medicine_name: row.medicine_name,
        quantity: Number(row.quantity),
        unit_price: row.unit_price === null
          ? null
          : Number(row.unit_price),
        total: Number(row.total),
        sold_at: row.sold_at
      }))
    );

  } catch (error) {
    console.error("Sales API error:", error);

    res.status(500).json({
      error: "Database error"
    });
  }
};
