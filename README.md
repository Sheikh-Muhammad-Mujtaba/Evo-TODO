# Quick Start Guide - CLI Todo Application

## Prerequisites

- Python 3.13+
- `uv` package manager (v0.9.18+)

## Setup

### 1. Install Dependencies

```bash
cd Evo-TODO
uv sync --all-extras
```

This will:
- ✅ Create virtual environment at `.venv/`
- ✅ Install pytest and pytest-cov
- ✅ Build todo-app package

### 2. Run Tests

```bash
uv run pytest tests/unit/ -v
```

Expected output:
```
============================== 67 passed in 4.86s ==============================
```

### 3. Run Application

```bash
uv run python -m src.todo_app.main
```

## Usage

Once the application starts, you'll see the menu:

```
=== TODO Manager ===
1. View All Todos
2. Add Todo
3. Update Todo
4. Mark Complete/Incomplete
5. Delete Todo
6. Exit

Select option (1-6):
```

### User Stories

**Story 1: View List**
- Select option `1`
- See all todos with status (☐ incomplete, ☑ complete)

**Story 2: Add Todo**
- Select option `2`
- Enter title (required)
- Enter description (optional)
- Confirm creation

**Story 3: Mark Complete**
- Select option `4`
- Enter todo ID
- Status toggles and displays with checkbox

**Story 4: Update Todo**
- Select option `3`
- Enter todo ID
- Enter new title (leave blank to keep)
- Enter new description (leave blank to keep)

**Story 5: Delete Todo**
- Select option `5`
- Enter todo ID
- Confirm deletion with "yes"/"no"

**Exit**
- Select option `6`
- Application terminates

## Example Session

```bash
$ uv run python -m src.todo_app.main

=== TODO Manager ===
1. View All Todos
2. Add Todo
3. Update Todo
4. Mark Complete/Incomplete
5. Delete Todo
6. Exit

Select option (1-6): 2
Enter todo title: Buy Groceries
Enter description (optional): Milk, eggs, bread
✓ Todo added successfully! (ID: 1)

=== TODO Manager ===
1. View All Todos
...
Select option (1-6): 1

=== TODO List ===

[1] ☐ Buy Groceries | Milk, eggs, bread

=== TODO Manager ===
...
Select option (1-6): 4
Enter todo ID to toggle: 1
✓ Todo 1 marked as complete!

=== TODO Manager ===
...
Select option (1-6): 1

=== TODO List ===

[1] ☑ Buy Groceries | Milk, eggs, bread

=== TODO Manager ===
...
Select option (1-6): 6
Goodbye!
```

## Project Structure

```
.
├── src/todo_app/              # Implementation
│   ├── models/task.py         # Task data model
│   ├── services/              # Business logic
│   │   └── todo_manager.py    # CRUD operations
│   ├── ui/cli_handler.py      # CLI formatting
│   └── main.py                # Entry point & menu loop
│
├── tests/                     # Test suite
│   └── unit/
│       ├── test_task.py       # Model tests (20 tests)
│       ├── test_todo_manager.py # Service tests (26 tests)
│       └── test_cli_handler.py # UI tests (21 tests)
│
├── pyproject.toml             # Project configuration
├── .gitignore                 # Git ignore patterns
└── .venv/                     # Virtual environment (created by uv sync)
```

## Development

### Run Tests with Coverage

```bash
uv run pytest tests/unit/ --cov=src --cov-report=term-missing
```

### Run Specific Test

```bash
uv run pytest tests/unit/test_task.py -v
```

### Run Single Test Function

```bash
uv run pytest tests/unit/test_todo_manager.py::TestTodoManagerCreation::test_create_task_basic -v
```

## Architecture

**3-Layer Architecture**:

1. **Data Layer** (models/)
   - `Task`: Immutable value object

2. **Business Logic** (services/)
   - `TodoManager`: In-memory CRUD operations

3. **Presentation** (ui/)
   - `cli_handler`: Formatting and prompts
   - `main`: Menu loop and routing

**Storage**: In-memory List[Task] (no persistence)

## Features

✅ **All 5 User Stories Implemented**
- View List with status indicators
- Add Todo with title and description
- Mark Complete/Incomplete
- Update title and/or description
- Delete with confirmation

✅ **Error Handling**
- Empty title validation
- Non-existent ID handling
- Invalid input graceful recovery
- KeyboardInterrupt shutdown

✅ **Performance**
- Sub-100ms response time
- Suitable for 10k+ todos
- Efficient O(n) operations

## Troubleshooting

**Error: `No module named 'src'`**
- Make sure you're in the project root directory
- Run `uv sync` first

**Error: `pytest not found`**
- Run `uv sync --all-extras` to install dev dependencies

**Application crashes on input**
- This shouldn't happen - all inputs are handled gracefully
- Please report via git issue if it occurs

## Files

- `IMPLEMENTATION_STATUS.md` - Detailed implementation report
- `UV_VERIFICATION.md` - UV setup and testing verification
- `FINAL_VERIFICATION.txt` - Final deployment checklist

---

**Status**: ✅ Production Ready
**Python**: 3.13+
**Package Manager**: uv
**Tests**: 67/67 Passing
