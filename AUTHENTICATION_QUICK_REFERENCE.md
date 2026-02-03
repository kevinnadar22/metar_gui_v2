# Quick Reference: Authentication & Logging System

## 🔐 Tab-Scoped JWT Authentication

### What Changed?
- Each browser tab has unique session
- Tokens bound to specific tab IDs
- Prevents token sharing between tabs

### How It Works
```
Tab 1: token with tab_id_123 ✓
Tab 2: token with tab_id_456 ✓
Tab 1 uses Tab 2's token: ✗ BLOCKED
```

---

## 📊 User Activity Logs

### What Gets Logged?
✓ Login event (username, IP, timestamp, tab_id)
✓ Logout event (username, IP, timestamp, tab_id)
✓ Page access (optional)

### Who Can View?
- **Admin**: View all user logs
- **Super Admin**: View all logs + clear them
- **User**: No access to logs

---

## 🚀 API Endpoints

### Admin Access
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/logs/all` | GET | All user activity logs |
| `/api/logs/user/<id>` | GET | Specific user's logs |
| `/api/logs/stats` | GET | Activity statistics |
| `/api/logs/log-access` | POST | Manual page access log |

### Super Admin Only
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/logs/clear` | POST | Delete all logs (permanent) |

---

## 🎯 Admin Dashboard Features

**Navigate to:** `/admin_logs.html` (click "View Logs" button)

### Statistics
- Total Logins
- Total Logouts  
- Unique Users
- Active Users (24h)

### Filters
- Activity Type dropdown
- Username search
- Per-page count selector

### Actions
- View paginated logs
- Export to CSV
- Auto-refresh every 30s

---

## 🛡️ Super Admin Features

**Navigate to:** `/superadmin.html` → Click "View Logs"

### Extra Capability
- **Danger Zone** section
- **Clear All Logs** button
- Requires double confirmation + typed confirmation

---

## 🔧 Frontend Integration

### Every API call now includes:
```javascript
Headers: {
    'X-Tab-ID': <generated_tab_id>,
    'Content-Type': 'application/json'
}
```

### Login now sends:
```json
{
    "username": "VABB",
    "password": "password123",
    "tab_id": "tab_abc123_1700000000"
}
```

---

## 📋 Database Schema

### UserActivity Table
```
id (INT) - Primary key
user_id (INT FK) - User reference
activity_type (VARCHAR) - login/logout/access
timestamp (DATETIME) - When occurred
page_or_route (VARCHAR) - Which page/API
ip_address (VARCHAR) - Client IP
tab_id (VARCHAR) - Browser tab identifier
details (TEXT) - Extra metadata
```

---

## 🚨 Important Notes

### Removed Feature
❌ Removed: User self-logs endpoint (`/api/logs/my-logs`)
- Users can no longer view their own activity
- Only admins/super_admins can see logs

### Session Management
- Each tab: Independent session
- Closing tab: Tab ID becomes invalid
- Across devices: Different session per device

### Token Expiry
- **8 hours** from login
- **Tab ID** embedded in token
- Auto-logout after expiry

---

## 🔍 Testing Checklist

- [ ] Login and see activity logged
- [ ] Open app in Tab 2 - separate session
- [ ] Logout and see logout logged
- [ ] Admin views logs successfully
- [ ] Filter by activity type works
- [ ] Export to CSV works
- [ ] Super admin can clear logs
- [ ] Statistics update correctly
- [ ] Logs auto-refresh every 30s

---

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| "Unauthorized" on logs page | Ensure admin/super_admin role |
| Tab ID mismatch error | Clear cookies, re-login |
| Logs not appearing | Check database connection |
| Can't clear logs | Ensure super_admin role |
| Export button disabled | Ensure logs exist |

---

## 📞 Support

For issues, check:
1. Flask console for errors
2. Browser console for JS errors
3. Database connection
4. User role in database

---

**Version:** 2.0 | **Date:** January 28, 2026
