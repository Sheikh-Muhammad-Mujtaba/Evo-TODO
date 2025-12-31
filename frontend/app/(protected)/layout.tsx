// Task T-242 + T-250 + T-253: Protected routes layout
// Enforces authentication for all routes under (protected) group
// Redirects unauthenticated users to /login
// Includes Navigation component for all protected pages

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "@/lib/auth-client"
import { Navigation } from "@/components/Navigation"
import { logAuthCookies } from "@/lib/utils"

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { data: session, isPending } = useSession()

  console.log("[Protected Layout] Checking authentication...", {
    isPending,
    hasSession: !!session,
    userId: session?.user?.id,
  });

  useEffect(() => {
    console.log("[Protected Layout] useEffect triggered:", {
      isPending,
      hasSession: !!session,
    });

    // Task T-250: Redirect unauthenticated users to login
    if (!isPending && !session) {
      console.warn("[Protected Layout] ✗ No session - redirecting to /login");
      logAuthCookies("Protected-NoSession");
      router.push("/login")
    } else if (!isPending && session) {
      console.log("[Protected Layout] ✓ Session authenticated:", {
        userId: session.user?.id,
        userEmail: session.user?.email,
      });
      logAuthCookies("Protected-Authenticated");
    }
  }, [session, isPending, router])

  // Show loading spinner while checking authentication
  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-50"></div>
      </div>
    )
  }

  // Task T-250: Prevent rendering protected content for unauthenticated users
  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      {/* Task T-253: Navigation component for user info and logout */}
      <Navigation />

      <main className="container mx-auto py-6">
        {children}
      </main>
    </div>
  )
}
