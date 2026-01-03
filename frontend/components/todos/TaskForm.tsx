'use client'

import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTodos } from '@/lib/hooks/useTodos'
import { Todo } from '@/lib/types/todo'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

// Validation schema
const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(500, 'Title must be under 500 characters'),
  description: z.string().max(2000, 'Description must be under 2000 characters').optional().default(''),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']).default('MEDIUM'),
  dueDate: z.string().optional().default(''),
})

type TaskFormData = z.infer<typeof taskSchema>

interface TaskFormProps {
  onSuccess?: () => void
  initialData?: Todo
  isEditing?: boolean
}

/**
 * Task T027: TaskForm Component
 *
 * Features:
 * 1. Create new tasks with validation
 * 2. Edit existing tasks
 * 3. Form validation using react-hook-form + zod
 * 4. Priority selection (HIGH, MEDIUM, LOW)
 * 5. Optional due date
 * 6. Toast notifications for success/error
 */
export function TaskForm({ onSuccess, initialData, isEditing = false }: TaskFormProps) {
  const { createTodo, updateTodo } = useTodos()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: initialData ? {
      title: initialData.title,
      description: initialData.description || '',
      priority: initialData.priority,
      dueDate: initialData.dueDate || '',
    } : {
      title: '',
      description: '',
      priority: 'MEDIUM',
      dueDate: '',
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    try {
      setIsSubmitting(true)

      if (isEditing && initialData) {
        await updateTodo(initialData.id, {
          title: data.title,
          description: data.description,
          priority: data.priority,
          dueDate: data.dueDate || null,
        })
        toast.success('Task updated successfully')
      } else {
        await createTodo({
          title: data.title,
          description: data.description,
          priority: data.priority,
          dueDate: data.dueDate || null,
        })
        toast.success('Task created successfully')
        reset()
      }

      onSuccess?.()
    } catch (error) {
      console.error('Task form error:', error)
      toast.error(isEditing ? 'Failed to update task' : 'Failed to create task')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Title */}
      <div>
        <Label htmlFor="title">Task Title</Label>
        <Input
          id="title"
          placeholder="Enter task title"
          {...register('title')}
          className={errors.title ? 'border-red-500' : ''}
        />
        {errors.title && (
          <p className="text-sm text-red-500 mt-1">{errors.title.message}</p>
        )}
      </div>

      {/* Description */}
      <div>
        <Label htmlFor="description">Description (Optional)</Label>
        <textarea
          id="description"
          placeholder="Enter task description"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.description ? 'border-red-500' : 'border-gray-300'
          }`}
          rows={3}
          {...register('description')}
        />
        {errors.description && (
          <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>
        )}
      </div>

      {/* Priority */}
      <div>
        <Label htmlFor="priority">Priority</Label>
        <select
          id="priority"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...register('priority')}
        >
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
        </select>
      </div>

      {/* Due Date */}
      <div>
        <Label htmlFor="dueDate">Due Date (Optional)</Label>
        <Input
          id="dueDate"
          type="date"
          {...register('dueDate')}
        />
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full"
      >
        {isSubmitting ? 'Saving...' : isEditing ? 'Update Task' : 'Create Task'}
      </Button>
    </form>
  )
}
