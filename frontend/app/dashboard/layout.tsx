// Task T009: Protected dashboard layout with session validation
// Validates session before rendering dashboard and children
// Prevents unauthenticated content flash using server component
// Uses Better Auth's auth.api.getSession() for full validation

import { auth } from '@/lib/auth'
import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import React from 'react'

/**
 * Task T009: Dashboard layout - Protected route group
 *
 * This layout:
 * 1. Validates session using auth.api.getSession() (server-side, Node.js runtime)
 * 2. Redirects unauthenticated users to /login
 * 3. Prevents FOUC (Flash of Unstyled Content) by validating before rendering
 * 4. Wraps all dashboard routes with authenticated session requirement
 *
 * Session validation flow:
 * - Middleware (edge): checks for session cookie (optimistic redirect)
 * - Layout (server): validates session with database (security check)
 * - If invalid: clear cookie, redirect to login
 */
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Task T009: Get and validate session server-side
  // This ensures full validation happens before rendering any protected content
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    // No valid session found - redirect to login
    if (!session) {
      console.warn('[Dashboard Layout] No valid session found, redirecting to login')
      redirect('/login')
    }

    // Session is valid - user is authenticated
    // Safe to render dashboard and children
    console.log('[Dashboard Layout] ✓ Session validated:', {
      userId: session.user.id,
      userEmail: session.user.email,
      sessionExpiresAt: session.session.expiresAt,
    })
  } catch (error) {
    // Session validation error - treat as unauthenticated
    console.error('[Dashboard Layout] Session validation error:', error)
    redirect('/login')
  }

  // Session is valid - render children
  return <>{children}</>
}
