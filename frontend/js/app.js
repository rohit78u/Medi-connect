import { CONFIG } from './config.js';
import { state } from './state.js';
import { showToast } from './components.js';
import { renderAuthModal, initAuthListeners } from './views/authView.js';
import { renderTriageView, initTriageListeners } from './views/triageView.js';
import { renderDoctorSearchView, initDoctorSearchListeners } from './views/doctorSearchView.js';
import { renderAppointmentsView, initAppointmentsListeners } from './views/appointmentsView.js';
import { renderPaymentModal, initPaymentListeners } from './views/paymentModal.js';

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
    container.innerHTML = `
      <button class="btn btn-secondary" id="btn-open-auth">Sign In</button>
    `;
    document.getElementById('btn-open-auth')?.addEventListener('click', () => {
      document.getElementById('auth-modal')?.classList.add('active');
    });
  }
}

function renderCurrentView() {
  const container = document.getElementById('view-container');
  if (!container) return;

  // Update Nav Active Link
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('data-view') === state.currentView) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
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

    wsSocket.onopen = () => {
      console.log('Realtime WebSocket connected for user', state.user.id);
    };

    wsSocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'NEW_APPOINTMENT_BOOKED') {
          showToast(`🔔 New Appointment Booked by ${payload.patient_name}`, 'info');
        } else if (payload.type === 'APPOINTMENT_STATUS_UPDATED') {
          showToast(`🔔 Appointment Status Updated to [${payload.status}]`, 'success');
        }
      } catch (err) {
        console.error('WS parse error:', err);
      }
    };

    wsSocket.onclose = () => {
      wsSocket = null;
    };
  } catch (err) {
    console.error('WebSocket connection failed:', err);
  }
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  // Inject static modals into DOM
  document.getElementById('modal-container').innerHTML = renderAuthModal();
  document.getElementById('payment-modal-container').innerHTML = renderPaymentModal();

  initAuthListeners();
  initPaymentListeners();

  // Navigation Links Click Listener
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const view = e.currentTarget.getAttribute('data-view');
      state.setView(view);
    });
  });

  // Subscribe state changes
  state.subscribe(() => {
    renderNavUser();
    renderCurrentView();
    initWebSockets();
  });

  // Initial render
  renderNavUser();
  renderCurrentView();
  initWebSockets();
});
