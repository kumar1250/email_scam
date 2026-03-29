/* ============================================================
   ShieldMail — Main JS
   ============================================================ */

// ── Dark Mode ──────────────────────────────────────────────
(function () {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

document.addEventListener('DOMContentLoaded', function () {

  // Theme toggle
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }

  // Sidebar mobile toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Auto-dismiss alerts after 5s
  setTimeout(function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (el) {
      el.style.opacity = '0';
      el.style.transition = 'opacity .4s ease';
      setTimeout(function () { el.remove(); }, 400);
    });
  }, 5000);

  // Animate stat values
  document.querySelectorAll('.stat-value').forEach(function (el) {
    const target = parseInt(el.textContent);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(function () {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });

  // Notification bell demo
  const bell = document.querySelector('.notification-bell button');
  if (bell) {
    bell.addEventListener('click', function () {
      showToast('No new notifications', 'info');
    });
  }

});

// ── Toast Notification ─────────────────────────────────────
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast-container');
  if (existing) existing.remove();

  const container = document.createElement('div');
  container.className = 'toast-container';
  container.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    display: flex; flex-direction: column; gap: 8px;
  `;

  const toast = document.createElement('div');
  const colors = {
    success: '#22c55e', danger: '#ef4444', warning: '#f59e0b', info: '#6366f1'
  };
  const icons = {
    success: 'fa-circle-check', danger: 'fa-circle-xmark',
    warning: 'fa-triangle-exclamation', info: 'fa-circle-info'
  };

  toast.style.cssText = `
    display: flex; align-items: center; gap: 10px;
    background: white; border-radius: 10px;
    padding: 12px 18px; box-shadow: 0 8px 24px rgba(0,0,0,.15);
    border-left: 4px solid ${colors[type] || colors.info};
    font-family: Inter, sans-serif; font-size: 14px;
    animation: slideInRight .3s ease; min-width: 260px;
    color: #0f172a;
  `;
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}" style="color:${colors[type] || colors.info}"></i> ${message}`;

  const style = document.createElement('style');
  style.textContent = `@keyframes slideInRight { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
  document.head.appendChild(style);

  container.appendChild(toast);
  document.body.appendChild(container);
  setTimeout(() => { container.remove(); }, 3500);
}
