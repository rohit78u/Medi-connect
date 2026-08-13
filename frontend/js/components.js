// Reusable Component Helpers

export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const iconMap = {
    success: '✅',
    error: '❌',
    info: 'ℹ️'
  };

  toast.innerHTML = `
    <span>${iconMap[type] || 'ℹ️'}</span>
    <div style="flex:1;">${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

export function renderSkeletonCards(count = 3) {
  let html = '';
  for (let i = 0; i < count; i++) {
    html += `
      <div class="card">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text" style="width:70%;"></div>
        <div class="skeleton skeleton-card" style="height:40px; margin-top:1rem;"></div>
      </div>
    `;
  }
  return html;
}

export function renderEmptyState(title, message, icon = '📂') {
  return `
    <div class="empty-state">
      <div class="state-icon">${icon}</div>
      <h3>${title}</h3>
      <p class="page-subtitle" style="margin-top:0.5rem;">${message}</p>
    </div>
  `;
}

export function renderErrorState(message) {
  return `
    <div class="error-state">
      <div class="state-icon">⚠️</div>
      <h3>Something went wrong</h3>
      <p class="page-subtitle" style="margin-top:0.5rem; color: var(--accent-rose);">${message}</p>
    </div>
  `;
}
