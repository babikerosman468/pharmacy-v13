const {
  neon
} = require("@neondatabase/serverless");

const {
  getUser,
  hashPassword
} = require("../../lib/auth");

module.exports = async function handler(req, res) {

  try {

    const user = getUser(req);

    if (!user) {
      return res.status(401).json({
        error: "Authentication required"
      });
    }

    if (user.role !== "administrator") {
      return res.status(403).json({
        error: "Administrator access required"
      });
    }

    const sql =
      neon(process.env.DATABASE_URL);

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

    if (req.method === "GET") {

      const rows = await sql`
        SELECT
          id,
          name,
          email,
          requested_role,
          message,
          status,
          created_at,
          reviewed_at,
          reviewed_by
        FROM auth_access_requests
        ORDER BY created_at DESC
      `;

      return res.status(200).json({
        requests: rows
      });
    }

    if (req.method !== "POST") {

      res.setHeader(
        "Allow",
        "GET, POST"
      );

      return res.status(405).json({
        error: "Method not allowed"
      });
    }

    const body = req.body || {};

    const requestId =
      Number(body.requestId);

    const action =
      String(body.action || "")
        .trim()
        .toUpperCase();

    if (!Number.isInteger(requestId)) {
      return res.status(400).json({
        error: "Valid requestId is required"
      });
    }

    if (!["APPROVE", "REJECT"].includes(action)) {
      return res.status(400).json({
        error: "Action must be APPROVE or REJECT"
      });
    }

    const found = await sql`
      SELECT
        id,
        name,
        email,
        requested_role,
        status
      FROM auth_access_requests
      WHERE id = ${requestId}
      LIMIT 1
    `;

    if (!found.length) {
      return res.status(404).json({
        error: "Access request not found"
      });
    }

    const request = found[0];

    if (request.status !== "PENDING") {
      return res.status(409).json({
        error: "Access request has already been processed",
        status: request.status
      });
    }

    if (action === "REJECT") {

      await sql`
        UPDATE auth_access_requests
        SET
          status = 'REJECTED',
          reviewed_at = CURRENT_TIMESTAMP,
          reviewed_by = ${user.sub}
        WHERE id = ${requestId}
      `;

      return res.status(200).json({
        success: true,
        status: "REJECTED"
      });
    }

    /*
     * Approval requires the administrator to provide
     * the username and initial password.
     */
    const username =
      String(body.username || "")
        .trim()
        .toLowerCase();

    const password =
      String(body.password || "");

    if (!username || !password) {
      return res.status(400).json({
        error:
          "Approval requires username and password"
      });
    }

    if (password.length < 8) {
      return res.status(400).json({
        error:
          "Password must contain at least 8 characters"
      });
    }

    const existing = await sql`
      SELECT id
      FROM auth_users
      WHERE username = ${username}
      LIMIT 1
    `;

    if (existing.length) {
      return res.status(409).json({
        error: "Username already exists"
      });
    }

    const passwordHash =
      hashPassword(password);

    const created = await sql`
      INSERT INTO auth_users
        (
          username,
          password_hash,
          role,
          active,
          created_at,
          updated_at
        )
      VALUES
        (
          ${username},
          ${passwordHash},
          ${request.requested_role},
          true,
          CURRENT_TIMESTAMP,
          CURRENT_TIMESTAMP
        )
      RETURNING
        id,
        username,
        role,
        active
    `;

    await sql`
      UPDATE auth_access_requests
      SET
        status = 'APPROVED',
        reviewed_at = CURRENT_TIMESTAMP,
        reviewed_by = ${user.sub}
      WHERE id = ${requestId}
    `;

    return res.status(200).json({
      success: true,
      status: "APPROVED",
      user: created[0]
    });

  } catch (error) {

    console.error(
      "Pharmacy V13 request-management error:",
      error
    );

    return res.status(500).json({
      error: "Unable to process access request",
      detail: String(error && error.message || error)
    });
  }
};
