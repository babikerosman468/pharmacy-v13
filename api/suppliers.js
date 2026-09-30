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
      const suppliers = await sql`
        SELECT
          id,
          name,
          phone,
          address,
          created_at
        FROM suppliers
        ORDER BY id;
      `;

      return res.status(200).json(
        suppliers.map(row => ({
          id: Number(row.id),
          name: row.name,
          phone: row.phone,
          address: row.address,
          created_at: row.created_at
        }))
      );
    }

    if (req.method === "POST") {
      const body = req.body || {};

      const name = String(body.name || "").trim();
      const phone = body.phone == null
        ? null
        : String(body.phone).trim();
      const address = body.address == null
        ? null
        : String(body.address).trim();

      if (!name) {
        return res.status(400).json({
          error: "Supplier name is required"
        });
      }

      const result = await sql`
        INSERT INTO suppliers (
          name,
          phone,
          address
        )
        VALUES (
          ${name},
          ${phone},
          ${address}
        )
        RETURNING
          id,
          name,
          phone,
          address,
          created_at;
      `;

      const row = result[0];

      return res.status(201).json({
        id: Number(row.id),
        name: row.name,
        phone: row.phone,
        address: row.address,
        created_at: row.created_at
      });
    }

    res.setHeader("Allow", "GET, POST");

    return res.status(405).json({
      error: "Method not allowed"
    });

  } catch (error) {
    console.error("Suppliers API error:", error);

    return res.status(500).json({
      error: "Database error"
    });
  }
};
