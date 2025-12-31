/**
 * Task T-237: Better Auth API route handler
 * 
 * This route mounts the Better Auth handler at /api/auth/[...all]
 * All authentication requests go through this handler
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

/**
 * Export GET and POST handlers for all auth routes
 * This creates the following endpoints:
 * - POST /api/auth/sign-up
 * - POST /api/auth/sign-in
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 * - etc.
 */
export const { GET, POST } = toNextJsHandler(auth.handler);
