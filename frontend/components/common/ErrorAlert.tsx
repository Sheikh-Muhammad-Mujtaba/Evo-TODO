// Task T-237: Error alert component for displaying error messages
// Built with Shadcn/UI Alert primitive
// Used across app for consistent error display

"use client"

import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

export interface ErrorAlertProps {
  title?: string
  message: string
  onDismiss?: () => void
  variant?: "default" | "destructive"
}

/**
 * Task T-237: ErrorAlert component
 * - Displays error messages with icon
 * - Optional title and dismiss button
 * - Dark mode support via Shadcn/UI
 * - Accessible alert role
 */
export function ErrorAlert({
  title,
  message,
  onDismiss,
  variant = "destructive",
}: ErrorAlertProps) {
  return (
    <Alert variant={variant} className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
      <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
      <div className="ml-3 flex-1">
        {title && (
          <h4 className="text-sm font-semibold text-red-800 dark:text-red-200">
            {title}
          </h4>
        )}
        <AlertDescription className="text-sm text-red-700 dark:text-red-300">
          {message}
        </AlertDescription>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="ml-auto flex-shrink-0 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
          aria-label="Dismiss error"
        >
          ✕
        </button>
      )}
    </Alert>
  )
}
