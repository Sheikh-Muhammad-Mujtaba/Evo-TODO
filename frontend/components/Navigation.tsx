// Task T-253: Navigation component for protected routes
// Displays user email, theme toggle, and logout button
// Appears at the top of protected pages

"use client"

import { useRouter } from "next/navigation"
import { useSession } from "@/lib/auth-client"
import { useTheme } from "@/lib/hooks/useTheme"
import { Button } from "@/components/ui/button"
import { signOut } from "@/lib/auth"
import { LogOut, Sun, Moon } from "lucide-react"
import { useState } from "react"

export function Navigation() {
  const router = useRouter()
  const { data: session } = useSession()
  const { theme, toggleTheme } = useTheme()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await signOut()
      router.push("/login")
    } catch (error) {
      console.error("Logout failed:", error)
      setIsLoggingOut(false)
    }
  }

  return (
    <nav className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo/Title */}
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            Evo-TODO
          </h1>
        </div>

        {/* Right side - User info and actions */}
        <div className="flex items-center gap-4">
          {/* User email display */}
          {session?.user?.email && (
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {session.user.email}
            </span>
          )}

          {/* Theme toggle button */}
          <Button
            onClick={toggleTheme}
            variant="ghost"
            size="sm"
            className="p-2"
            title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          >
            {theme === "light" ? (
              <Moon className="h-4 w-4" />
            ) : (
              <Sun className="h-4 w-4" />
            )}
          </Button>

          {/* Logout button */}
          <Button
            onClick={handleLogout}
            disabled={isLoggingOut}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            {isLoggingOut ? "Logging out..." : "Logout"}
          </Button>
        </div>
      </div>
    </nav>
  )
}
