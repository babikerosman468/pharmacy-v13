const crypto = require("crypto");
const { neon } = require("@neondatabase/serverless");

const JWT_SECRET = process.env.PHARMACY_JWT_SECRET;

if (!JWT_SECRET) {
  throw new Error("PHARMACY_JWT_SECRET is not configured");
}

function base64url(value) {
  return Buffer
    .from(value)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function base64urlBuffer(buffer) {
  return buffer
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function sign(input) {
  return base64urlBuffer(
    crypto
      .createHmac("sha256", JWT_SECRET)
      .update(input)
      .digest()
  );
}

function createToken(user) {
  const header = base64url(
    JSON.stringify({
      alg: "HS256",
      typ: "JWT"
    })
  );

  const now = Math.floor(Date.now() / 1000);

  const payload = base64url(
    JSON.stringify({
      sub: user.id,
      username: user.username,
      role: user.role,
      iat: now,
      exp: now + 8 * 60 * 60
    })
  );

  const unsigned = `${header}.${payload}`;
  const signature = sign(unsigned);

  return `${unsigned}.${signature}`;
}

function verifyToken(token) {
  if (!token || typeof token !== "string") {
    return null;
  }

  const parts = token.split(".");

  if (parts.length !== 3) {
    return null;
  }

  const [header, payload, signature] = parts;

  const expected = sign(`${header}.${payload}`);

  const a = Buffer.from(signature);
  const b = Buffer.from(expected);

  if (
    a.length !== b.length ||
    !crypto.timingSafeEqual(a, b)
  ) {
    return null;
  }

  try {
    const decoded = JSON.parse(
      Buffer.from(payload, "base64url").toString("utf8")
    );

    if (!decoded.exp || decoded.exp < Math.floor(Date.now() / 1000)) {
      return null;
    }

    return decoded;
  } catch (_) {
    return null;
  }
}

function getToken(req) {
  const header =
    req.headers.authorization ||
    req.headers.Authorization ||
    "";

  if (!header.startsWith("Bearer ")) {
    return null;
  }

  return header.slice(7).trim();
}

function getUser(req) {
  return verifyToken(getToken(req));
}

function requireAuth(req, res, roles) {
  const user = getUser(req);

  if (!user) {
    res.writeHead(401, {
      "Content-Type": "application/json"
    });
    res.end(JSON.stringify({
      error: "Authentication required"
    }));

    return null;
  }

  if (
    Array.isArray(roles) &&
    roles.length &&
    !roles.includes(user.role)
  ) {
    res.status(403).json({
      error: "Insufficient permissions",
      role: user.role
    });

    return null;
  }

  return user;
}


const ROLE_PERMISSIONS = {
  administrator: ["*"],

  manager: [
    "dashboard.read",
    "medicines.read",
    "medicines.write",
    "inventory.read",
    "inventory.write",
    "sales.read",
    "sales.write",
    "suppliers.read",
    "suppliers.write",
    "purchases.read",
    "purchases.write",
    "cash.read",
    "alerts.read",
    "reports.read",
    "reports.generate",
    "analytics.read"
  ],

  analyst: [
    "dashboard.read",
    "medicines.read",
    "inventory.read",
    "sales.read",
    "suppliers.read",
    "purchases.read",
    "cash.read",
    "alerts.read",
    "reports.read",
    "reports.generate",
    "analytics.read",
    "research.read"
  ],

  viewer: [
    "dashboard.read",
    "medicines.read",
    "inventory.read",
    "sales.read",
    "alerts.read",
    "reports.read"
  ]
};

function hasPermission(role, permission) {
  const permissions = ROLE_PERMISSIONS[role] || [];

  return (
    permissions.includes("*") ||
    permissions.includes(permission)
  );
}

function requirePermission(req, res, permission) {
  const user = getUser(req);

  if (!user) {
    res.writeHead(401, {
      "Content-Type": "application/json"
    });

    res.end(JSON.stringify({
      error: "Authentication required"
    }));

    return null;
  }

  if (!hasPermission(user.role, permission)) {
    res.writeHead(403, {
      "Content-Type": "application/json"
    });

    res.end(JSON.stringify({
      error: "Insufficient permissions",
      role: user.role,
      required: permission
    }));

    return null;
  }

  return user;
}

function hashPassword(password) {
  const salt = crypto.randomBytes(16);

  const hash = crypto.scryptSync(
    password,
    salt,
    64,
    {
      N: 16384,
      r: 8,
      p: 1
    }
  );

  return [
    "scrypt",
    "16384",
    "8",
    "1",
    base64urlBuffer(salt),
    base64urlBuffer(hash)
  ].join("$");
}

function verifyPassword(password, stored) {
  try {
    const parts = String(stored).split("$");

    if (parts.length !== 6 || parts[0] !== "scrypt") {
      return false;
    }

    const N = Number(parts[1]);
    const r = Number(parts[2]);
    const p = Number(parts[3]);

    const salt = Buffer.from(
      parts[4],
      "base64url"
    );

    const expected = Buffer.from(
      parts[5],
      "base64url"
    );

    const actual = crypto.scryptSync(
      password,
      salt,
      expected.length,
      {
        N,
        r,
        p
      }
    );

    return (
      actual.length === expected.length &&
      crypto.timingSafeEqual(actual, expected)
    );
  } catch (_) {
    return false;
  }
}

function getClientIP(req) {
  const forwarded =
    req.headers["x-forwarded-for"];

  if (forwarded) {
    return String(forwarded)
      .split(",")[0]
      .trim();
  }

  return (
    req.headers["x-real-ip"] ||
    req.socket?.remoteAddress ||
    null
  );
}

async function login(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");

    return res.status(405).json({
      error: "Method not allowed"
    });
  }

  const body = req.body || {};

  const username =
    String(body.username || "")
      .trim()
      .toLowerCase();

  const password =
    String(body.password || "");

  if (!username || !password) {
    return res.status(400).json({
      error: "Username and password are required"
    });
  }

  const sql = neon(process.env.DATABASE_URL);
  const ip = getClientIP(req);

  const recent = await sql`
    SELECT COUNT(*) AS attempts
    FROM auth_login_attempts
    WHERE username = ${username}
      AND successful = false
      AND attempted_at >= CURRENT_TIMESTAMP - INTERVAL '15 minutes'
  `;

  if (Number(recent[0].attempts) >= 10) {
    return res.status(429).json({
      error: "Too many failed login attempts. Try again later."
    });
  }

  const rows = await sql`
    SELECT
      id,
      username,
      password_hash,
      role,
      active
    FROM auth_users
    WHERE username = ${username}
    LIMIT 1
  `;

  const user = rows[0];

  const valid = Boolean(
    user &&
    user.active === true &&
    verifyPassword(
      password,
      user.password_hash
    )
  );

  await sql`
    INSERT INTO auth_login_attempts
      (username, ip_address, successful)
    VALUES
      (${username}, ${ip}, ${valid})
  `;

  if (!valid) {
    await sql`
      INSERT INTO auth_audit
        (username, action, endpoint, ip_address, details)
      VALUES
        (
          ${username},
          'LOGIN_FAILED',
          '/api/auth/login',
          ${ip},
          ${JSON.stringify({
            reason: "invalid_credentials"
          })}
        )
    `;

    return res.status(401).json({
      error: "Invalid username or password"
    });
  }

  await sql`
    UPDATE auth_users
    SET
      last_login_at = CURRENT_TIMESTAMP,
      updated_at = CURRENT_TIMESTAMP
    WHERE id = ${user.id}
  `;

  await sql`
    INSERT INTO auth_audit
      (user_id, username, action, endpoint, ip_address)
    VALUES
      (
        ${user.id},
        ${user.username},
        'LOGIN_SUCCESS',
        '/api/auth/login',
        ${ip}
      )
  `;

  const token = createToken(user);

  return res.status(200).json({
    token,
    user: {
      id: user.id,
      username: user.username,
      role: user.role
    },
    expiresIn: 8 * 60 * 60
  });
}

async function me(req, res) {
  const user = getUser(req);

  if (!user) {
    return res.status(401).json({
      error: "Authentication required"
    });
  }

  return res.status(200).json({
    authenticated: true,
    user: {
      id: user.sub,
      username: user.username,
      role: user.role
    }
  });
}

module.exports = {
  createToken,
  getUser,
  requireAuth,
  requirePermission,
  hasPermission,
  ROLE_PERMISSIONS,
  hashPassword,
  verifyPassword,
  login,
  me
};
