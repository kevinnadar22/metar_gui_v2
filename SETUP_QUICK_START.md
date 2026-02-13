# Quick Setup Guide - Authentication & Logging System

## 🚀 5-Minute Setup

### Step 1: Database Setup (30 seconds)
```bash
python
>>> from app.backend.app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Step 2: Restart Flask Server (10 seconds)
```bash
# Kill current Flask process
# Restart with:
python app/backend/app.py
```

### Step 3: Test Login (2 minutes)
1. Open browser → `http://localhost:5000/login.html`
2. Enter credentials
3. Should see dashboard (no auth errors)
4. Check console → No "Tab ID mismatch" messages

### Step 4: Test Logs (2 minutes)
1. Login as admin user
2. Click "📊 View Logs" button
3. Should see all activity logs
4. Try filters and export

---

## ✅ Verification Checklist

- [ ] Can login successfully
- [ ] No auth errors in console
- [ ] Admin sees "View Logs" button
- [ ] Logs page loads and shows data
- [ ] Statistics cards display numbers
- [ ] Can filter by activity type
- [ ] Can export to CSV
- [ ] Multiple tabs work independently

---

## 🔐 What Changed for Users

### Regular Users
- ✅ Login works same as before
- ✅ Session now per-tab (each tab independent)
- ⚠️ F5 refresh = auto-logout (by design)

### Admin Users
- ✅ New "📊 View Logs" button on dashboard
- ✅ Can view all user activity logs
- ✅ Can filter and export logs

### Super Admin Users
- ✅ All admin features +
- ✅ Can clear all logs (danger zone)
- ✅ Full system control

---

## 🐛 If You See "Tab ID Mismatch" Error

### Quick Fix (2 steps)
1. Clear cookies: `Cmd+Shift+Del` (or Ctrl+Shift+Del on Windows)
2. Refresh page: `Cmd+R` (or Ctrl+R on Windows)
3. Login again

### Detailed Fix
- Clear all browser cache
- Close all browser tabs
- Restart browser
- Open app fresh

---

## 📊 Where to Access Logs

### For Admin
1. Login with admin account
2. See admin dashboard
3. Click purple "📊 View Logs" button
4. URL: `/admin_logs.html`

### For Super Admin
1. Login with super_admin account
2. See super admin dashboard
3. Click purple "📊 View Logs" button
4. URL: `/admin_logs.html`
5. Scroll down for "Danger Zone" section

---

## 📝 Log File Location

Database: `instance/auth_test.db` (SQLite)

View logs directly:
```bash
sqlite3 instance/auth_test.db
> SELECT * FROM user_activities ORDER BY timestamp DESC LIMIT 10;
```

---

## 🔧 Configuration

### Auto-refresh Interval
Edit `/app/frontend/js/admin_logs.js` line ~343:
```javascript
// Refresh every 30 seconds
setInterval(loadLogs, 30000);  // Change 30000 to new milliseconds
```

### Per-Page Options
Edit `/app/frontend/admin_logs.html` line ~63:
```html
<option value="20">20 entries</option>
<option value="50" selected>50 entries</option>
<!-- Add more options here -->
```

### Token Expiry
Edit `/app/backend/auth.py` line ~41:
```python
"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)  # Change 8 to new hours
```

---

## 🧪 Test Commands

### Login Test
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tab-ID: tab_test123" \
  -b "auth_token=" \
  -d '{"username":"VABB","password":"password123","tab_id":"tab_test123"}'
```

### Get Logs Test
```bash
curl -X GET "http://localhost:5000/api/logs/all?page=1&per_page=10" \
  -H "X-Tab-ID: tab_test123" \
  -b "auth_token=<your_token_here>"
```

### Get Stats Test
```bash
curl -X GET http://localhost:5000/api/logs/stats \
  -H "X-Tab-ID: tab_test123" \
  -b "auth_token=<your_token_here>"
```

---

## 📱 Browser DevTools Check

### Check Tab ID
Open browser console → paste:
```javascript
console.log('Current Tab ID:', sessionStorage.getItem('tab_id'));
```

### Monitor API Calls
1. Open DevTools (F12)
2. Go to Network tab
3. Make any API call
4. Check request headers → Should see `X-Tab-ID: tab_xxx`

### Check Token
```javascript
// In console, paste:
document.cookie.split('; ').find(c => c.startsWith('auth_token='))
```

---

## 🎯 Next Steps

1. ✅ Deploy to production
2. ✅ Run database setup
3. ✅ Test in multiple browsers
4. ✅ Monitor logs for errors
5. ✅ Backup database regularly

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Login again, clear cookies |
| Tab ID mismatch | Refresh browser, clear cache |
| Logs not showing | Restart Flask, check DB |
| Can't export CSV | Ensure logs exist, check permissions |
| Super admin can't clear logs | Verify user role = "super_admin" |

---

## 🔍 System Check

Run this to verify everything is working:
```bash
python -c "
from app.backend.app import app, db
from app.backend.models import User, UserActivity
with app.app_context():
    users = User.query.count()
    activities = UserActivity.query.count()
    print(f'✓ Database connected')
    print(f'✓ Users in DB: {users}')
    print(f'✓ Activities logged: {activities}')
    print(f'✓ System ready!')
"
```

---

## 💡 Pro Tips

1. **Check logs regularly** - Use CSV export for reports
2. **Monitor active users** - Statistics show 24h activity
3. **Archive old logs** - Export before clearing
4. **Test new tabs** - Each tab gets independent session
5. **Password reset** - Users can change via admin panel

---

## 📞 Support

For issues:
1. Check Flask console for errors
2. Review browser console (F12)
3. Check `AUTHENTICATION_LOGGING_GUIDE.md`
4. Review `TABID_MISMATCH_FIX.md` for tab issues
5. Check `AUTHENTICATION_QUICK_REFERENCE.md` for common fixes

---

**Version:** 2.0  
**Date:** January 28, 2026  
**Status:** Ready for Production ✅

---

## Final Checklist Before Deployment

- [ ] Database migrations run successfully
- [ ] No errors in Flask console
- [ ] Admin logs page accessible
- [ ] Test login in 2 different tabs
- [ ] Both tabs work independently
- [ ] CSV export works
- [ ] Statistics update correctly
- [ ] No "Tab ID mismatch" errors in console
- [ ] Backup of existing database created
- [ ] Team notified of changes

**All systems GO! 🚀**
