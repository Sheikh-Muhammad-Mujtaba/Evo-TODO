"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * Dashboard Home Page
 * Redirects to todos page to show main task management interface
 * Provides better UX than showing a placeholder
 */
export default function DashboardPage() {
  const router = useRouter()

  useEffect(() => {
    router.push("/dashboard/todos")
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-blue-400 border-t-transparent"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading tasks...</p>
      </div>
    </div>
  )
}