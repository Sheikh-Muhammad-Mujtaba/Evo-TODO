# Shadcn/UI Dialog and Popover Components Research
## Task Management Application Implementation Guide

This comprehensive research guide covers best practices, patterns, and code examples for using Shadcn/UI Dialog and Popover components in a task management application.

---

## 1. Dialog Component: Best Practices

### 1.1 Fundamental Structure

The Shadcn/UI Dialog component provides a modal dialog pattern built on Radix UI with Tailwind CSS styling.

```tsx
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function BasicDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Open Dialog</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Dialog Title</DialogTitle>
          <DialogDescription>
            Add a description of the dialog's purpose here.
          </DialogDescription>
        </DialogHeader>
        <div>{/* Content goes here */}</div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button type="submit">Confirm</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

**Key Points:**
- Use `asChild` prop on triggers to avoid extra wrapper divs
- `DialogClose` automatically closes the dialog when clicked
- Structure follows semantic HTML patterns (header, content, footer)
- Built on Radix UI Dialog for accessibility guarantees

### 1.2 Confirmation Dialogs (Destructive Actions)

For permanent actions like deletion, use AlertDialog instead:

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

export function DeleteTaskConfirmation() {
  const handleDelete = () => {
    // Perform deletion
    console.log("Task deleted")
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="sm">
          Delete Task
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete your
            task and remove all associated data.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

**Best Practices:**
- Use `AlertDialog` for destructive actions, not regular `Dialog`
- Provide clear consequences in the description
- Use variant="destructive" on the delete button
- Require explicit confirmation (not just one-click)
- Avoid auto-closing; require user action

### 1.3 Form Modals with React Hook Form

Dialog combined with React Hook Form provides validated form submission:

```tsx
"use client"

import { useState } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

// Define validation schema
const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(100),
  description: z.string().max(500).optional(),
  priority: z.enum(["low", "medium", "high"]),
  dueDate: z.string().optional(),
})

type TaskFormData = z.infer<typeof taskSchema>

export function CreateTaskDialog() {
  const [open, setOpen] = useState(false)
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "medium",
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    try {
      // Submit to API
      console.log("Creating task:", data)
      form.reset()
      setOpen(false)
    } catch (error) {
      console.error("Error creating task:", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Create Task</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Add a new task to your todo list. Fill in the details below.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Task Title</Label>
            <Input
              id="title"
              placeholder="Enter task title"
              {...form.register("title")}
            />
            {form.formState.errors.title && (
              <p className="text-destructive text-sm">
                {form.formState.errors.title.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="Add task details"
              {...form.register("description")}
              className="min-h-[100px]"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Controller
              name="priority"
              control={form.control}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger id="priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting ? "Creating..." : "Create Task"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

**Key Patterns:**
- Use `useState` to control dialog open state
- Wrap form submission in try-catch for error handling
- Show loading state during submission
- Reset form after successful submission
- Close dialog only after successful operation
- Use Zod for schema validation

---

## 2. Popover Component: Inline Selections

### 2.1 Basic Popover

Popovers are non-modal dialogs positioned relative to a trigger element, ideal for quick inline edits.

```tsx
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function PopoverDemo() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline">Open popover</Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Dimensions</h4>
            <p className="text-muted-foreground text-sm">
              Set the dimensions for your element.
            </p>
          </div>
          <div className="space-y-3">
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="width">Width</Label>
              <Input
                id="width"
                defaultValue="100%"
                className="col-span-2 h-8"
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="height">Height</Label>
              <Input
                id="height"
                defaultValue="25px"
                className="col-span-2 h-8"
              />
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
```

### 2.2 Priority Level Selection with Popover

Perfect for task management - inline priority selection:

```tsx
"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"

type Priority = "low" | "medium" | "high"

const priorities: { value: Priority; label: string; color: string }[] = [
  { value: "low", label: "Low", color: "bg-blue-500" },
  { value: "medium", label: "Medium", color: "bg-yellow-500" },
  { value: "high", label: "High", color: "bg-red-500" },
]

export function PrioritySelector() {
  const [open, setOpen] = React.useState(false)
  const [selectedPriority, setSelectedPriority] = React.useState<Priority>(
    "medium"
  )

  const current = priorities.find((p) => p.value === selectedPriority)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="w-full justify-start">
          {current && <Badge className={`mr-2 ${current.color}`} />}
          {current?.label || "Set priority"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-40 p-0" side="right" align="start">
        <div className="space-y-2 p-4">
          <p className="text-muted-foreground text-sm font-medium">Priority</p>
          {priorities.map((priority) => (
            <Button
              key={priority.value}
              variant={selectedPriority === priority.value ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => {
                setSelectedPriority(priority.value)
                setOpen(false)
              }}
            >
              <Badge className={`mr-2 ${priority.color}`} />
              {priority.label}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  )
}
```

### 2.3 Combobox Pattern (Search + Select)

For selecting from a large list with search capability:

```tsx
"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

type TaskStatus = {
  value: string
  label: string
}

const statuses: TaskStatus[] = [
  { value: "backlog", label: "Backlog" },
  { value: "todo", label: "Todo" },
  { value: "in-progress", label: "In Progress" },
  { value: "done", label: "Done" },
  { value: "canceled", label: "Canceled" },
]

export function StatusCombobox() {
  const [open, setOpen] = React.useState(false)
  const [selectedStatus, setSelectedStatus] = React.useState<TaskStatus | null>(
    null
  )

  return (
    <div className="flex items-center space-x-4">
      <span className="text-muted-foreground text-sm">Status</span>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="w-[150px] justify-between"
            aria-expanded={open}
          >
            {selectedStatus ? selectedStatus.label : "Select status..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[150px] p-0" side="right" align="start">
          <Command>
            <CommandInput placeholder="Search status..." />
            <CommandList>
              <CommandEmpty>No status found.</CommandEmpty>
              <CommandGroup>
                {statuses.map((status) => (
                  <CommandItem
                    key={status.value}
                    value={status.value}
                    onSelect={(value) => {
                      const newStatus = statuses.find((s) => s.value === value)
                      setSelectedStatus(newStatus || null)
                      setOpen(false)
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedStatus?.value === status.value
                          ? "opacity-100"
                          : "opacity-0"
                      )}
                    />
                    {status.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
}
```

---

## 3. State Management Patterns

### 3.1 Uncontrolled Dialog (Built-in State)

Simplest approach - Dialog manages its own state:

```tsx
export function UncontrolledDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Uncontrolled Dialog</DialogTitle>
        </DialogHeader>
        <p>Dialog state is managed by the Dialog component itself</p>
      </DialogContent>
    </Dialog>
  )
}
```

**Use when:**
- Simple, one-off dialogs
- No external state needed
- Dialog doesn't depend on parent state

### 3.2 Controlled Dialog (Parent State Management)

Parent component controls open/close state:

```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export function ControlledDialog() {
  const [open, setOpen] = useState(false)

  const handleOpenChange = (newOpen: boolean) => {
    // Add validation or side effects here
    setOpen(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Controlled Dialog</DialogTitle>
          <DialogDescription>
            Dialog state is controlled by the parent component
          </DialogDescription>
        </DialogHeader>
        <p>Open state: {open ? "true" : "false"}</p>
      </DialogContent>
    </Dialog>
  )
}
```

**Use when:**
- Need to synchronize with other state
- Dialog position affects other components
- Conditional rendering based on open state

### 3.3 Multiple Dialogs from Dropdown Menu

Managing multiple dialog states from a menu:

```tsx
"use client"

import { useState } from "react"
import { MoreHorizontalIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"

export function TaskActionsMenu() {
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  return (
    <>
      {/* Dropdown Menu */}
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <MoreHorizontalIcon className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setEditDialogOpen(true)}>
            Edit
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setDeleteDialogOpen(true)}>
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>Make changes to your task</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input placeholder="Task title" />
            <Input placeholder="Description" />
          </div>
          <DialogFooter>
            <Button onClick={() => setEditDialogOpen(false)}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              This action cannot be undone. Are you sure you want to delete
              this task?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                // Delete task
                setDeleteDialogOpen(false)
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
```

---

## 4. Accessibility Best Practices

### 4.1 Focus Management

Shadcn/UI components built on Radix UI automatically handle focus management:

```tsx
export function AccessibleDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        {/* Focus automatically moves here when dialog opens */}
        <DialogHeader>
          <DialogTitle>Accessible Dialog</DialogTitle>
          {/* DialogTitle is focused by default */}
        </DialogHeader>
        <div>
          <label htmlFor="input">Name</label>
          {/* First focusable element after title */}
          <input id="input" type="text" />
        </div>
        {/* Focus trap ensures user can't tab outside dialog */}
      </DialogContent>
    </Dialog>
  )
}
```

**Features:**
- Focus automatically moves to dialog when opened
- Focus is trapped within the dialog
- Focus returns to trigger element when closed
- Tab order is preserved within dialog

### 4.2 ARIA Attributes

Proper ARIA markup for assistive technologies:

```tsx
export function AriaDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button aria-label="Create a new task">Create Task</Button>
      </DialogTrigger>
      <DialogContent
        role="dialog"
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
      >
        <DialogHeader>
          <DialogTitle id="dialog-title">Create New Task</DialogTitle>
          <DialogDescription id="dialog-description">
            Fill in the details to create a new task in your todo list.
          </DialogDescription>
        </DialogHeader>
        {/* Content */}
      </DialogContent>
    </Dialog>
  )
}
```

**ARIA Guidelines:**
- `role="dialog"` on DialogContent
- `aria-labelledby` points to title element
- `aria-describedby` points to description element
- Use semantic HTML (labels, buttons)
- Announce dynamic content changes

### 4.3 Keyboard Navigation

```tsx
export function KeyboardAccessibleDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          Open Dialog (Press Enter or Space)
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Keyboard Navigation Demo</DialogTitle>
          <DialogDescription>
            Try using Tab, Shift+Tab, Enter, and Escape keys
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <button>First focusable element (Tab to focus)</button>
          <button>Second focusable element</button>
          <button>Third focusable element</button>
          {/* Escape key closes dialog automatically */}
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

**Keyboard Support:**
- **Tab**: Move focus to next element
- **Shift+Tab**: Move focus to previous element
- **Enter/Space**: Activate buttons, toggle checkboxes
- **Escape**: Close dialog

---

## 5. Common Patterns for Task Management

### 5.1 Complete Task Creation Workflow

Combining Dialog, Form, and state management:

```tsx
"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const createTaskSchema = z.object({
  title: z.string().min(1, "Title is required").max(100),
  description: z.string().max(500).optional().default(""),
  priority: z.enum(["low", "medium", "high"]).default("medium"),
  dueDate: z.string().optional(),
  assignee: z.string().optional(),
})

type CreateTaskInput = z.infer<typeof createTaskSchema>

export function CreateTaskWorkflow() {
  const [open, setOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<CreateTaskInput>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "medium",
    },
  })

  const onSubmit = async (data: CreateTaskInput) => {
    setIsSubmitting(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      console.log("Task created:", data)
      toast.success("Task created successfully!")

      // Reset form and close dialog
      form.reset()
      setOpen(false)
    } catch (error) {
      toast.error("Failed to create task. Please try again.")
      console.error(error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Create Task</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Add a new task to your list. Fill in the required fields below.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {/* Title Field */}
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              placeholder="Enter task title"
              {...form.register("title")}
              disabled={isSubmitting}
            />
            {form.formState.errors.title && (
              <p className="text-destructive text-sm">
                {form.formState.errors.title.message}
              </p>
            )}
          </div>

          {/* Description Field */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Add task details (optional)"
              {...form.register("description")}
              disabled={isSubmitting}
              className="min-h-[100px]"
            />
          </div>

          {/* Priority Field */}
          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select
              value={form.watch("priority")}
              onValueChange={(value) =>
                form.setValue("priority", value as "low" | "medium" | "high")
              }
              disabled={isSubmitting}
            >
              <SelectTrigger id="priority">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Due Date Field */}
          <div className="space-y-2">
            <Label htmlFor="dueDate">Due Date</Label>
            <Input
              id="dueDate"
              type="date"
              {...form.register("dueDate")}
              disabled={isSubmitting}
            />
          </div>

          {/* Assignee Field */}
          <div className="space-y-2">
            <Label htmlFor="assignee">Assign To</Label>
            <Select
              value={form.watch("assignee") || ""}
              onValueChange={(value) => form.setValue("assignee", value)}
              disabled={isSubmitting}
            >
              <SelectTrigger id="assignee">
                <SelectValue placeholder="Select assignee" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="user1">John Doe</SelectItem>
                <SelectItem value="user2">Jane Smith</SelectItem>
                <SelectItem value="user3">Bob Johnson</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <DialogFooter className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Task"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

---

## 6. Key Implementation Takeaways

### Dialog Component
1. **Use for**: Modal interactions, confirmation dialogs, complex forms
2. **State**: Can be uncontrolled or controlled with parent state
3. **Best practice**: Show loading state, reset form on success
4. **Accessibility**: Focus management, ARIA labels automatic via Radix UI

### Popover Component
1. **Use for**: Inline selections, non-modal interactions, quick actions
2. **Auto-close**: Set `setOpen(false)` after selection for better UX
3. **Positioning**: Use `side` and `align` props for proper placement
4. **Combobox**: Combine with Command component for searchable lists

### State Management
1. **Uncontrolled**: For simple, isolated dialogs
2. **Controlled**: When dialog state affects parent or other components
3. **Multiple dialogs**: Use separate state variables per dialog
4. **Forms**: Use React Hook Form with Zod for validation

### Accessibility
1. Focus management handled automatically by Radix UI
2. Always include DialogTitle and DialogDescription
3. Use semantic HTML and proper aria labels
4. Keyboard navigation (Tab, Escape) works out of the box

---

## 7. Resources and References

- **Official Shadcn/UI Docs**: https://ui.shadcn.com/docs
- **Radix UI Dialog**: https://radix-ui.com/docs/primitives/components/dialog
- **Radix UI Popover**: https://radix-ui.com/docs/primitives/components/popover
- **React Hook Form**: https://react-hook-form.com/
- **Zod Validation**: https://zod.dev/
- **WCAG Accessibility Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
