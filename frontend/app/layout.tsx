import type { Metadata } from 'next'
import './globals.css'

// Task T-201: Root layout with AuthProvider wrapper (will add in T-219)

export const metadata: Metadata = {
  title: 'Evo-TODO - Task Management',
  description: 'Phase II: Full-stack todo application with JWT authentication',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* Task T-219: Wrap with AuthProvider */}
        {children}
      </body>
    </html>
  )
}
