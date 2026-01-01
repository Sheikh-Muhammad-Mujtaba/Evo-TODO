// Task T-235: Custom useTodos hook for todo CRUD operations
// Provides state management for todo items with filtering, sorting, and API integration
// Handles all todo operations: fetch, create, update, delete, filter

"use client"

import { useEffect, useState } from "react"
import { apiGet, apiPost, apiPatch, apiDelete } from "../api"

export type TodoStatus = "pending" | "completed"
export type TodoPriority = "low" | "medium" | "high"

export interface Todo {
  id: string
  userId: string
  title: string
  description?: string
  status: TodoStatus
  priority: TodoPriority
  dueDate?: string
  createdAt: string
  updatedAt: string
}

export type TodoFilter = "all" | "pending" | "completed"
export type TodoSort = "title" | "priority" | "dueDate" | "createdAt"

export interface UseTodosReturn {
  // State
  todos: Todo[]
  filteredTodos: Todo[]
  isLoading: boolean
  error: string | null

  // Filter & Sort
  currentFilter: TodoFilter
  currentSort: TodoSort
  setFilter: (filter: TodoFilter) => void
  setSort: (sort: TodoSort) => void

  // CRUD Operations
  createTodo: (data: Omit<Todo, "id" | "userId" | "createdAt" | "updatedAt">) => Promise<Todo>
  updateTodo: (id: string, data: Partial<Todo>) => Promise<Todo>
  deleteTodo: (id: string) => Promise<void>
  refreshTodos: () => Promise<void>
}

/**
 * Task T-235: Custom useTodos hook
 * - Fetches todos from /api/todos endpoint
 * - Manages filtering by status (all/pending/completed)
 * - Supports sorting by multiple fields
 * - Provides create, update, delete methods
 * - Maintains loading and error states
 * 
 * FIX (2026-01-01): Handle backend response format
 * Backend returns: { todos: [...], total: number }
 * Frontend expects: Todo[] array
 * Also converts snake_case fields to camelCase
 */
export function useTodos(): UseTodosReturn {
  const [todos, setTodos] = useState<Todo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentFilter, setFilter] = useState<TodoFilter>("all")
  const [currentSort, setSort] = useState<TodoSort>("createdAt")

  // Initial fetch on mount
  useEffect(() => {
    refreshTodos()
  }, [])

  /**
   * Task T-235: Apply filtering based on status
   * Converts backend is_complete field to frontend status field
   */
  const getFilteredTodos = (): Todo[] => {
    let filtered = todos

    // Apply status filter
    if (currentFilter === "pending") {
      filtered = filtered.filter((todo) => todo.status === "pending")
    } else if (currentFilter === "completed") {
      filtered = filtered.filter((todo) => todo.status === "completed")
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (currentSort) {
        case "title":
          return a.title.localeCompare(b.title)
        case "priority": {
          const priorityOrder = { low: 0, medium: 1, high: 2 }
          return priorityOrder[b.priority] - priorityOrder[a.priority]
        }
        case "dueDate":
          return (
            new Date(a.dueDate || "").getTime() -
            new Date(b.dueDate || "").getTime()
          )
        case "createdAt":
        default:
          return (
            new Date(b.createdAt).getTime() -
            new Date(a.createdAt).getTime()
          )
      }
    })

    return sorted
  }

  /**
   * Convert backend todo response to frontend format
   * Backend returns snake_case, frontend uses camelCase
   */
  const transformTodoResponse = (backendTodo: any): Todo => {
    return {
      id: backendTodo.id,
      userId: backendTodo.user_id,
      title: backendTodo.title,
      description: backendTodo.description,
      status: backendTodo.is_complete ? "completed" : "pending",
      priority: backendTodo.priority || "low",
      dueDate: backendTodo.due_date,
      createdAt: backendTodo.created_at,
      updatedAt: backendTodo.updated_at,
    }
  }

  const filteredTodos = getFilteredTodos()

  /**
   * Task T-235: Fetch all todos from backend
   * Endpoint: GET /api/todos
   * Returns: { todos: Todo[], total: number }
   * Includes JWT token via API wrapper
   */
  const refreshTodos = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await apiGet<{ todos: any[]; total: number }>("/api/todos")

      if (response.ok && response.data?.todos) {
        // Transform backend todos to frontend format
        const transformedTodos = response.data.todos.map(transformTodoResponse)
        setTodos(transformedTodos)
      } else {
        setError(response.error || "Failed to load todos")
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load todos"
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Task T-235: Create new todo
   * Endpoint: POST /api/todos
   * Body: title, description, status, priority, dueDate
   * Returns: Created todo with id, userId, timestamps
   */
  const createTodo = async (
    data: Omit<Todo, "id" | "userId" | "createdAt" | "updatedAt">
  ): Promise<Todo> => {
    try {
      setError(null)

      // Convert frontend format to backend format
      const backendData = {
        title: data.title,
        description: data.description,
        is_complete: data.status === "completed",
        priority: data.priority,
        due_date: data.dueDate,
      }

      const response = await apiPost<any>("/api/todos", backendData)

      if (response.ok && response.data) {
        // Transform and add new todo to state
        const transformedTodo = transformTodoResponse(response.data)
        setTodos([...todos, transformedTodo])
        return transformedTodo
      } else {
        throw new Error(response.error || "Failed to create todo")
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create todo"
      setError(errorMessage)
      throw err
    }
  }

  /**
   * Task T-235: Update existing todo
   * Endpoint: PATCH /api/todos/{id}
   * Body: Partial todo fields (title, description, status, priority, dueDate)
   * Returns: Updated todo
   */
  const updateTodo = async (
    id: string,
    data: Partial<Todo>
  ): Promise<Todo> => {
    try {
      setError(null)

      // Convert frontend format to backend format
      const backendData: any = {}
      if (data.title !== undefined) backendData.title = data.title
      if (data.description !== undefined) backendData.description = data.description
      if (data.status !== undefined) backendData.is_complete = data.status === "completed"
      if (data.priority !== undefined) backendData.priority = data.priority
      if (data.dueDate !== undefined) backendData.due_date = data.dueDate

      const response = await apiPatch<any>(`/api/todos/${id}`, backendData)

      if (response.ok && response.data) {
        // Transform and update todo in state
        const transformedTodo = transformTodoResponse(response.data)
        setTodos(
          todos.map((todo) => (todo.id === id ? transformedTodo : todo))
        )
        return transformedTodo
      } else {
        throw new Error(response.error || "Failed to update todo")
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update todo"
      setError(errorMessage)
      throw err
    }
  }

  /**
   * Task T-235: Delete todo
   * Endpoint: DELETE /api/todos/{id}
   * Returns: void
   */
  const deleteTodo = async (id: string): Promise<void> => {
    try {
      setError(null)

      const response = await apiDelete(`/api/todos/${id}`)

      if (response.ok) {
        // Remove todo from state
        setTodos(todos.filter((todo) => todo.id !== id))
      } else {
        throw new Error(response.error || "Failed to delete todo")
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete todo"
      setError(errorMessage)
      throw err
    }
  }

  return {
    todos,
    filteredTodos,
    isLoading,
    error,
    currentFilter,
    currentSort,
    setFilter,
    setSort,
    createTodo,
    updateTodo,
    deleteTodo,
    refreshTodos,
  }
}
