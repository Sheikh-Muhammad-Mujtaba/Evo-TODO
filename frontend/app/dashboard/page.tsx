import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <section>
          <h1 className="text-3xl font-bold">Welcome to Evo-TODO</h1>
          <p className="mt-2 text-gray-600">Manage your tasks efficiently</p>
        </section>
        <section>
          <h2 className="text-2xl font-semibold mb-4">Your Tasks</h2>
          <div className="text-center py-12">
            <p className="text-gray-500">Task list loading...</p>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}