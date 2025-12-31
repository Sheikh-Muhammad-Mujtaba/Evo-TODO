// Task T-249: Create Todo component with form and validation
// User-friendly form to create new todos with optional description, due date, and priority

"use client"

import { useState } from "react"
import { TodoPriority } from "@/lib/hooks/useTodos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Loader2, X } from "lucide-react"

interface CreateTodoProps {
  onAdd: (data: {
    title: string
    description?: string
    dueDate?: string
    priority: TodoPriority
  }) => Promise<void>
  isLoading?: boolean
}

export function CreateTodo({ onAdd, isLoading = false }: CreateTodoProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [dueDate, setDueDate] = useState("")
  const [priority, setPriority] = useState<TodoPriority>("medium")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!title.trim()) {
      setError("Title is required")
      return
    }

    setIsSubmitting(true)
    try {
      await onAdd({
        title: title.trim(),
        description: description.trim() || undefined,
        dueDate: dueDate ? `${dueDate}T00:00:00Z` : undefined,
        priority,
      })

      // Reset form
      setTitle("")
      setDescription("")
      setDueDate("")
      setPriority("medium")
      setIsOpen(false)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create todo"
      setError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setTitle("")
    setDescription("")
    setDueDate("")
    setPriority("medium")
    setError("")
    setIsOpen(false)
  }

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        disabled={isLoading}
        className="flex items-center gap-2 w-full sm:w-auto"
        size="lg"
      >
        <Plus className="h-5 w-5" />
        Add New Task
      </Button>
    )
  }

  return (
    <div className="p-6 rounded-lg bg-gradient-to-br from-blue-50 to-blue-50/50 dark:from-blue-950/20 dark:to-blue-950/10 border border-blue-200 dark:border-blue-900 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Create New Task
        </h3>
        <button
          onClick={handleCancel}
          disabled={isSubmitting}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title field */}
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
          >
            Task Title *
          </label>
          <Input
            id="title"
            type="text"
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isSubmitting}
            autoFocus
            className="text-base"
          />
        </div>

        {/* Description field */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
          >
            Description (Optional)
          </label>
          <textarea
            id="description"
            placeholder="Add more details about this task..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isSubmitting}
            className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={3}
          />
        </div>

        {/* Priority and Due Date */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="priority"
              className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
            >
              Priority
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as TodoPriority)}
              disabled={isSubmitting}
              className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="dueDate"
              className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
            >
              Due Date (Optional)
            </label>
            <Input
              id="dueDate"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 rounded-md bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900">
            <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Form actions */}
        <div className="flex gap-2">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center gap-2 flex-1 sm:flex-none"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                Create Task
              </>
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
