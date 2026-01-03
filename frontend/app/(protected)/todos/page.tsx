// Task T025: Todos list page with full CRUD operations
// Displays all todos with ability to filter, create, edit, and delete
// Protected route - only accessible to authenticated users

"use client"

import { TasksContainer } from "@/components/todos/TasksContainer"

export default function TodosPage() {
  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
      <TasksContainer showCreateForm={true} />
    </div>
  )
}
