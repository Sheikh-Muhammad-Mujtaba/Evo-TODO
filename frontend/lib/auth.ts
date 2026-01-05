/**
 * Task T-237: Server-side Better Auth configuration
 *
 * This is the server-side auth instance that must be created first.
 * The client instance connects to the API route handlers created from this.
 */

import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Debug logging for database initialization
const databaseUrl = process.env.DATABASE_URL;
const authSecret = process.env.BETTER_AUTH_SECRET;
const baseUrl = process.env.NEXT_PUBLIC_AUTH_URL;

console.log("[Better Auth] ==================== INITIALIZATION ====================");
console.log("[Better Auth] Initializing auth instance...");
console.log("[Better Auth] Database URL:", databaseUrl ? "✓ Set" : "✗ Missing");
if (databaseUrl) {
  // Log connection details (hide password for security)
  const urlObj = new URL(databaseUrl);
  console.log(
    `[Better Auth] Database: ${urlObj.protocol}//${urlObj.hostname}:${urlObj.port}/${urlObj.pathname}`
  );
}
console.log("[Better Auth] Base URL:", baseUrl || "http://localhost:3000");
console.log("[Better Auth] Auth Secret:", authSecret ? "✓ Set" : "✗ Missing");
console.log("[Better Auth] Environment: Node.js server-side auth instance");

if (!databaseUrl) {
  console.error(
    "[Better Auth] ERROR: DATABASE_URL is not set! Add it to .env.local"
  );
  console.error("[Better Auth] Expected format: postgresql://user:pass@host:5432/db");
}

/**
 * Create the Better Auth server instance
 * This handles all authentication logic on the server
 */
console.log("[Better Auth] Creating auth instance...");

let authInstance: ReturnType<typeof betterAuth> | null = null;

try {
  console.log("[Better Auth] Creating database pool...");

  // Create a PostgreSQL connection pool
  const dbPool = new Pool({
    connectionString: databaseUrl || "",
  });

  // Test the connection
  dbPool.on("error", (err) => {
    console.error("[Better Auth] Database pool error:", err);
  });

  console.log("[Better Auth] Configuring auth instance with plugins...");
  console.log("[Better Auth] Plugins: nextCookies() + jwt()");
  console.log("[Better Auth] Session config: 7 days expiry, 1 day refresh age");

  authInstance = betterAuth({
    baseURL: baseUrl || "http://localhost:3000",
    database: dbPool,
    secret: authSecret || "your-secret-key",
    emailAndPassword: {
      enabled: true,
    },
    // Session configuration to prevent quick expiration
    session: {
      expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
      updateAge: 60 * 60 * 24, // Refresh session every 1 day when used
      // Disable session refresh to prevent automatic logout
      disableSessionRefresh: false,
      // Session freshness - how long before session is considered "stale"
      // Default is 1 day, but JWT plugin requires fresh session
      // Set to 7 days to match expiresIn so session is always fresh
      freshAge: 60 * 60 * 24 * 7, // 7 days - same as expiresIn
      // Enable cookie cache for better performance
      cookieCache: {
        enabled: true,
        maxAge: 60 * 60, // Cache for 1 hour
      },
    },
    plugins: [
      nextCookies(),
      jwt(), // Enable JWT token generation with JWKS endpoint for API requests
    ],
    logger: {
      disabled: false,
    },
    // Trust host for development
    trustHost: true,
  });
  console.log("[Better Auth] ✓ Auth instance created successfully with database pool");
  console.log("[Better Auth] JWT plugin enabled - tokens available at /api/auth/token");
  console.log("[Better Auth] JWKS endpoint available at /api/auth/jwks");
  console.log("[Better Auth] ===========================================================");
} catch (error) {
  console.error("[Better Auth] ✗ Failed to create auth instance:", error);
  if (error instanceof Error) {
    console.error("[Better Auth] Error details:", error.message);
    console.error("[Better Auth] Stack:", error.stack);
  }
  throw error;
}

export const auth = authInstance as ReturnType<typeof betterAuth>;

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.User;
