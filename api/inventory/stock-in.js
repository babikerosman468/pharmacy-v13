const { Pool } = require("pg");
const { requireAuth } = require("../../lib/auth");

let pool;

function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      max: 5,
      idleTimeoutMillis: 10000,
      connectionTimeoutMillis: 10000
    });
  }

  return pool;
}

module.exports = async function handler(req, res) {
  const user = requireAuth(req, res, [
    "administrator",
    "manager"
  ]);

  if (!user) return;


  if (req.method !== "POST") {
    return res.status(405).json({
      error: "Method not allowed"
    });
  }

  const medicineId = Number(req.body?.medicine_id);
  const quantity = Number(req.body?.quantity);

  if (!Number.isInteger(medicineId) || medicineId <= 0) {
    return res.status(400).json({
      error: "medicine_id must be a positive integer"
    });
  }

  if (!Number.isInteger(quantity) || quantity <= 0) {
    return res.status(400).json({
      error: "quantity must be a positive integer"
    });
  }

  const client = await getPool().connect();

  try {
    await client.query("BEGIN");

    const result = await client.query(
      `
      UPDATE medicines
      SET quantity = quantity + $1
      WHERE id = $2
      RETURNING id, name, quantity, price, expiry
      `,
      [quantity, medicineId]
    );

    if (result.rowCount === 0) {
      await client.query("ROLLBACK");

      return res.status(404).json({
        error: "Medicine not found",
        medicine_id: medicineId
      });
    }

    await client.query("COMMIT");

    return res.status(200).json({
      action: "stock-in",
      medicine: result.rows[0],
      added: quantity
    });

  } catch (error) {
    try {
      await client.query("ROLLBACK");
    } catch (_) {}

    console.error("STOCK_IN_TRANSACTION_ERROR", error);

    return res.status(500).json({
      error: "Transaction failed",
      message: error.message
    });

  } finally {
    client.release();
  }
};
