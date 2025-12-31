// Task T-244: Theme toggle button component
// Allows users to switch between light and dark mode
// Persists preference to localStorage via next-themes

"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "@/lib/hooks/useTheme"

interface ThemeToggleProps {
  size?: "sm" | "md"
}

/**
 * Task T-244: ThemeToggle component
 * - Button to toggle between light/dark mode
 * - Shows sun icon (light mode) or moon icon (dark mode)
 * - Persists user preference to localStorage
 * - Supports system preference detection
 * - Dark mode support
 */
export function ThemeToggle({ size = "md" }: ThemeToggleProps) {
  const { isDark, toggleTheme, mounted } = useTheme()

  if (!mounted) {
    // Return placeholder during hydration
    return (
      <div
        className={`rounded-md bg-gray-100 dark:bg-gray-800 ${
          size === "sm" ? "h-8 w-8" : "h-10 w-10"
        }`}
      />
    )
  }

  const sizeClasses = {
    sm: "h-8 w-8 p-1.5",
    md: "h-10 w-10 p-2",
  }

  return (
    <button
      onClick={toggleTheme}
      className={`inline-flex items-center justify-center rounded-md text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 ${sizeClasses[size]}`}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </button>
  )
}
