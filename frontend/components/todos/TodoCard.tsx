// Task T-228: Todo card component with priority badge and responsive design
// Displays individual todo items with priority indicators and status
// Responsive design: Mobile (320px) to Desktop (1920px)

interface Todo {
  id: string
  title: string
  description?: string
  priority: "High" | "Medium" | "Low"
  status: "pending" | "completed"
  dueDate?: string
}

interface TodoCardProps {
  todo: Todo
  onEdit?: (todo: Todo) => void
  onDelete?: (id: string) => void
}

export function TodoCard({ todo, onEdit, onDelete }: TodoCardProps) {
  // Task T-228: Priority color mapping
  const priorityColors: Record<string, { bg: string; text: string; border: string }> = {
    High: {
      bg: "bg-red-50 dark:bg-red-950",
      text: "text-red-700 dark:text-red-300",
      border: "border-red-200 dark:border-red-800",
    },
    Medium: {
      bg: "bg-yellow-50 dark:bg-yellow-950",
      text: "text-yellow-700 dark:text-yellow-300",
      border: "border-yellow-200 dark:border-yellow-800",
    },
    Low: {
      bg: "bg-green-50 dark:bg-green-950",
      text: "text-green-700 dark:text-green-300",
      border: "border-green-200 dark:border-green-800",
    },
  }

  const statusColors = {
    pending:
      "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200",
    completed:
      "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200",
  }

  const colors = priorityColors[todo.priority] || priorityColors.Medium

  // Task T-228: Format due date for display
  const formattedDueDate = todo.dueDate
    ? new Date(todo.dueDate).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null

  return (
    <div
      className={`
        border rounded-lg p-4 mb-4 transition-all
        hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600
        bg-white dark:bg-gray-800
        border-gray-200 dark:border-gray-700
        ${colors.border}
      `}
    >
      {/* Header: Title and Priority Badge */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          {/* Task T-228: Task title with strikethrough for completed todos */}
          <h3
            className={`
              text-lg font-semibold break-words
              ${
                todo.status === "completed"
                  ? "line-through text-gray-500 dark:text-gray-400"
                  : "text-gray-900 dark:text-white"
              }
            `}
          >
            {todo.title}
          </h3>

          {/* Task T-228: Task description (optional) */}
          {todo.description && (
            <p
              className={`
                text-sm mt-2 break-words
                ${
                  todo.status === "completed"
                    ? "text-gray-400 dark:text-gray-500"
                    : "text-gray-600 dark:text-gray-400"
                }
              `}
            >
              {todo.description}
            </p>
          )}
        </div>

        {/* Task T-228: Priority Badge - Responsive and color-coded */}
        <div
          className={`
            px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap
            ${colors.bg} ${colors.text}
            flex-shrink-0
          `}
        >
          {todo.priority}
        </div>
      </div>

      {/* Meta Information: Status, Due Date */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-4">
        {/* Task T-228: Status badge */}
        <span
          className={`
            px-3 py-1 rounded-full text-sm font-medium w-fit
            ${statusColors[todo.status]}
          `}
        >
          {todo.status === "completed" ? "✓ Completed" : "Pending"}
        </span>

        {/* Task T-228: Due date display (responsive) */}
        {formattedDueDate && (
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Due: {formattedDueDate}
          </span>
        )}
      </div>

      {/* Task T-228: Action buttons - Responsive layout */}
      {(onEdit || onDelete) && (
        <div className="flex flex-col sm:flex-row gap-2 pt-3 border-t border-gray-200 dark:border-gray-700">
          {onEdit && (
            <button
              onClick={() => onEdit(todo)}
              className="
                flex-1 sm:flex-none px-4 py-2 text-sm font-medium
                bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600
                text-white rounded-md transition-colors
              "
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(todo.id)}
              className="
                flex-1 sm:flex-none px-4 py-2 text-sm font-medium
                bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600
                text-white rounded-md transition-colors
              "
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default TodoCard
