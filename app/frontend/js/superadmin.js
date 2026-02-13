async function loadAdmins() {
    try {
        const res = await fetch('/auth/admins', { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to load admins');
        
        const admins = await res.json();
        const container = document.getElementById('adminList');
        container.innerHTML = '';

        if (!admins || admins.length === 0) {
            container.innerHTML = '<p class="text-gray-500 py-8 text-center">No admins found</p>';
            return;
        }

        admins.forEach(a => {
            container.innerHTML += `
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 flex justify-between items-center">
                <div>
                  <p class="font-semibold text-gray-800">${a.username}</p>
                  <p class="text-xs text-gray-500">${a.role}</p>
                  <p class="text-xs ${a.active ? 'text-green-600' : 'text-red-600'} font-medium">
                    ${a.active ? '✓ Active' : '✗ Disabled'}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button onclick="toggleAdminStatus(${a.id}, ${!a.active})" 
                    class="px-3 py-1 text-xs font-medium rounded ${a.active ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' : 'bg-green-100 text-green-700 hover:bg-green-200'}">
                    ${a.active ? 'Disable' : 'Enable'}
                  </button>
                  <button onclick="deleteAdmin(${a.id})"
                    class="px-3 py-1 text-xs font-medium bg-red-100 text-red-700 hover:bg-red-200 rounded">
                    Delete
                  </button>
                </div>
              </div>
            `;
        });
    } catch (err) {
        const container = document.getElementById('adminList');
        container.innerHTML = `<p class="text-red-600 py-8 text-center">${err.message}</p>`;
    }
}

async function loadUsers() {
    try {
        const res = await fetch('/auth/users', { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to load users');
        
        const users = await res.json();
        const container = document.getElementById('userList');
        container.innerHTML = '';

        if (!users || users.length === 0) {
            container.innerHTML = '<p class="text-gray-500 py-8 text-center">No users found</p>';
            return;
        }

        users.forEach(u => {
            container.innerHTML += `
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 flex justify-between items-center">
                <div>
                  <p class="font-semibold text-gray-800">${u.username}</p>
                  <p class="text-xs text-gray-500">Station: ${u.station}</p>
                  <p class="text-xs ${u.active ? 'text-green-600' : 'text-red-600'} font-medium">
                    ${u.active ? '✓ Active' : '✗ Disabled'}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button onclick="toggleUserStatus(${u.id}, ${!u.active})" 
                    class="px-3 py-1 text-xs font-medium rounded ${u.active ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' : 'bg-green-100 text-green-700 hover:bg-green-200'}">
                    ${u.active ? 'Disable' : 'Enable'}
                  </button>
                  <button onclick="deleteUser(${u.id})"
                    class="px-3 py-1 text-xs font-medium bg-red-100 text-red-700 hover:bg-red-200 rounded">
                    Delete
                  </button>
                </div>
              </div>
            `;
        });
    } catch (err) {
        const container = document.getElementById('userList');
        container.innerHTML = `<p class="text-red-600 py-8 text-center">${err.message}</p>`;
    }
}

async function toggleAdminStatus(id, isActive) {
    try {
        const res = await fetch(`/auth/admins/${id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: isActive })
        });

        if (res.ok) {
            showAlert(isActive ? 'Admin enabled' : 'Admin disabled', 'success');
            loadAdmins();
        } else {
            showAlert('Failed to update admin', 'error');
        }
    } catch (err) {
        showAlert('Network error', 'error');
    }
}

async function toggleUserStatus(id, isActive) {
    try {
        const res = await fetch(`/auth/users/${id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: isActive })
        });

        if (res.ok) {
            showAlert(isActive ? 'User enabled' : 'User disabled', 'success');
            loadUsers();
        } else {
            showAlert('Failed to update user', 'error');
        }
    } catch (err) {
        showAlert('Network error', 'error');
    }
}

async function deleteAdmin(id) {
    if (!confirm('Are you sure you want to delete this admin?')) return;

    try {
        const res = await fetch(`/auth/remove/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (res.ok) {
            showAlert('Admin deleted successfully', 'success');
            loadAdmins();
        } else {
            showAlert('Failed to delete admin', 'error');
        }
    } catch (err) {
        showAlert('Network error', 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
        const res = await fetch(`/auth/remove/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (res.ok) {
            showAlert('User deleted successfully', 'success');
            loadUsers();
        } else {
            showAlert('Failed to delete user', 'error');
        }
    } catch (err) {
        showAlert('Network error', 'error');
    }
}

function showAlert(message, type) {
    const alertBox = document.getElementById('alertBox');
    if (alertBox) {
        alertBox.textContent = message;
        alertBox.className = `${type === 'success' ? 'bg-green-500' : 'bg-red-500'} fixed top-4 right-4 p-4 rounded-md shadow-md text-white max-w-sm z-40`;
        alertBox.classList.remove('hidden');
        setTimeout(() => alertBox.classList.add('hidden'), 3000);
    }
}

// Wait for auth to finish before initial load
if (window.authManager && window.authManager.ready) {
    window.authManager.ready.then(() => {
        authManager.requireRole('super_admin');
        if (authManager.user) {
            const avatar = document.getElementById('userAvatar');
            const info = document.getElementById('userInfo');
            const dropdown = document.getElementById('userInfoDropdown');
            if (avatar) avatar.textContent = authManager.user.username.charAt(0).toUpperCase();
            if (info) { info.textContent = authManager.user.username; info.style.display = 'inline'; }
            if (dropdown) dropdown.textContent = authManager.user.username;
        }
        loadAdmins();
        loadUsers();
    }).catch(() => {});
} else {
    loadAdmins();
    loadUsers();
}