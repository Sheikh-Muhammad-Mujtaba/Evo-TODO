// Utility functions for the frontend
// clsx and twMerge for class name handling

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Log all cookies and session information for debugging
 * Useful for tracking authentication state
 */
export function logAuthCookies(context: string = "Auth") {
  if (typeof document === "undefined") {
    console.log(`[${context}] Running in server environment - cookies not accessible`);
    return;
  }

  console.log(`[${context}] ==================== COOKIES & SESSION ====================`);

  // Log all cookies
  const cookies = document.cookie.split(";").filter((c) => c.trim());
  console.log(`[${context}] Total cookies: ${cookies.length}`);

  cookies.forEach((cookie) => {
    const [key, value] = cookie.trim().split("=");
    const isSensitive = key.toLowerCase().includes("auth") ||
                       key.toLowerCase().includes("session") ||
                       key.toLowerCase().includes("token");

    if (isSensitive) {
      const displayValue = value ? value.substring(0, 20) + "..." : "empty";
      console.log(`[${context}] Cookie: ${key} = ${displayValue} (sensitive)`);
    } else {
      console.log(`[${context}] Cookie: ${key} = ${value}`);
    }
  });

  // Log localStorage authentication data
  console.log(`[${context}] LocalStorage entries:`);
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && (key.toLowerCase().includes("auth") || key.toLowerCase().includes("session"))) {
      const value = localStorage.getItem(key);
      const displayValue = value ? value.substring(0, 30) + "..." : "empty";
      console.log(`[${context}] localStorage: ${key} = ${displayValue}`);
    }
  }

  console.log(`[${context}] ===========================================================`);
}

/**
 * Format a date for display
 * Shows "Today", "Yesterday", "Tomorrow", or the date in format "MMM D, YYYY"
 */
export function formatDate(date: Date): string {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  const compareDate = new Date(date)
  compareDate.setHours(0, 0, 0, 0)

  if (compareDate.getTime() === today.getTime()) {
    return "Today"
  }
  if (compareDate.getTime() === yesterday.getTime()) {
    return "Yesterday"
  }
  if (compareDate.getTime() === tomorrow.getTime()) {
    return "Tomorrow"
  }

  const formatter = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: compareDate.getFullYear() === today.getFullYear() ? undefined : "numeric",
  })

  return formatter.format(date)
}
