// Task T-248: Protected root page - redirect to todos dashboard
// Ensures authenticated users landing on /dashboard are redirected to the todos list

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function ProtectedRootPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to todos dashboard
    router.push("/todos")
  }, [router])

  return null
}
