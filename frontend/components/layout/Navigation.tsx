// Task T-243: Navigation component
// Header with user menu (profile, logout) for authenticated users
// Responsive design with dark mode support

"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/hooks/useAuth"
import { useTheme } from "@/lib/hooks/useTheme"
import { LogOut, Menu, X, User } from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"

/**
 * Task T-243: Navigation component
 * - Displays app header with logo/title
 * - Shows user email and logout button
 * - Includes theme toggle
 * - Mobile-responsive hamburger menu
 * - Dark mode support
 */
export function Navigation() {
  const router = useRouter()
  const { user, signOut } = useAuth()
  const { mounted } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push("/login")
    } catch (error) {
      console.error("Sign out failed:", error)
    }
  }

  return (
    <nav className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo / Title */}
          <Link
            href="/todos"
            className="flex items-center gap-2 font-bold text-lg text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400"
          >
            <span>Evo-TODO</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden items-center gap-4 sm:flex">
            {mounted && <ThemeToggle />}

            <div className="border-l border-gray-200 pl-4 dark:border-gray-800">
              <div className="flex items-center gap-3">
                <div className="flex flex-col items-end">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.name || user?.email}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.email}
                  </p>
                </div>

                <button
                  onClick={() => router.push("/profile")}
                  className="inline-flex items-center justify-center rounded-full bg-gray-100 p-2 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  title="Profile"
                  aria-label="View profile"
                >
                  <User className="h-4 w-4" />
                </button>

                <button
                  onClick={handleSignOut}
                  className="inline-flex items-center gap-2 rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
                  title="Sign out"
                  aria-label="Sign out"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 sm:hidden">
            {mounted && <ThemeToggle size="sm" />}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-md p-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="border-t border-gray-200 py-4 dark:border-gray-800">
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1 px-2">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.name || user?.email}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.email}
                </p>
              </div>

              <button
                onClick={() => {
                  router.push("/profile")
                  setMobileMenuOpen(false)
                }}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </button>

              <button
                onClick={() => {
                  handleSignOut()
                  setMobileMenuOpen(false)
                }}
                className="flex items-center gap-2 rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
