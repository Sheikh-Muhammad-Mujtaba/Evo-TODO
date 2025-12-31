// Task T-248: Todo item component with edit, delete, and status toggle
// Displays individual todo with actions and inline editing capability

"use client"

import { useState } from "react"
import { Todo, TodoPriority, TodoStatus } from "@/lib/hooks/useTodos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Trash2,
  Edit2,
  Check,
  X,
  Calendar,
  AlertCircle,
  Loader2,
} from "lucide-react"
import { formatDate } from "@/lib/utils"

interface TodoItemProps {
  todo: Todo
  onUpdate: (id: string, data: Partial<Todo>) => Promise<void>
  onDelete: (id: string) => Promise<void>
  onStatusChange: (id: string, status: TodoStatus) => Promise<void>
}

const priorityColors = {
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  medium:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
}

export function TodoItem({
  todo,
  onUpdate,
  onDelete,
  onStatusChange,
}: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(todo.title)
  const [editDescription, setEditDescription] = useState(todo.description || "")
  const [editDueDate, setEditDueDate] = useState(
    todo.dueDate ? todo.dueDate.split("T")[0] : ""
  )
  const [editPriority, setEditPriority] = useState<TodoPriority>(todo.priority)
  const [isUpdating, setIsUpdating] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isTogglingStatus, setIsTogglingStatus] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [updateError, setUpdateError] = useState("")

  const handleSaveEdit = async () => {
    setUpdateError("")

    if (!editTitle.trim()) {
      setUpdateError("Title is required")
      return
    }

    setIsUpdating(true)
    try {
      await onUpdate(todo.id, {
        title: editTitle,
        description: editDescription,
        dueDate: editDueDate ? `${editDueDate}T00:00:00Z` : undefined,
        priority: editPriority,
      })
      setIsEditing(false)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update todo"
      setUpdateError(errorMessage)
    } finally {
      setIsUpdating(false)
    }
  }

  const handleCancelEdit = () => {
    setEditTitle(todo.title)
    setEditDescription(todo.description || "")
    setEditDueDate(
      todo.dueDate ? todo.dueDate.split("T")[0] : ""
    )
    setEditPriority(todo.priority)
    setIsEditing(false)
    setUpdateError("")
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onDelete(todo.id)
      setShowDeleteConfirm(false)
    } catch (err) {
      console.error("Failed to delete todo:", err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleStatusToggle = async () => {
    setIsTogglingStatus(true)
    try {
      const newStatus: TodoStatus =
        todo.status === "completed" ? "pending" : "completed"
      await onStatusChange(todo.id, newStatus)
    } catch (err) {
      console.error("Failed to toggle status:", err)
    } finally {
      setIsTogglingStatus(false)
    }
  }

  if (isEditing) {
    return (
      <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Title
          </label>
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            placeholder="Todo title"
            disabled={isUpdating}
            className="mt-1"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Description (Optional)
          </label>
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            placeholder="Add a description"
            disabled={isUpdating}
            className="mt-1 w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
              Priority
            </label>
            <select
              value={editPriority}
              onChange={(e) =>
                setEditPriority(e.target.value as TodoPriority)
              }
              disabled={isUpdating}
              className="mt-1 w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
              Due Date
            </label>
            <Input
              type="date"
              value={editDueDate}
              onChange={(e) => setEditDueDate(e.target.value)}
              disabled={isUpdating}
              className="mt-1"
            />
          </div>
        </div>

        {updateError && (
          <div className="p-3 rounded-md bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900">
            <p className="text-sm text-red-800 dark:text-red-300">
              {updateError}
            </p>
          </div>
        )}

        <div className="flex gap-2">
          <Button
            onClick={handleSaveEdit}
            disabled={isUpdating}
            className="flex items-center gap-2"
          >
            {isUpdating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Check className="h-4 w-4" />
                Save
              </>
            )}
          </Button>
          <Button
            onClick={handleCancelEdit}
            variant="outline"
            disabled={isUpdating}
          >
            Cancel
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`p-4 rounded-lg border transition-all ${
        todo.status === "completed"
          ? "bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-800"
          : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700"
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Status checkbox */}
        <button
          onClick={handleStatusToggle}
          disabled={isTogglingStatus}
          className="flex-shrink-0 mt-1"
        >
          <div
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
              todo.status === "completed"
                ? "bg-green-500 border-green-500"
                : "border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500"
            }`}
          >
            {todo.status === "completed" && (
              <Check className="h-4 w-4 text-white" />
            )}
          </div>
        </button>

        {/* Todo content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium transition-all ${
              todo.status === "completed"
                ? "line-through text-gray-500 dark:text-gray-400"
                : "text-gray-900 dark:text-white"
            }`}
          >
            {todo.title}
          </h3>

          {todo.description && (
            <p
              className={`text-sm mt-1 ${
                todo.status === "completed"
                  ? "text-gray-400 dark:text-gray-500"
                  : "text-gray-600 dark:text-gray-400"
              }`}
            >
              {todo.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex flex-wrap items-center gap-3 mt-3">
            {/* Priority badge */}
            <span
              className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${priorityColors[todo.priority]}`}
            >
              {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
            </span>

            {/* Due date */}
            {todo.dueDate && (
              <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
                <Calendar className="h-3.5 w-3.5" />
                {formatDate(new Date(todo.dueDate))}
              </div>
            )}

            {/* Created date */}
            <div className="text-xs text-gray-500 dark:text-gray-500">
              Created {formatDate(new Date(todo.createdAt))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Button
            onClick={() => setIsEditing(true)}
            variant="ghost"
            size="sm"
            disabled={isTogglingStatus || isUpdating}
            title="Edit"
          >
            <Edit2 className="h-4 w-4" />
          </Button>

          {showDeleteConfirm ? (
            <>
              <Button
                onClick={handleDelete}
                variant="destructive"
                size="sm"
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Confirm"
                )}
              </Button>
              <Button
                onClick={() => setShowDeleteConfirm(false)}
                variant="outline"
                size="sm"
                disabled={isDeleting}
              >
                Cancel
              </Button>
            </>
          ) : (
            <Button
              onClick={() => setShowDeleteConfirm(true)}
              variant="ghost"
              size="sm"
              className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-950/20"
              disabled={isTogglingStatus || isUpdating}
              title="Delete"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Delete confirmation message */}
      {showDeleteConfirm && (
        <div className="mt-3 p-3 rounded-md bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 flex items-start gap-3">
          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-300">
            Are you sure you want to delete this task? This action cannot be undone.
          </p>
        </div>
      )}
    </div>
  )
}
