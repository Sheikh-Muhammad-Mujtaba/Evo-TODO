# Root Cause Analysis: 401 Unauthorized Auto-Logout Issue

**Date**: 2026-01-01  
**Issue**: Users can sign up/login but immediately get logged out when accessing `/api/todos`  
**Status**: ✅ FIXED  
**Severity**: CRITICAL

---

## The Problem

When a user successfully logs in via Better Auth:
1. Session is created ✅
2. They're redirected to `/todos` page ✅
3. Frontend immediately calls `/api/todos` API endpoint ❌
4. Backend returns `401 Unauthorized` ❌
5. Frontend's API client receives 401 and calls `authClient.signOut()` ❌
6. User is immediately logged out ❌

This created the illusion that login failed, even though it actually succeeded.

---

## Root Cause: Database Table Mismatch

### What Better Auth Creates
Better Auth creates a database table named **`user`** (singular) with this schema:

```sql
user
├── id (TEXT) - UUID string, primary key
├── email (TEXT) - unique
├── name (TEXT)
├── emailVerified (BOOLEAN)
├── image (TEXT, optional)
├── createdAt (TIMESTAMP)
└── updatedAt (TIMESTAMP)
```

### What Backend Was Querying
The backend User model defined a table named **`users`** (plural) with this schema:

```python
users
├── id (UUID) - UUID object
├── email (VARCHAR)
├── password_hash (VARCHAR) - ❌ Better Auth doesn't store this
├── name (VARCHAR)
├── is_active (BOOLEAN) - ❌ Better Auth doesn't use this
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### The Mismatch
The backend was looking for users in the **`users`** table, but Better Auth stores them in the **`user`** table!

```python
# In deps.py get_current_user():
statement = select(User).where(User.id == user_id)
user = db.exec(statement).first()

# This translates to:
# SELECT * FROM users WHERE id = {user_id}
# But the table is called 'user', not 'users'!
```

When the query executed, it would either:
1. Fail to find the table (if SQLAlchemy strict mode)
2. Find an empty table (if table actually existed from previous schema)
3. Return None (user not found)

Result: Backend returns 401 Unauthorized → Frontend logs out user

---

## The Fix

Updated three files to match Better Auth's actual database schema:

### 1. `backend/app/models/user.py`
**Changes**:
- `__tablename__` changed from `"users"` to `"user"` ✅
- Field `id` type changed from `UUID` to `str` ✅
- Added Better Auth fields: `emailVerified`, `image`
- Changed timestamps from snake_case to camelCase (Better Auth convention)
- Removed `password_hash` (Better Auth doesn't use)
- Removed `is_active` (Better Auth doesn't use)

**Before**:
```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**After**:
```python
class User(SQLModel, table=True):
    __tablename__ = "user"  # Singular, matching Better Auth
    id: str = Field(primary_key=True)  # String UUID from Better Auth
    email: str
    name: str
    emailVerified: bool
    image: Optional[str]
    createdAt: datetime
    updatedAt: datetime
```

### 2. `backend/app/models/todo.py`
**Changes**:
- `user_id` type changed from `UUID` to `str`
- Foreign key changed from `"users.id"` to `"user.id"`

**Before**:
```python
class Todo(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id")
```

**After**:
```python
class Todo(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id")
```

### 3. `backend/app/api/deps.py`
**Changes**:
- Removed UUID conversion (user_id stays as string from JWT)
- Removed `is_active` validation (field doesn't exist in Better Auth)
- Updated `get_user_id_from_header` return type from `Optional[UUID]` to `Optional[str]`

**Before**:
```python
# Extract and convert to UUID
user_id_str: str = payload.get("sub")
user_id = UUID(user_id_str)

# Query with UUID
statement = select(User).where(User.id == user_id)

# Check is_active
if not user.is_active:
    raise HTTPException(401)
```

**After**:
```python
# Keep as string (matches Better Auth's user.id type)
user_id: str = payload.get("sub")

# Query with string
statement = select(User).where(User.id == user_id)

# No is_active check (field doesn't exist)
```

---

## Verification

After the fix:
1. ✅ User creates account via Better Auth
2. ✅ User object stored in `user` table (string UUID)
3. ✅ JWT token generated with `sub: {user_id}`
4. ✅ Frontend sends JWT in Authorization header
5. ✅ Backend validates JWT signature
6. ✅ Backend extracts user_id from `sub` claim (stays as string)
7. ✅ Backend queries: `SELECT * FROM user WHERE id = {user_id}`
8. ✅ User found in database
9. ✅ Backend returns 200 with todos
10. ✅ User stays logged in

---

## Key Insight

**Never assume the database schema.** Better Auth is an external service that:
- Creates and manages its own tables
- Uses specific naming conventions (`user` not `users`)
- Uses specific field types and names (`emailVerified` not `email_verified`)
- Uses string UUIDs, not UUID objects

The backend's ORM models must match the actual database schema, not a conceptual "user" model.

---

## Files Modified

- `backend/app/models/user.py` - Fixed table name and schema
- `backend/app/models/todo.py` - Fixed user_id type and foreign key
- `backend/app/api/deps.py` - Fixed user_id handling and removed is_active check

**Commit**: `b177556` - "CRITICAL FIX: T-221 - User table mismatch between Better Auth and backend models"

---

## Impact

- **Severity**: CRITICAL - Completely broke API authentication
- **Scope**: All API endpoints requiring authentication
- **User Impact**: Users could not access any protected endpoints after login
- **Resolution**: Complete authentication flow now works end-to-end

---

## Lessons Learned

1. **Schema Awareness**: Always verify ORM model table/field names match the actual database
2. **Type Matching**: String UUIDs ≠ UUID objects; must match exactly
3. **External Services**: Third-party services (like Better Auth) have their own conventions
4. **Testing**: Comprehensive integration tests would have caught this immediately
5. **Documentation**: Better Auth docs clearly show the exact schema; reference them in code

---

*Generated on 2026-01-01*
