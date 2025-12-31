/**
 * Task T-237: Better Auth client-side configuration
 *
 * This creates the client instance that communicates with the server-side auth
 * at /api/auth (created in app/api/auth/[...all]/route.ts)
 *
 * Reference: better-auth/react createAuthClient
 * Reference: Better Auth Next.js integration documentation
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

console.log("[Auth Client] ==================== INITIALIZATION ====================");
console.log("[Auth Client] Initializing Better Auth client...");
const authBaseUrl = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000";
console.log("[Auth Client] Base URL:", authBaseUrl);
console.log("[Auth Client] Plugins: jwtClient() - JWT token retrieval enabled");

/**
 * Initialize Better Auth client
 * Connects to the server-side auth instance via /api/auth routes
 */
export const authClient = createAuthClient({
  baseURL: authBaseUrl,
  plugins: [
    jwtClient(), // Enable JWT token support for API requests
  ],
  // Client automatically connects to /api/auth routes created by the handler
});

console.log("[Auth Client] ✓ Client initialized successfully");
console.log("[Auth Client] Available endpoints:");
console.log("[Auth Client]   - /api/auth/sign-up (email + password signup)");
console.log("[Auth Client]   - /api/auth/sign-in (email + password signin)");
console.log("[Auth Client]   - /api/auth/sign-out (logout)");
console.log("[Auth Client]   - /api/auth/session (get current session)");
console.log("[Auth Client]   - /api/auth/token (get JWT token via jwtClient plugin)");
console.log("[Auth Client] ===========================================================");

/**
 * Export useSession hook for components
 * Returns reactive session state
 */
export const useSession = () => authClient.useSession();

/**
 * Export other client methods for direct use
 */
export const signIn = authClient.signIn;
export const signUp = authClient.signUp;
export const signOut = authClient.signOut;
