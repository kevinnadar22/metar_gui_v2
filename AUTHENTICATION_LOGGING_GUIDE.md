# Authentication & Logging System - Implementation Guide

## Overview
This document describes the newly implemented authentication system with **Super Admin privileges**, **Tab-scoped JWT authentication**, and **User Activity Logging**.

---

## 1. Tab-Scoped JWT Authentication

### What is Tab-Scoped JWT?
Each browser tab maintains its own unique `tab_id`. JWT tokens are now bound to specific tabs, preventing token reuse across different tabs and enhancing security.

### Implementation Details

#### Backend (auth.py)
```python
def create_token(user, tab_id=None):
    """Create JWT token with tab_id for tab-scoped authentication"""
    payload = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "station": user.station_code,
        "tab_id": tab_id or "default",  # Unique per tab
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
```

#### Frontend (auth.js)
- `TAB_ID` is generated when the page loads and stored in `sessionStorage`
- Every API request includes `X-Tab-ID` header
- Tab ID format: `tab_<random>_<timestamp>`

### Flow
1. User opens app in Tab 1 → `tab_id` = `tab_abc123_1700000000`
2. User logs in → Token created with `tab_id` embedded
3. User opens app in Tab 2 → New `tab_id` = `tab_def456_1700000001`
4. User logs in separately → New token with different `tab_id`
5. **Each tab maintains independent session** - no session leak between tabs

---

## 2. User Activity Logging

### Database Model (models.py)

New `UserActivity` table tracks all user actions:

```python
class UserActivity(db.Model):
    __tablename__ = "user_activities"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # login/logout/access
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    page_or_route = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    tab_id = db.Column(db.String(100), nullable=True)
    details = db.Column(db.Text, nullable=True)
```

### Logged Activities
- **Login**: When user authenticates
- **Logout**: When user ends session
- **Access**: When user navigates to a page (optional - can be expanded)

### Activity Logging Function (auth.py)
```python
def log_activity(user, activity_type, page_or_route=None, tab_id=None, details=None):
    """Log user activity to database"""
```

---

## 3. API Endpoints for Logging

### Admin Endpoints (requires `admin` role)

#### GET `/api/logs/all`
Get all users' activity logs (paginated)

**Parameters:**
- `page` (int, default=1)
- `per_page` (int, default=100)
- `activity_type` (str, optional) - filter by 'login', 'logout', or 'access'

**Response:**
```json
{
    "logs": [
        {
            "id": 1,
            "user_id": 5,
            "username": "VABB",
            "activity_type": "login",
            "timestamp": "2026-01-28T10:30:00",
            "page_or_route": "/auth/login",
            "ip_address": "192.168.1.100",
            "tab_id": "tab_abc123_1700000000",
            "details": null
        }
    ],
    "total": 150,
    "pages": 3,
    "current_page": 1
}
```

#### GET `/api/logs/user/<user_id>`
Get specific user's logs (admin only)

#### GET `/api/logs/stats`
Get activity statistics
- `total_logins`
- `total_logouts`
- `total_accesses`
- `unique_users`
- `active_users_24h`

#### POST `/api/logs/log-access`
Frontend can manually log page access

**Request Body:**
```json
{
    "page": "/index.html"
}
```

### Super Admin Endpoint (requires `super_admin` role)

#### POST `/api/logs/clear`
Clear all activity logs (permanent delete)

---

## 4. Admin Logs Page

### Route
**File:** `/admin_logs.html`

### Features
✅ View all user activity logs
✅ Filter by activity type (login/logout/access)
✅ Search by username
✅ Pagination with adjustable per-page count
✅ Real-time statistics dashboard
✅ Export logs to CSV
✅ Auto-refresh every 30 seconds
✅ Super Admin section to clear all logs

### Statistics Dashboard
- **Total Logins**: Count of all login events
- **Total Logouts**: Count of all logout events
- **Unique Users**: Count of distinct users
- **Active (24h)**: Users active in last 24 hours

### Filter Options
- Activity Type: All / Login / Logout / Page Access
- Username: Search by exact/partial username
- Per Page: 20 / 50 / 100 / 200 entries

### Export to CSV
Downloads all logs as `logs_YYYY-MM-DD.csv` with columns:
- Timestamp
- User
- Activity Type
- Page/Route
- IP Address
- Tab ID

---

## 5. Super Admin Privileges

### Role Hierarchy
```
user (level 1) < admin (level 2) < super_admin (level 3)
```

### Super Admin Capabilities
1. ✅ Manage all admins (create, enable, disable)
2. ✅ Manage all users (create, update, delete)
3. ✅ View all activity logs
4. ✅ **Clear all activity logs** (only super_admin)
5. ✅ Access entire system

### Super Admin Dashboard
**File:** `/superadmin.html`

- Manage Admins panel
- Manage Users panel
- **View Logs button** - Links to `/admin_logs.html`
- **Danger Zone** - Clear all logs functionality

---

## 6. Frontend Integration

### Tab ID Management (auth.js)
```javascript
// Generate unique tab ID
function generateTabId() {
    let tabId = sessionStorage.getItem('tab_id');
    if (!tabId) {
        tabId = 'tab_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        sessionStorage.setItem('tab_id', tabId);
    }
    return tabId;
}
const TAB_ID = generateTabId();
```

### API Call Helper (app.js)
```javascript
function apiFetch(url, options = {}) {
    const headers = options.headers || {};
    headers['X-Tab-ID'] = getTabId();
    return fetch(url, {
        ...options,
        headers,
        credentials: 'include'
    });
}
```

### Updated Login Flow
```javascript
async login(username, password) {
    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-Tab-ID': TAB_ID
        },
        credentials: 'include',
        body: JSON.stringify({ username, password, tab_id: TAB_ID })
    });
    // ...
}
```

---

## 7. Database Setup

### Create Tables
Run this after deployment to initialize the new table:

```bash
python
>>> from app.backend.app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Existing Data
- Existing users are NOT affected
- `UserActivity` table starts fresh
- Previous logins are not logged (logging starts after deployment)

---

## 8. Security Features

### Tab-Scoped JWT
- **Prevents token leakage** across tabs
- **Invalidates token** if tab ID doesn't match
- **Per-tab session management**

### IP Address Tracking
- Logs client IP (supports IPv4 and IPv6)
- Useful for detecting unusual access patterns
- Extractable from X-Forwarded-For header

### Activity Auditing
- **Immutable logs** (only super_admin can delete, requires confirmation)
- **Timestamps** for audit trail
- **Tab ID** for session tracking

---

## 9. Usage Examples

### For Admin Users
1. Navigate to Dashboard (admin.html)
2. Click **"📊 View Logs"** button
3. View all user activities
4. Filter by activity type or user
5. Export logs for reporting
6. Logs auto-refresh every 30 seconds

### For Super Admin Users
1. Navigate to Super Admin Dashboard (superadmin.html)
2. Same logging features as admin
3. Additional **"Danger Zone"** section
4. Click **"🗑️ Clear All Logs"**
5. Confirm twice (security measure)

### For Regular Users
- No direct access to logs
- Activity automatically logged on login/logout
- Admins can view their activity

---

## 10. Configuration

### Environment Variables
No new environment variables required. Uses existing:
- `JWT_SECRET` - for token signing
- Database credentials (SQLite by default)

### Token Expiry
- **8 hours** after login
- Tab ID remains valid until token expires
- Logout clears token immediately

---

## 11. Troubleshooting

### "Tab ID Mismatch" Error
**Problem:** Token validation fails with tab ID mismatch
**Solution:** 
- Clear browser cache/cookies
- Ensure all API calls include `X-Tab-ID` header
- Check `sessionStorage` is not cleared between requests

### Logs Not Appearing
**Problem:** Activity not logged
**Solution:**
- Check database connection
- Verify `UserActivity` table exists
- Check for exceptions in Flask console logs

### Cannot Clear Logs (Super Admin)
**Problem:** Button disabled or not showing
**Solution:**
- Ensure user role is exactly `super_admin`
- Re-login and check `/auth/me` response
- Clear browser cookies and try again

---

## 12. API Request Headers

### Required Headers for All Authenticated Endpoints
```
X-Tab-ID: <tab_id>        # Tab-scoped authentication
Content-Type: application/json
Cookie: auth_token=<jwt>  # Set by browser automatically
```

### Example cURL Request
```bash
curl -X GET http://localhost:5000/api/logs/all \
  -H "X-Tab-ID: tab_abc123_1700000000" \
  -H "Content-Type: application/json" \
  -b "auth_token=eyJ..."
```

---

## 13. Removal of User Self-Logs

✅ **Removed:** `GET /api/logs/my-logs` endpoint
- Users can no longer view their own logs
- Only admins/super_admins can view logs
- Prevents privacy concerns and log tampering

---

## Summary of Changes

### Files Created
- `/app/frontend/admin_logs.html` - Admin logs page
- `/app/frontend/js/admin_logs.js` - Logs frontend logic

### Files Modified
- `/app/backend/models.py` - Added `UserActivity` model
- `/app/backend/auth.py` - Added tab-scoped JWT, logging functions
- `/app/backend/routes/api.py` - Added logging endpoints, removed user self-logs
- `/app/frontend/admin.html` - Added "View Logs" button
- `/app/frontend/superadmin.html` - Added "View Logs" button
- `/app/frontend/js/auth.js` - Added tab ID management
- `/app/frontend/js/app.js` - Added `apiFetch()` helper

### Database
- New table: `user_activities`
- Foreign key constraint to `users` table

---

## Next Steps

1. ✅ Deploy to server
2. ✅ Run database migrations (`db.create_all()`)
3. ✅ Test login/logout logging
4. ✅ Test admin logs page
5. ✅ Test tab-scoped authentication (open in 2 tabs)
6. ✅ Verify super admin clear logs functionality
7. ✅ Export logs and verify CSV format
8. ✅ Monitor logs for any issues

---

**Implementation Date:** January 28, 2026
**Version:** 2.0 - Authentication & Logging System
