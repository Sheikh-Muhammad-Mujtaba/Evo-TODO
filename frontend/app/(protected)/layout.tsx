// Task T-242: Protected routes layout
// Enforces authentication for all routes under (protected) group
// Server-side session validation with middleware
// Client-side fallback for browser protection

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useSession } from '@/lib/auth-client'

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { data: session, isPending } = useSession()

  useEffect(() => {
    // Client-side auth check (middleware handles server-side)
    if (!isPending && !session) {
      router.push('/login')
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

  // Prevent rendering protected content for unauthenticated users
  if (!session) {
    return null
  }

  return <>{children}</>
}
