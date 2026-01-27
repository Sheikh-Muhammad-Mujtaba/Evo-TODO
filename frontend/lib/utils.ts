import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Existing utils (logAuthCookies, formatDate)
export function logAuthCookies(context: string = "Auth") {
  if (typeof document === "undefined") {
    console.log(`[${context}] Server - cookies not accessible`);
    return;
  }
  console.log(`[${context}] Cookies:`);
  document.cookie.split(";").forEach(c => {
    const [key] = c.trim().split("=");
    const isSensitive = key.toLowerCase().includes("auth") || key.toLowerCase().includes("session");
    console.log(`${key} = ${isSensitive ? '[sensitive]' : c.trim().split("=")[1]}`);
  });
}

export function formatDate(date: Date): string {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const compareDate = new Date(date);
  compareDate.setHours(0, 0, 0, 0);
  if (compareDate.getTime() === today.getTime()) return "Today";
  const formatter = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" });
  return formatter.format(date);
}

// Shadcn cn() restored + existing (T304 UI fix)
