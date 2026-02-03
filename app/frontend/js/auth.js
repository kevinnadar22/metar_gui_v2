function generateTabId() {
    let tabId = sessionStorage.getItem('tab_id');
    if (!tabId) {
        tabId = 'tab_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        sessionStorage.setItem('tab_id', tabId);
    }
    return tabId;
}

const TAB_ID = generateTabId();

class AuthManager {
    constructor() {
        this.user = null;
        this.ready = this.init();
    }

    async init() {
        // Check if this is a new tab (first time loading in this session)
        const previousTabId = localStorage.getItem('last_tab_id');
        
        // If this is a new tab (different from previous tab), clear old session
        if (previousTabId && previousTabId !== TAB_ID) {
            // New tab detected - clear old token to get fresh one
            document.cookie = "auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        }
        localStorage.setItem('last_tab_id', TAB_ID);
        
        // Force logout on full page reload (user requested behavior)
        try {
            const navEntries = (performance.getEntriesByType && performance.getEntriesByType('navigation')) || [];
            const nav = navEntries[0] || null;
            const isReload = nav ? nav.type === 'reload' : (performance.navigation && performance.navigation.type === 1);
            if (isReload) {
                await fetch('/auth/logout', { method: 'POST', credentials: 'include', headers: { 'X-Tab-ID': TAB_ID } });
                window.location.href = '/login';
                return;
            }
        } catch (e) {
            // ignore; continue to auth check
        }

        await this.checkAuth();
    }

    async checkAuth() {
        try {
            const response = await fetch('/auth/me', {
                credentials: 'include',
                headers: {
                    'X-Tab-ID': TAB_ID,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.user = data.user;
                this.updateUI();
                this.routeByRole();
                return true;
            } else {
                this.user = null;
                this.handleUnauthorized();
                return false;
            }
        } catch (err) {
            console.error('Auth check failed:', err);
            this.user = null;
            this.handleUnauthorized();
            return false;
        }
    }

    async login(username, password) {
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Tab-ID': TAB_ID
                },
                credentials: 'include',
                body: JSON.stringify({ username, password, tab_id: TAB_ID })
            });

            const data = await response.json();

            if (!response.ok) {
                return { success: false, error: data.error || 'Login failed' };
            }

            // After login, fetch user info
            await this.checkAuth();
            return { success: true };

        } catch (err) {
            return { success: false, error: 'Network error' };
        }
    }

    async logout() {
        try {
            await fetch('/auth/logout', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-Tab-ID': TAB_ID,
                    'Content-Type': 'application/json'
                }
            });
        } finally {
            this.user = null;
            // clear any client-side storage if needed
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
    }

    isAuthenticated() {
        return !!this.user;
    }

    hasRole(role) {
        if (!this.user) return false;

        const hierarchy = {
            user: 1,
            admin: 2,
            super_admin: 3
        };

        return hierarchy[this.user.role] >= hierarchy[role];
    }

    isAdmin() {
        return this.hasRole('admin');
    }

    isSuperAdmin() {
        return this.hasRole('super_admin');
    }

    updateUI() {
        const userInfo = document.getElementById('userInfo');
        const logoutBtn = document.getElementById('logoutBtn');
        const userRoleEl = document.getElementById('userRole');
        const avatarEl = document.getElementById('userAvatar');

        if (this.user) {
            if (userInfo) {
                userInfo.textContent = this.user.username;
                userInfo.style.display = 'inline';
            }
            if (userRoleEl) {
                userRoleEl.textContent = this.user.role;
            }
            if (avatarEl) {
                // show first letter as avatar fallback
                avatarEl.textContent = (this.user.username || 'U').charAt(0).toUpperCase();
            }
            if (logoutBtn) logoutBtn.style.display = 'inline';
        } else {
            if (userInfo) userInfo.style.display = 'none';
            if (userRoleEl) userRoleEl.textContent = '';
            if (avatarEl) avatarEl.textContent = '';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }

routeByRole() {
    if (!this.user) return;

    const path = window.location.pathname;

    if (this.user.role === 'super_admin') {
        if (path !== '/superadmin') {
            window.location.replace('/superadmin');
        }
    } else if (this.user.role === 'admin') {
        if (path !== '/admin') {
            window.location.replace('/admin');
        }
    } else if (this.user.role === 'user') {
        if (path !== '/') {
            window.location.replace('/');
        }
    }
}


    handleUnauthorized() {
        const path = window.location.pathname;
        if (path !== '/login' && path !== '/signup') {
            window.location.href = '/login';
        }
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    }

    requireRole(role) {
        if (!this.requireAuth()) return false;

        if (!this.hasRole(role)) {
            alert('Access denied');
            window.location.href = '/';
            return false;
        }
        return true;
    }
}

const authManager = new AuthManager();
window.authManager = authManager;