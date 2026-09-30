const { neon } = require("@neondatabase/serverless");

module.exports = async function handler(req, res) {

  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");

    return res.status(405).json({
      error: "Method not allowed"
    });
  }

  try {

    if (!process.env.DATABASE_URL) {
      return res.status(503).json({
        error: "Authentication database unavailable"
      });
    }

    const body = req.body || {};

    const name =
      String(body.name || "").trim();

    const email =
      String(body.email || "")
        .trim()
        .toLowerCase();

    const requestedRole =
      String(body.role || "viewer")
        .trim()
        .toLowerCase();

    const message =
      String(body.message || "").trim();

    if (!name || !email) {
      return res.status(400).json({
        error: "Name and email are required"
      });
    }

    const allowedRoles = [
      "viewer",
      "analyst",
      "manager"
    ];

    const role =
      allowedRoles.includes(requestedRole)
        ? requestedRole
        : "viewer";

    const sql =
      neon(process.env.DATABASE_URL);

    /*
     * Access requests are separate from approved
     * authentication accounts.
     */
    await sql`
      CREATE TABLE IF NOT EXISTS auth_access_requests (
        id BIGSERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        requested_role TEXT NOT NULL DEFAULT 'viewer',
        message TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMPTZ,
        reviewed_by BIGINT
      )
    `;

    const result = await sql`
      INSERT INTO auth_access_requests
        (
          name,
          email,
          requested_role,
          message,
          status
        )
      VALUES
        (
          ${name},
          ${email},
          ${role},
          ${message},
          'PENDING'
        )
      RETURNING
        id,
        name,
        email,
        requested_role,
        status,
        created_at
    `;

    return res.status(201).json({
      success: true,
      request: result[0]
    });

  } catch (error) {

    console.error(
      "Pharmacy V13 access request error:",
      error
    );

    return res.status(500).json({
      error: "Unable to submit access request"
    });
  }
};
