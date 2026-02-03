// DOM Elements
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalForm = document.getElementById('modalForm');
const addAdminBtn = document.getElementById('addAdminBtn');
const addUserBtn = document.getElementById('addUserBtn');
const notification = document.getElementById('notification');
const adminCardsContainer = document.querySelector('.admin-section .cards-container');
const userCardsContainer = document.querySelector('.user-section .cards-container');
const backBtn = document.getElementById('backBtn');

// Profile Dropdown Elements
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');
const logoutBtn = document.getElementById('logoutBtn');
const headerLogsBtn = document.getElementById('headerLogsBtn');

let currentMode = ''; // 'admin' or 'user'

// Event Listeners
addAdminBtn?.addEventListener('click', () => openModal('admin'));
addUserBtn?.addEventListener('click', () => openModal('user'));
modalForm?.addEventListener('submit', handleFormSubmit);

// Profile Dropdown Toggle
profileBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (profileDropdown) profileDropdown.classList.toggle('show');
    profileBtn.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest || !e.target.closest('.user-profile-wrapper')) {
        if (profileDropdown) profileDropdown.classList.remove('show');
        if (profileBtn) profileBtn.classList.remove('active');
    }
});

// Logout Button
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        window.location.href = 'login.html';
    });
}

// Header Logs Button
headerLogsBtn?.addEventListener('click', (e) => {
    // Determine which dashboard label we're on and pass as 'from' param
    const sub = document.querySelector('.header .header-text p')?.textContent || '';
    let from = 'super_admin';
    if (/\bADMIN\b/i.test(sub) && !/SUPER/i.test(sub)) from = 'admin';
    // navigate with query param so user_log can show correct subheading
    window.location.href = `user_log.html?from=${from}`;
});

// Back button: navigate to origin specified in query param, fallback to history
backBtn?.addEventListener('click', () => {
    try {
        const params = new URLSearchParams(window.location.search);
        const from = params.get('from');
        if (from === 'admin') {
            window.location.href = 'admin.html';
            return;
        }
        if (from === 'super_admin') {
            window.location.href = 'super_admin.html';
            return;
        }
    } catch (err) {}
    // fallback
    if (window.history.length > 1) window.history.back(); else window.location.href = 'super_admin.html';
});

// Open Modal
function openModal(mode) {
    currentMode = mode;
    modalTitle.textContent = mode === 'admin' ? 'Add Admin' : 'Add User';
    document.getElementById('station').placeholder = mode === 'admin' ? 'Leave blank for Admin role' : 'e.g., VADD, VABB';
    modalForm.reset();
    modal.classList.add('show');
}

// Close Modal
function closeModal() {
    modal.classList.remove('show');
    currentMode = '';
}

// Handle Form Submission
function handleFormSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const station = document.getElementById('station').value.trim();

    if (!name) {
        showNotification('Please enter a name', 'error');
        return;
    }

    // Create new card
    const newCard = createCard(name, station || (currentMode === 'admin' ? 'Admin' : 'Station'));
    
    // Add to appropriate container
    if (currentMode === 'admin') {
        adminCardsContainer.appendChild(newCard);
    } else {
        userCardsContainer.appendChild(newCard);
    }

    // Close modal and show notification
    closeModal();
    showNotification(`${currentMode === 'admin' ? 'Admin' : 'User'} "${name}" added successfully!`);
}

// Create Card Element
function createCard(name, subtitle) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <div class="card-header">
            <h3>${name}</h3>
            <p class="card-subtitle">${subtitle}</p>
        </div>
        <div class="card-status">
            <span class="status-indicator active"></span>
            <span class="status-text">Active</span>
        </div>
        <div class="card-actions">
            <button class="btn-action btn-disable" onclick="toggleDisable(this)">Disable</button>
            <button class="btn-action btn-delete" onclick="deleteItem(this)">Delete</button>
        </div>
    `;
    return card;
}

// Toggle Disable/Enable
function toggleDisable(button) {
    const card = button.closest('.card');
    const statusIndicator = card.querySelector('.status-indicator');
    const statusText = card.querySelector('.status-text');

    const isActive = statusIndicator.classList.contains('active');

    if (isActive) {
        // Disable
        statusIndicator.classList.remove('active');
        statusIndicator.classList.add('disabled');
        statusText.textContent = 'Disabled';
        button.textContent = 'Enable';
        card.style.opacity = '0.6';
        showNotification('Item disabled', 'success');
    } else {
        // Enable
        statusIndicator.classList.add('active');
        statusIndicator.classList.remove('disabled');
        statusText.textContent = 'Active';
        button.textContent = 'Disable';
        card.style.opacity = '1';
        showNotification('Item enabled', 'success');
    }
}

// Delete Item
function deleteItem(button) {
    if (confirm('Are you sure you want to delete this item?')) {
        const card = button.closest('.card');
        const name = card.querySelector('.card-header h3').textContent;
        
        card.style.animation = 'slideUp 0.3s ease forwards';
        card.style.animationDirection = 'reverse';
        
        setTimeout(() => {
            card.remove();
            showNotification(`"${name}" deleted successfully`, 'success');
        }, 300);
    }
}

// Show Notification
function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = 'notification show';
    
    if (type === 'error') {
        notification.classList.add('error');
    }

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (modal && e.target === modal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
        closeModal();
    }
});

console.log('Dashboard initialized successfully!');

// If on user_log.html, update the header subtext based on query param
(function(){
    const headerRoleSub = document.getElementById('headerRoleSub');
    if (!headerRoleSub) return;
    const params = new URLSearchParams(window.location.search);
    const from = params.get('from');
    if (from === 'admin') headerRoleSub.textContent = 'ADMIN DASHBOARD';
    else if (from === 'super_admin') headerRoleSub.textContent = 'SUPER ADMIN DASHBOARD';
})();

/* ==========================
     User Log page logic (merged from user_log.js)
     Runs only when the User Log DOM exists.
     ========================== */
(function(){
    const logsBody = document.getElementById('logsBody');
    if (!logsBody) return; // not on logs page

    const selectAll = document.getElementById('selectAll');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const exportBtn = document.getElementById('exportBtn');
    const filtersBtn = document.getElementById('filtersBtn');
    const searchInput = document.getElementById('searchInput');

    // Create some dummy log entries
    const dummyLogs = [];
    for (let i = 1; i <= 14; i++) {
        dummyLogs.push({
            id: i,
            user: `User_${i}`,
            station: ['VADD','VABB','VOCL'][i % 3],
            action: ['Login','Logout','Edit Profile','Reset Password'][i % 4],
            time: new Date(Date.now() - i * 3600 * 1000).toLocaleString(),
            status: i % 3 === 0 ? 'Inactive' : 'Active'
        });
    }

    let currentFilters = { station: 'All', status: 'All' };

    function getFilteredLogs() {
        const q = (searchInput?.value || '').trim().toLowerCase();
        return dummyLogs.filter(d => {
            if (currentFilters.station !== 'All' && d.station !== currentFilters.station) return false;
            if (currentFilters.status !== 'All' && d.status !== currentFilters.status) return false;
            if (q) {
                return d.user.toLowerCase().includes(q) || d.station.toLowerCase().includes(q) || d.action.toLowerCase().includes(q);
            }
            return true;
        });
    }

    function renderLogs(list = getFilteredLogs()) {
        logsBody.innerHTML = '';
        list.forEach(l => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="padding:12px 8px;"><input type=\"checkbox\" class=\"row-check\" data-id=\"${l.id}\"></td>
                <td style="padding:12px 8px; font-weight:500;">${l.user}</td>
                <td style="padding:12px 8px; color:#667085;">${l.station}</td>
                <td style="padding:12px 8px; color:#667085;">${l.action}</td>
                <td style="padding:12px 8px; color:#667085;">${l.time}</td>
                <td style="padding:12px 8px;"><span class=\"status-pill ${l.status==='Active'?'active':'inactive'}\">${l.status}</span></td>
            `;
            logsBody.appendChild(tr);
        });
    }

    renderLogs();

    selectAll?.addEventListener('change', (e) => {
        document.querySelectorAll('.row-check').forEach(cb => cb.checked = e.target.checked);
    });

    deleteSelectedBtn?.addEventListener('click', () => {
        const selected = Array.from(document.querySelectorAll('.row-check:checked')).map(n => parseInt(n.dataset.id));
        if (!selected.length) { alert('Select rows to delete'); return; }
        if (!confirm(`Delete ${selected.length} selected log(s)?`)) return;
        for (const id of selected) {
            const idx = dummyLogs.findIndex(d => d.id === id);
            if (idx >= 0) dummyLogs.splice(idx,1);
        }
        if (selectAll) selectAll.checked = false;
        renderLogs();
    });

    exportBtn?.addEventListener('click', () => {
        // export currently filtered rows as CSV
        const exportRows = getFilteredLogs();
        const rows = [ ['User','Station','Action','Timestamp','Status'], ...exportRows.map(d=>[d.user,d.station,d.action,d.time,d.status]) ];
        const csv = rows.map(r => r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(',')).join('\n');
        const blob = new Blob([csv], {type:'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'user_logs.csv'; a.click();
        URL.revokeObjectURL(url);
    });

    filtersBtn?.addEventListener('click', () => { openFiltersModal(); });

    searchInput?.addEventListener('input', (e) => { renderLogs(); });

    // simple status pill styles injection (in case styles.css lacks them)
    const style = document.createElement('style');
    style.textContent = `
    .status-pill{display:inline-block;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:600}
    .status-pill.active{background:#ECFDF3;color:#037847}
    .status-pill.inactive{background:#F2F4F7;color:#364254}
    `;
    document.head.appendChild(style);

    // Filters modal implementation
    function openFiltersModal() {
        if (document.getElementById('filtersModal')) return;
        const modal = document.createElement('div');
        modal.id = 'filtersModal';
        modal.style = 'position:fixed;inset:0;background:rgba(0,0,0,0.35);display:flex;align-items:center;justify-content:center;z-index:3000;';

        const panel = document.createElement('div');
        panel.style = 'background:white;padding:18px;border-radius:8px;min-width:320px;box-shadow:0 8px 24px rgba(17,24,39,0.12);';
        panel.innerHTML = `
            <h3 style="margin:0 0 12px 0;font-size:16px">Filters</h3>
            <div style="display:flex;gap:8px;margin-bottom:12px;">
                <label style="flex:1;display:flex;flex-direction:column;font-size:13px;color:#374151">Station<select id="filterStation" style="margin-top:6px;padding:8px;border:1px solid #E6E7EA;border-radius:6px;"><option>All</option><option>VADD</option><option>VABB</option><option>VOCL</option></select></label>
                <label style="flex:1;display:flex;flex-direction:column;font-size:13px;color:#374151">Status<select id="filterStatus" style="margin-top:6px;padding:8px;border:1px solid #E6E7EA;border-radius:6px;"><option>All</option><option>Active</option><option>Inactive</option></select></label>
            </div>
            <div style="display:flex;gap:8px;justify-content:flex-end;"><button id="filtersApply" class="btn">Apply</button><button id="filtersReset" class="btn">Reset</button></div>
        `;

        modal.appendChild(panel);
        document.body.appendChild(modal);

        document.getElementById('filtersApply').addEventListener('click', () => {
            const s = document.getElementById('filterStation').value;
            const st = document.getElementById('filterStatus').value;
            currentFilters.station = s;
            currentFilters.status = st;
            renderLogs();
            closeFiltersModal();
        });

        document.getElementById('filtersReset').addEventListener('click', () => {
            currentFilters = { station: 'All', status: 'All' };
            document.getElementById('filterStation').value = 'All';
            document.getElementById('filterStatus').value = 'All';
            renderLogs();
            closeFiltersModal();
        });

        modal.addEventListener('click', (e) => { if (e.target === modal) closeFiltersModal(); });
    }

    function closeFiltersModal() { const m = document.getElementById('filtersModal'); if (m) m.remove(); }

})();
