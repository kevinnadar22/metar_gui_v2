# Security Features Explained

## 1. Password Hashing with Werkzeug

### What is Password Hashing?
Password hashing is a one-way cryptographic function that converts a plain text password into a fixed-length string of characters. The key feature is that it's **irreversible** - you cannot get the original password back from the hash.

### How Werkzeug Implements It
Werkzeug uses the **PBKDF2 (Password-Based Key Derivation Function 2)** algorithm with SHA-256:

```python
# In models.py
from werkzeug.security import generate_password_hash, check_password_hash

# When creating/updating password
user.set_password("MyPassword123")
# Internally: generate_password_hash("MyPassword123")
# Result: "pbkdf2:sha256:600000$salt$hash"

# When verifying password
user.check_password("MyPassword123")
# Internally: check_password_hash(stored_hash, "MyPassword123")
# Returns: True or False
```

### Security Benefits:
- **Salt**: Each password gets a unique random salt, preventing rainbow table attacks
- **Iterations**: Default 260,000 iterations make brute-force attacks extremely slow
- **One-way**: Even if database is compromised, original passwords cannot be recovered
- **Timing-safe**: Prevents timing attacks during password verification

### Example:
```python
# Stored in database (never store plain text!)
password_hash = "pbkdf2:sha256:600000$abc123$def456..."

# When user logs in
if user.check_password("MyPassword123"):  # Returns True
    # Login successful
```

---

## 2. Session-Based Authentication

### What is Session-Based Authentication?
Instead of sending credentials with every request, the server creates a **session** after successful login and stores it server-side. The client receives a **session ID** (stored in a cookie) to identify the session.

### How It Works:
1. **Login**: User provides username/password
2. **Verification**: Server checks credentials
3. **Session Creation**: Server creates session, stores user ID in session
4. **Cookie**: Browser receives session cookie automatically
5. **Subsequent Requests**: Browser sends cookie, server validates session

### Implementation:
```python
# In routes/auth.py - Login
session['user_id'] = user.id
session['username'] = user.username
session['role'] = user.role.value

# In auth.py - Checking authentication
@login_required
def protected_route():
    user_id = session.get('user_id')  # Get from session
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
```

### Security Features:
- **Server-side storage**: Session data stored on server, not client
- **Signed cookies**: Flask-Session signs cookies to prevent tampering
- **Expiration**: Sessions expire after 24 hours of inactivity
- **Secure**: Session ID is random and unpredictable

### Session Storage:
- **Type**: File-based (can be changed to Redis/DB for production)
- **Location**: `/app/sessions` in Docker, `./sessions` locally
- **Lifetime**: 24 hours (configurable)

---

## 3. SQL Injection Protection via SQLAlchemy ORM

### What is SQL Injection?
SQL Injection is an attack where malicious SQL code is inserted into input fields to manipulate database queries.

### Example of Vulnerable Code (NOT used):
```python
# DANGEROUS - Never do this!
query = f"SELECT * FROM users WHERE username = '{username}'"
# If username = "admin' OR '1'='1"
# Query becomes: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# This would return ALL users!
```

### How SQLAlchemy Protects:
SQLAlchemy uses **parameterized queries** and **ORM (Object-Relational Mapping)**:

```python
# SAFE - SQLAlchemy way
user = User.query.filter_by(username=username).first()
# OR
user = User.query.filter(User.username == username).first()

# SQLAlchemy automatically:
# 1. Escapes special characters
# 2. Uses parameterized queries
# 3. Validates data types
```

### Protection Mechanisms:
1. **Parameter Binding**: Values are bound separately from query structure
2. **Type Safety**: SQLAlchemy validates data types before querying
3. **ORM Abstraction**: No raw SQL strings with user input
4. **Automatic Escaping**: Special characters are automatically escaped

### Example:
```python
# User input: "admin' OR '1'='1"
username = request.json.get('username')

# SQLAlchemy query
user = User.query.filter_by(username=username).first()
# Generated SQL (safe):
# SELECT * FROM users WHERE username = %(username)s
# Parameters: {'username': "admin' OR '1'='1"}
# Result: No match found (treated as literal string)
```

---

## 4. Input Validation on Registration

### What is Input Validation?
Input validation ensures that user-provided data meets specific criteria before processing, preventing invalid or malicious data from entering the system.

### Validation Layers:

#### A. Frontend Validation (Client-side)
```javascript
// In signup.html
- Username: 3-50 characters
- Email: Valid email format
- Password: Minimum 8 characters, uppercase, lowercase, number
- Password match: Confirmation must match
```

#### B. Backend Validation (Server-side)
```python
# In routes/auth.py - register()

# 1. Required Fields
if not username or not email or not password:
    return jsonify({'error': 'All fields required'}), 400

# 2. Username Validation
if len(username) < 3 or len(username) > 50:
    return jsonify({'error': 'Username must be 3-50 characters'}), 400

# 3. Email Validation (Regex)
if not validate_email(email):
    return jsonify({'error': 'Invalid email format'}), 400

# 4. Password Strength
is_valid, error_msg = validate_password(password)
# Checks:
# - Minimum 8 characters
# - At least one uppercase letter
# - At least one lowercase letter
# - At least one number

# 5. Uniqueness Check
if User.query.filter_by(username=username).first():
    return jsonify({'error': 'Username already exists'}), 400
```

### Validation Rules:

**Username:**
- Length: 3-50 characters
- Characters: Letters, numbers, underscores
- Unique: Must not exist in database

**Email:**
- Format: Valid email pattern (regex)
- Unique: Must not exist in database
- Normalized: Converted to lowercase

**Password:**
- Minimum: 8 characters
- Must contain: Uppercase letter, lowercase letter, number
- Stored: Only as hash, never plain text

### Security Benefits:
- **Prevents invalid data**: Rejects malformed inputs early
- **Prevents duplicates**: Ensures unique usernames/emails
- **Strong passwords**: Enforces password complexity
- **Data integrity**: Maintains database consistency

---

## 5. Super Admin Role Management

### Role Hierarchy:
```
Super Admin (Level 3)
    ↓ Can manage
Admin (Level 2)
    ↓ Can manage
User (Level 1)
```

### Super Admin Capabilities:

#### A. Delete Admins
```python
# In routes/auth.py - delete_user()
@role_required('admin', 'super_admin')
def delete_user(user_id):
    current_user = get_current_user()
    target_user = User.query.get_or_404(user_id)
    
    # Super admin can delete anyone (including admins)
    # Admin can only delete users (not admins or super admins)
    if target_user.role == UserRole.SUPER_ADMIN:
        # Only super admin can delete super admin
        if current_user.role != UserRole.SUPER_ADMIN:
            return jsonify({'error': 'Only super admin can delete super admin'}), 403
    
    # Prevent self-deletion
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(target_user)
    db.session.commit()
```

#### B. Change User Roles
```python
# Only super admin can change roles
@role_required('super_admin')
def update_user_role(user_id):
    # Super admin can promote/demote:
    # - User → Admin
    # - Admin → User
    # - User → Super Admin (careful!)
    # - Admin → Super Admin (careful!)
```

#### C. Manage All Users
- View all users
- Delete any user (except own account)
- Change any user's role
- Activate/deactivate any account

### Protection Rules:
1. **Self-protection**: Cannot delete/change own role/status
2. **Super admin protection**: Only super admin can delete super admin
3. **Admin limitation**: Admin can delete users but not admins/super admins

### Example Scenarios:

**Scenario 1: Super Admin deleting Admin**
```python
# Super Admin (ID: 1) wants to delete Admin (ID: 2)
DELETE /api/auth/users/2
# ✅ Allowed - Super admin can delete admins
```

**Scenario 2: Admin trying to delete Admin**
```python
# Admin (ID: 2) tries to delete another Admin (ID: 3)
DELETE /api/auth/users/3
# ❌ Denied - Admin cannot delete other admins
```

**Scenario 3: Admin deleting User**
```python
# Admin (ID: 2) deletes User (ID: 4)
DELETE /api/auth/users/4
# ✅ Allowed - Admin can delete users
```

---

## Security Best Practices Implemented

1. ✅ **Never store plain text passwords** - Always hashed
2. ✅ **Server-side validation** - Never trust client-side only
3. ✅ **Parameterized queries** - SQLAlchemy ORM prevents SQL injection
4. ✅ **Session security** - Signed, server-side, with expiration
5. ✅ **Role-based access** - Hierarchical permissions
6. ✅ **Input sanitization** - Validation and normalization
7. ✅ **Error messages** - Generic errors don't reveal system details
8. ✅ **Account protection** - Cannot delete/change own account

---

## Additional Security Recommendations for Production

1. **HTTPS**: Always use HTTPS in production
2. **CSRF Protection**: Add Flask-WTF for CSRF tokens
3. **Rate Limiting**: Limit login attempts (e.g., 5 attempts per 15 minutes)
4. **Password Reset**: Implement secure password reset flow
5. **Audit Logging**: Log all admin actions
6. **Two-Factor Authentication**: Add 2FA for admin accounts
7. **Session Security**: Use secure, httpOnly cookies
8. **Database Encryption**: Encrypt sensitive data at rest

