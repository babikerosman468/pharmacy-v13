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
      const purchases = await sql`
        SELECT
          p.id,
          p.supplier_id,
          s.name AS supplier_name,
          p.medicine_id,
          m.name AS medicine_name,
          p.quantity,
          p.unit_cost,
          p.total_cost,
          p.purchase_date,
          p.batch_number,
          p.expiry,
          p.created_at
        FROM purchases p
        LEFT JOIN suppliers s
          ON s.id = p.supplier_id
        LEFT JOIN medicines m
          ON m.id = p.medicine_id
        ORDER BY p.purchase_date DESC, p.id DESC;
      `;

      return res.status(200).json(
        purchases.map(row => ({
          id: Number(row.id),
          supplier_id: row.supplier_id === null
            ? null
            : Number(row.supplier_id),
          supplier_name: row.supplier_name,
          medicine_id: row.medicine_id === null
            ? null
            : Number(row.medicine_id),
          medicine_name: row.medicine_name,
          quantity: Number(row.quantity),
          unit_cost: Number(row.unit_cost),
          total_cost: Number(row.total_cost),
          purchase_date: row.purchase_date,
          batch_number: row.batch_number,
          expiry: row.expiry,
          created_at: row.created_at
        }))
      );
    }

    if (req.method === "POST") {
      const body = req.body || {};

      const supplierId =
        body.supplier_id == null
          ? null
          : Number(body.supplier_id);

      const medicineId =
        body.medicine_id == null
          ? null
          : Number(body.medicine_id);

      const quantity = Number(body.quantity);
      const unitCost = Number(body.unit_cost);

      const batchNumber =
        body.batch_number == null
          ? null
          : String(body.batch_number).trim();

      const expiry =
        body.expiry || null;

      if (
        supplierId !== null &&
        (!Number.isInteger(supplierId) || supplierId <= 0)
      ) {
        return res.status(400).json({
          error: "Invalid supplier_id"
        });
      }

      if (
        medicineId !== null &&
        (!Number.isInteger(medicineId) || medicineId <= 0)
      ) {
        return res.status(400).json({
          error: "Invalid medicine_id"
        });
      }

      if (!Number.isInteger(quantity) || quantity <= 0) {
        return res.status(400).json({
          error: "Quantity must be a positive integer"
        });
      }

      if (!Number.isFinite(unitCost) || unitCost < 0) {
        return res.status(400).json({
          error: "Unit cost must be a non-negative number"
        });
      }

      const totalCost = quantity * unitCost;

      const result = await sql`
        INSERT INTO purchases (
          supplier_id,
          medicine_id,
          quantity,
          unit_cost,
          total_cost,
          purchase_date,
          batch_number,
          expiry
        )
        VALUES (
          ${supplierId},
          ${medicineId},
          ${quantity},
          ${unitCost},
          ${totalCost},
          CURRENT_TIMESTAMP,
          ${batchNumber},
          ${expiry}
        )
        RETURNING
          id,
          supplier_id,
          medicine_id,
          quantity,
          unit_cost,
          total_cost,
          purchase_date,
          batch_number,
          expiry,
          created_at;
      `;

      const row = result[0];

      return res.status(201).json({
        id: Number(row.id),
        supplier_id:
          row.supplier_id === null
            ? null
            : Number(row.supplier_id),
        medicine_id:
          row.medicine_id === null
            ? null
            : Number(row.medicine_id),
        quantity: Number(row.quantity),
        unit_cost: Number(row.unit_cost),
        total_cost: Number(row.total_cost),
        purchase_date: row.purchase_date,
        batch_number: row.batch_number,
        expiry: row.expiry,
        created_at: row.created_at
      });
    }

    res.setHeader("Allow", "GET, POST");

    return res.status(405).json({
      error: "Method not allowed"
    });

  } catch (error) {
    console.error("Purchases API error:", error);

    return res.status(500).json({
      error: "Database error"
    });
  }
};
