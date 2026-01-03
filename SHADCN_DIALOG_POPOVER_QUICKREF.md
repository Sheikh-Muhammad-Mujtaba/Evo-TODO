# Shadcn/UI Dialog & Popover - Quick Reference

## Dialog Component Overview

### When to Use
- Modal interactions requiring user attention
- Confirmation dialogs for destructive actions
- Complex forms that need full-screen focus
- Multi-step workflows

### Basic Pattern
```tsx
<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">Cancel</Button>
      </DialogClose>
      <Button>Save</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### State Management
```tsx
// Controlled Dialog (recommended for most cases)
const [open, setOpen] = useState(false)
<Dialog open={open} onOpenChange={setOpen}>
```

### Form Integration Pattern
```tsx
const [open, setOpen] = useState(false)
const form = useForm({ resolver: zodResolver(schema) })

const onSubmit = async (data) => {
  await api.create(data)
  form.reset()
  setOpen(false) // Close only after success
}

<form onSubmit={form.handleSubmit(onSubmit)}>
  {/* fields */}
</form>
```

---

## Popover Component Overview

### When to Use
- Non-modal, inline selections
- Quick edits without full focus requirement
- Priority/status selection
- Small forms or dropdown menus
- Context-sensitive options

### Basic Pattern
```tsx
<Popover open={open} onOpenChange={setOpen}>
  <PopoverTrigger asChild>
    <Button>Open</Button>
  </PopoverTrigger>
  <PopoverContent>
    {/* Content - auto-closes after selection */}
  </PopoverContent>
</Popover>
```

### Selection Pattern with Auto-Close
```tsx
const [open, setOpen] = useState(false)
const [value, setValue] = useState("")

const handleSelect = (newValue) => {
  setValue(newValue)
  setOpen(false) // Auto-close after selection
}
```

### Combobox Pattern (Search + Select)
```tsx
<Popover open={open} onOpenChange={setOpen}>
  <PopoverTrigger asChild>
    <Button aria-expanded={open}>{value}</Button>
  </PopoverTrigger>
  <PopoverContent className="w-[200px] p-0">
    <Command>
      <CommandInput placeholder="Search..." />
      <CommandList>
        <CommandGroup>
          {items.map((item) => (
            <CommandItem
              key={item.value}
              onSelect={() => {
                setValue(item.value)
                setOpen(false)
              }}
            >
              {item.label}
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </Command>
  </PopoverContent>
</Popover>
```

---

## Accessibility Checklist

- [x] Dialog has title and description (required)
- [x] Focus moves to dialog when opened (automatic)
- [x] Focus trapped within dialog (automatic)
- [x] Escape key closes dialog (automatic)
- [x] Tab order preserved (automatic)
- [x] ARIA labels on semantic elements
- [x] aria-expanded on popover trigger
- [x] Proper button types (submit vs button)

---

## Task Management Patterns

### Quick Priority Selection
```tsx
<Popover open={priorityOpen} onOpenChange={setPriorityOpen}>
  <PopoverTrigger asChild>
    <Button variant="outline">
      <Badge className={getPriorityColor(priority)} />
      {priority}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-40 p-2">
    {priorities.map((p) => (
      <Button
        key={p}
        onClick={() => {
          setPriority(p)
          setPriorityOpen(false)
        }}
      >
        {p}
      </Button>
    ))}
  </PopoverContent>
</Popover>
```

### Task Creation Dialog with Form
```tsx
const createTaskSchema = z.object({
  title: z.string().min(1, "Title required").max(100),
  description: z.string().max(500).optional(),
  priority: z.enum(["low", "medium", "high"]),
  dueDate: z.string().optional(),
})

<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent>
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Input fields with form.register() */}
      <DialogFooter>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create"}
        </Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

### Confirmation Dialog for Delete
```tsx
import { AlertDialog } from "@/components/ui/alert-dialog"

<AlertDialog>
  <AlertDialogTrigger asChild>
    <Button variant="destructive">Delete</Button>
  </AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone.
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
```

---

## Common Mistakes to Avoid

1. **Not resetting form after submission** - Reset form after successful submission, not before
2. **Closing dialog on form error** - Only close dialog after successful API response
3. **Forgetting loading state** - Disable button with `disabled={isSubmitting}`
4. **Not using controlled state** - Use `useState` to control open state from parent
5. **Dialog within dropdown** - Wrap Dialog outside DropdownMenu to avoid z-index issues
6. **Auto-closing too aggressively** - Only auto-close Popover after selection, not on keyboard
7. **Missing ARIA labels** - Always include DialogTitle and DialogDescription

---

## Key Props

### Dialog Props
- `open` - Control dialog visibility
- `onOpenChange` - Callback when open state changes

### DialogContent Props
- `className="sm:max-w-[425px]"` - Set responsive width
- `onEscapeKeyDown` - Handle Escape key custom behavior

### Popover Props
- `open` - Control popover visibility
- `onOpenChange` - Callback for visibility changes
- `side="right"` - Position relative to trigger
- `align="start"` - Vertical alignment

### PopoverContent Props
- `className="w-80"` - Set width
- `side="right" align="start"` - Positioning

---

## Real-World Task Management Example

```tsx
"use client"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

export function TaskCard({ task, onUpdate, onDelete }) {
  const [editOpen, setEditOpen] = useState(false)
  const [statusOpen, setStatusOpen] = useState(false)
  const form = useForm({
    resolver: zodResolver(taskSchema),
    defaultValues: task
  })

  return (
    <div className="flex items-center justify-between p-4 border rounded">
      <div>
        <h3>{task.title}</h3>
        <p className="text-sm text-muted-foreground">{task.description}</p>
      </div>

      {/* Quick Status Selector */}
      <Popover open={statusOpen} onOpenChange={setStatusOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline">{task.status}</Button>
        </PopoverTrigger>
        <PopoverContent className="w-40 p-2">
          {["todo", "in-progress", "done"].map((status) => (
            <Button
              key={status}
              variant={task.status === status ? "default" : "ghost"}
              onClick={() => {
                onUpdate({ ...task, status })
                setStatusOpen(false)
              }}
            >
              {status}
            </Button>
          ))}
        </PopoverContent>
      </Popover>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost">Edit</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
          </DialogHeader>
          <form onSubmit={form.handleSubmit((data) => {
            onUpdate(data)
            setEditOpen(false)
          })}>
            <Input {...form.register("title")} />
            <DialogFooter>
              <Button type="submit">Save</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button variant="destructive">Delete</Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this task?</AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => onDelete(task.id)}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
```

---

## Performance Tips

1. Use `useState` for dialog state (not useCallback)
2. Memoize handler functions if Dialog/Popover is reused
3. Use `asChild` to avoid extra wrapper divs
4. For long lists in Popover, use virtualization libraries
5. Reset form only after successful submission
6. Disable buttons during submission to prevent double-clicks

---

## Testing Patterns

```tsx
// Test Dialog Opening
it("opens dialog on button click", () => {
  const { getByRole } = render(<CreateTaskDialog />)
  fireEvent.click(getByRole("button", { name: /open/i }))
  expect(getByRole("dialog")).toBeInTheDocument()
})

// Test Form Submission
it("submits form data", async () => {
  const onSubmit = jest.fn()
  const { getByRole } = render(<CreateTaskDialog onSubmit={onSubmit} />)
  fireEvent.click(getByRole("button", { name: /open/i }))
  
  fireEvent.change(getByRole("textbox", { name: /title/i }), {
    target: { value: "Test Task" }
  })
  fireEvent.click(getByRole("button", { name: /create/i }))
  
  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      title: "Test Task"
    }))
  })
})

// Test Keyboard Navigation
it("closes on Escape key", () => {
  const { getByRole, queryByRole } = render(<CreateTaskDialog />)
  fireEvent.click(getByRole("button", { name: /open/i }))
  fireEvent.keyDown(getByRole("dialog"), { key: "Escape" })
  expect(queryByRole("dialog")).not.toBeInTheDocument()
})
```

---

## Resource Links

- Shadcn/UI Docs: https://ui.shadcn.com/
- Radix UI: https://radix-ui.com/
- React Hook Form: https://react-hook-form.com/
- Zod Validation: https://zod.dev/
- Tailwind CSS: https://tailwindcss.com/
