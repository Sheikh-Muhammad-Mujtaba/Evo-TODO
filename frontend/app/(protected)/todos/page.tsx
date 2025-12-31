// Task T-247: Todo list page with filtering and task management
// Displays all todos with ability to filter by status and create new todos
// Protected route - only accessible to authenticated users

"use client"

import { useState } from "react"
import { useTodos, type TodoFilter } from "@/lib/hooks/useTodos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, AlertCircle, Loader2 } from "lucide-react"

export default function TodosPage() {
  const { filteredTodos, isLoading, error, currentFilter, setFilter, createTodo } = useTodos()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newTodoTitle, setNewTodoTitle] = useState("")
  const [isCreating, setIsCreating] = useState(false)
  const [createError, setCreateError] = useState("")

  // Task T-247: Handle creating new todo
  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreateError("")

    if (!newTodoTitle.trim()) {
      setCreateError("Title is required")
      return
    }

    setIsCreating(true)
    try {
      await createTodo({
        title: newTodoTitle,
        description: "",
        status: "pending",
        priority: "medium",
      })
      setNewTodoTitle("")
      setShowCreateForm(false)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create todo"
      setCreateError(errorMessage)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          My Tasks
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Stay organized and track your progress
        </p>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800 dark:text-red-200">
              Failed to load todos
            </p>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
              {error}
            </p>
          </div>
        </div>
      )}

      {/* Create todo section */}
      {showCreateForm ? (
        <div className="mb-6 p-6 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          <form onSubmit={handleCreateTodo} className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="What needs to be done?"
                value={newTodoTitle}
                onChange={(e) => setNewTodoTitle(e.target.value)}
                disabled={isCreating}
                autoFocus
                className="text-lg"
              />
            </div>
            {createError && (
              <p className="text-sm text-red-600 dark:text-red-400">
                {createError}
              </p>
            )}
            <div className="flex gap-2">
              <Button
                type="submit"
                disabled={isCreating}
                className="flex items-center gap-2"
              >
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Add Task
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false)
                  setNewTodoTitle("")
                  setCreateError("")
                }}
                disabled={isCreating}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      ) : (
        <Button
          onClick={() => setShowCreateForm(true)}
          className="mb-6 flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          New Task
        </Button>
      )}

      {/* Filter tabs */}
      <div className="mb-6 flex gap-2 border-b border-gray-200 dark:border-gray-800">
        {(["all", "pending", "completed"] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => setFilter(filter as TodoFilter)}
            className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 -mb-px ${
              currentFilter === filter
                ? "text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400"
                : "text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-100"
            }`}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
        </div>
      ) : filteredTodos.length === 0 ? (
        <div className="py-12 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            {currentFilter === "all"
              ? "No tasks yet. Create one to get started!"
              : `No ${currentFilter} tasks.`}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTodos.map((todo) => (
            <div
              key={todo.id}
              className="p-4 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 hover:shadow-md dark:hover:shadow-gray-800 transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 dark:text-white break-words">
                    {todo.title}
                  </h3>
                  {todo.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {todo.description}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-xs">
                    <span
                      className={`px-2 py-1 rounded-full ${
                        todo.status === "completed"
                          ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300"
                          : "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300"
                      }`}
                    >
                      {todo.status.charAt(0).toUpperCase() + todo.status.slice(1)}
                    </span>
                    <span
                      className={`px-2 py-1 rounded-full ${
                        todo.priority === "high"
                          ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300"
                          : todo.priority === "medium"
                          ? "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300"
                          : "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                      }`}
                    >
                      {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
