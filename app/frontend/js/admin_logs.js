const TAB_ID = sessionStorage.getItem('tab_id') || (sessionStorage.setItem('tab_id', generateTabId()), sessionStorage.getItem('tab_id'));

function generateTabId() {
    return 'tab_' + Math.random().toString(36).substr(2, 9);
}

let currentPage = 1;
let totalPages = 1;
let currentUserRole = 'admin';
let currentUser = null;

async function init() {
    try {
        const meRes = await fetch('/auth/me', {
            method: 'GET',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!meRes.ok) {
            window.location.href = '/login.html';
            return;
        }

        const meData = await meRes.json();
        currentUser = meData.user;
        currentUserRole = meData.user.role;
        
        if (currentUserRole !== 'admin' && currentUserRole !== 'super_admin') {
            alert('Access Denied: Only Admins can view logs');
            window.location.href = '/index.html';
            return;
        }

        document.getElementById('username').textContent = `👤 ${meData.user.username} (${meData.user.role})`;

        if (currentUserRole === 'super_admin') {
            document.getElementById('superAdminSection').classList.remove('hidden');
            document.getElementById('userFilterDiv').style.display = 'block';
            await loadUsersForFilter();
        }

        await loadStats();
        await loadLogs();
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Error loading page. Please refresh.');
    }
}

async function loadUsersForFilter() {
    try {
        const res = await fetch('/api/logs/users-list', {
            method: 'GET',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!res.ok) return;
        
        const data = await res.json();
        const userFilter = document.getElementById('userFilter');
        
        data.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.username} (${user.station})`;
            userFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading users list:', error);
    }
}

function convertToIST(utcTimestamp) {
    const date = new Date(utcTimestamp);
    const istTime = new Date(date.getTime() + 5.5 * 60 * 60 * 1000);
    return istTime.toLocaleString('en-IN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Kolkata'
    });
}

async function loadStats() {
    try {
        const res = await fetch('/api/logs/stats', {
            method: 'GET',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!res.ok) throw new Error('Failed to fetch stats');
        
        const stats = await res.json();
        
        document.getElementById('stat-logins').textContent = stats.total_logins;
        document.getElementById('stat-logouts').textContent = stats.total_logouts;
        document.getElementById('stat-users').textContent = stats.unique_users;
        document.getElementById('stat-active').textContent = stats.active_users_24h;
    } catch (error) {
        console.error('Error loading stats:', error);
        showAlert('Failed to load statistics', 'error');
    }
}

async function loadLogs() {
    try {
        const perPage = document.getElementById('perPageSelect').value || 50;
        const activityType = document.getElementById('activityTypeFilter').value;
        const userId = document.getElementById('userFilter') ? document.getElementById('userFilter').value : '';
        
        let url = `/api/logs/all?page=${currentPage}&per_page=${perPage}`;
        if (activityType) {
            url += `&activity_type=${activityType}`;
        }
        if (userId && currentUserRole === 'super_admin') {
            url += `&user_id=${userId}`;
        }

        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!res.ok) throw new Error('Failed to fetch logs');
        
        const data = await res.json();
        totalPages = data.pages;

        renderLogsTable(data.logs);
        updatePagination(data);
    } catch (error) {
        console.error('Error loading logs:', error);
        showAlert('Failed to load logs', 'error');
    }
}

function renderLogsTable(logs) {
    const tbody = document.getElementById('logsTableBody');
    
    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-4 text-center text-gray-500">No logs found</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr class="log-entry border-b border-gray-200 hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-900">${convertToIST(log.timestamp)}</td>
            <td class="px-6 py-4 text-sm">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded">${log.username}</span>
            </td>
            <td class="px-6 py-4 text-sm">
                <span class="${getActivityBadgeClass(log.activity_type)}">${log.activity_type.toUpperCase()}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">${log.page_or_route || '—'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate" title="${log.details || ''}">${log.details || '—'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono text-xs">${log.ip_address || '—'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 font-mono text-xs">${log.tab_id || '—'}</td>
        </tr>
    `).join('');
}

function getActivityBadgeClass(type) {
    switch(type) {
        case 'login':
            return 'px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium';
        case 'logout':
            return 'px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium';
        case 'access':
            return 'px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium';
        case 'verification':
            return 'px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium';
        default:
            return 'px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs font-medium';
    }
}

function formatDate(timestamp) {
    return convertToIST(timestamp);
}

function updatePagination(data) {
    document.getElementById('logsInfo').textContent = 
        `Showing ${(data.current_page - 1) * data.logs.length + 1}-${(data.current_page - 1) * data.logs.length + data.logs.length} of ${data.total} logs`;

    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            pageNumbers.innerHTML += `<span class="px-2 py-1 bg-blue-600 text-white rounded">${i}</span>`;
        } else if (i <= 5 || (i > totalPages - 5)) {
            pageNumbers.innerHTML += `<button onclick="goToPage(${i})" class="px-2 py-1 text-sm text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50">${i}</button>`;
        } else if (i === 6 && totalPages > 10) {
            pageNumbers.innerHTML += '<span class="px-2 py-1">...</span>';
        }
    }
}

function filterLogs() {
    currentPage = 1;
    loadLogs();
}

function clearFilters() {
    document.getElementById('activityTypeFilter').value = '';
    document.getElementById('usernameFilter').value = '';
    currentPage = 1;
    loadLogs();
}

function goToPage(page) {
    currentPage = page;
    loadLogs();
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadLogs();
    }
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadLogs();
    }
}

async function exportLogs() {
    try {
        showAlert('Preparing export...', 'info');
        
        const perPage = 10000; 
        let url = `/api/logs/all?page=1&per_page=${perPage}`;
        
        const activityType = document.getElementById('activityTypeFilter').value;
        if (activityType) {
            url += `&activity_type=${activityType}`;
        }

        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!res.ok) throw new Error('Failed to fetch logs');
        
        const data = await res.json();
        
        let csv = 'Timestamp,User,Activity Type,Page/Route,IP Address,Tab ID\n';
        data.logs.forEach(log => {
            csv += `"${log.timestamp}","${log.username}","${log.activity_type}","${log.page_or_route || ''}","${log.ip_address || ''}","${log.tab_id || ''}"\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url_link = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url_link;
        a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url_link);
        document.body.removeChild(a);

        showAlert('Logs exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showAlert('Failed to export logs', 'error');
    }
}

async function clearAllLogs() {
    if (currentUserRole !== 'super_admin') {
        showAlert('Only Super Admins can clear logs', 'error');
        return;
    }

    const confirmed = confirm('WARNING: This will permanently delete ALL activity logs. Are you sure?');
    if (!confirmed) return;

    const doubleConfirm = prompt('Type "DELETE ALL LOGS" to confirm:');
    if (doubleConfirm !== 'DELETE ALL LOGS') {
        showAlert('Clear cancelled', 'info');
        return;
    }

    try {
        const res = await fetch('/api/logs/clear', {
            method: 'POST',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!res.ok) throw new Error('Failed to clear logs');
        
        showAlert('All logs cleared successfully!', 'success');
        currentPage = 1;
        await loadStats();
        await loadLogs();
    } catch (error) {
        console.error('Clear error:', error);
        showAlert('Failed to clear logs', 'error');
    }
}

function goBack() {
    if (currentUserRole === 'super_admin') {
        window.location.href = '/superadmin.html';
    } else {
        window.location.href = '/admin.html';
    }
}

async function logout() {
    try {
        await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'X-Tab-ID': TAB_ID,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login.html';
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-100' : type === 'error' ? 'bg-red-100' : 'bg-blue-100';
    const textColor = type === 'success' ? 'text-green-800' : type === 'error' ? 'text-red-800' : 'text-blue-800';
    
    alertDiv.className = `fixed top-4 right-4 px-6 py-3 rounded-md ${bgColor} ${textColor} shadow-lg z-50`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', init);

setInterval(loadLogs, 30000);
