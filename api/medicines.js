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
    const sql = neon(process.env.DATABASE_URL);

    if (req.method === "GET") {
      const medicines = await sql`
        SELECT
          id,
          name,
          quantity,
          price,
          expiry,
          created_at
        FROM medicines
        ORDER BY id;
      `;

      return res.status(200).json(
        medicines.map(row => ({
          id: Number(row.id),
          name: row.name,
          quantity: Number(row.quantity),
          price: Number(row.price),
          expiry: row.expiry,
          created_at: row.created_at
        }))
      );
    }

    if (req.method === "POST") {
      const body = req.body || {};

      const name = String(body.name || "").trim();
      const quantity = Number(body.quantity ?? 0);
      const price = Number(body.price ?? 0);
      const expiry = body.expiry || null;

      if (!name) {
        return res.status(400).json({
          error: "Medicine name is required"
        });
      }

      if (!Number.isInteger(quantity) || quantity < 0) {
        return res.status(400).json({
          error: "Quantity must be a non-negative integer"
        });
      }

      if (!Number.isFinite(price) || price < 0) {
        return res.status(400).json({
          error: "Price must be a non-negative number"
        });
      }

      const result = await sql`
        INSERT INTO medicines (
          name,
          quantity,
          price,
          expiry
        )
        VALUES (
          ${name},
          ${quantity},
          ${price},
          ${expiry}
        )
        RETURNING
          id,
          name,
          quantity,
          price,
          expiry,
          created_at;
      `;

      const row = result[0];

      return res.status(201).json({
        id: Number(row.id),
        name: row.name,
        quantity: Number(row.quantity),
        price: Number(row.price),
        expiry: row.expiry,
        created_at: row.created_at
      });
    }

    res.setHeader("Allow", "GET, POST");

    return res.status(405).json({
      error: "Method not allowed"
    });

  } catch (error) {
    console.error("Medicines API error:", error);

    return res.status(500).json({
      error: "Database error"
    });
  }
};
