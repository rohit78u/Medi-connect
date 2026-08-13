import { CONFIG } from './config.js';
import { state } from './state.js';
import { showToast } from './components.js';
import { renderAuthModal, initAuthListeners } from './views/authView.js';
import { renderTriageView, initTriageListeners } from './views/triageView.js';
import { renderDoctorSearchView, initDoctorSearchListeners } from './views/doctorSearchView.js';
import { renderAppointmentsView, initAppointmentsListeners } from './views/appointmentsView.js';
import { renderPaymentModal, initPaymentListeners } from './views/paymentModal.js';
import { renderDashboardView, initDashboardListeners } from './views/dashboardView.js';

let wsSocket = null;

function renderNavUser() {
  const container = document.getElementById('nav-user-section');
  if (!container) return;

  if (state.user) {
    const role = state.getUserRole();
    container.innerHTML = `
      <span class="role-badge ${role.toLowerCase()}">${role}</span>
      <span style="font-weight:600; font-size:0.9rem;">${state.user.full_name}</span>
      <button class="btn btn-danger" id="btn-logout" style="padding:0.35rem 0.75rem; font-size:0.8rem;">Sign Out</button>
    `;
    document.getElementById('btn-logout')?.addEventListener('click', () => {
      state.setUser(null, null, null);
      showToast('Signed out successfully.', 'info');
    });
  } else {
    container.innerHTML = `<button class="btn btn-secondary" id="btn-open-auth">Sign In</button>`;
    document.getElementById('btn-open-auth')?.addEventListener('click', () => document.getElementById('auth-modal')?.classList.add('active'));
  }
}

function renderCurrentView() {
  const container = document.getElementById('view-container');
  if (!container) return;

  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-view') === state.currentView);
  });

  switch (state.currentView) {
    case 'triage':
      container.innerHTML = renderTriageView();
      initTriageListeners();
      break;
    case 'doctors':
      container.innerHTML = renderDoctorSearchView();
      initDoctorSearchListeners();
      break;
    case 'appointments':
      container.innerHTML = renderAppointmentsView();
      initAppointmentsListeners();
      break;
    case 'dashboard':
      container.innerHTML = '<section class="view"><div class="card">Loading dashboard…</div></section>';
      renderDashboardView().then(html => {
        container.innerHTML = html;
        initDashboardListeners();
      });
      break;
    default:
      container.innerHTML = renderTriageView();
      initTriageListeners();
  }
}

function initWebSockets() {
  if (!state.user || wsSocket) return;
  const wsUrl = `${CONFIG.WS_BASE_URL}/notifications/${state.user.id}`;
  try {
    wsSocket = new WebSocket(wsUrl);
    wsSocket.onopen = () => console.log('Realtime WebSocket connected for user', state.user.id);
    wsSocket.onmessage = event => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'NEW_APPOINTMENT_BOOKED') showToast(`🔔 New Appointment Booked by ${payload.patient_name}`, 'info');
        else if (payload.type === 'APPOINTMENT_STATUS_UPDATED') showToast(`🔔 Appointment Status Updated to [${payload.status}]`, 'success');
      } catch (err) { console.error('WS parse error:', err); }
    };
    wsSocket.onclose = () => { wsSocket = null; };
  } catch (err) { console.error('WebSocket connection failed:', err); }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('modal-container').innerHTML = renderAuthModal();
  document.getElementById('payment-modal-container').innerHTML = renderPaymentModal();
  initAuthListeners();
  initPaymentListeners();

  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => state.setView(e.currentTarget.getAttribute('data-view')));
  });

  state.subscribe(() => {
    renderNavUser();
    renderCurrentView();
    initWebSockets();
  });

  renderNavUser();
  renderCurrentView();
  initWebSockets();
});
