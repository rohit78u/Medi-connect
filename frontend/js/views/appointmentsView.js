import { api } from '../api.js';
import { renderEmptyState, renderErrorState, showToast } from '../components.js';
import { state } from '../state.js';
import { openPaymentModal } from './paymentModal.js';

export function renderAppointmentsView() {
  const isDoctor = state.getUserRole() === 'DOCTOR' || state.getUserRole() === 'ADMIN';

  return `
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 class="page-title">${isDoctor ? 'Doctor Clinical Schedule' : 'My Clinical Appointments'}</h1>
        <p class="page-subtitle">Track consultation statuses, clinical notes, and payment transactions</p>
      </div>
      <button class="btn btn-secondary" id="btn-refresh-appointments">🔄 Refresh Schedule</button>
    </div>

    <!-- Appointments Table Container -->
    <div class="card" style="padding:0; overflow:hidden;">
      <div class="table-container">
        <table class="data-table" id="appointments-table">
          <thead>
            <tr>
              <th>Date & Time</th>
              <th>${isDoctor ? 'Patient Name' : 'Doctor Specialist'}</th>
              <th>Reason for Visit</th>
              <th>Status</th>
              <th>Clinical Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="appointments-tbody">
            <tr><td colspan="6" style="text-align:center; padding:2rem;">Loading schedule...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

export async function loadAppointments() {
  const tbody = document.getElementById('appointments-tbody');
  if (!tbody) return;

  const isDoctor = state.getUserRole() === 'DOCTOR' || state.getUserRole() === 'ADMIN';
  const endpoint = isDoctor ? '/appointments/doctor-schedule' : '/appointments/my-appointments';

  try {
    const payload = await api.get(endpoint);
    const appointments = payload.data || [];

    if (appointments.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="padding:0;">
            ${renderEmptyState('No Appointments Scheduled', isDoctor ? 'No upcoming clinical consultations assigned.' : 'Book a consultation with a specialist.', '📅')}
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = appointments.map(app => {
      const dateStr = new Date(app.appointment_date).toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
      const nameDisplay = isDoctor ? app.patient.user.full_name : app.doctor.user.full_name;
      const statusClass = app.status.toLowerCase();

      return `
        <tr>
          <td style="font-weight:600;">${dateStr}</td>
          <td>${nameDisplay}</td>
          <td>${app.reason_for_visit || 'General Checkup'}</td>
          <td><span class="status-badge ${statusClass}">${app.status}</span></td>
          <td style="font-size:0.85rem; color:var(--text-muted);">${app.clinical_notes || 'No notes added'}</td>
          <td>
            <div style="display:flex; gap:0.5rem;">
              ${!isDoctor && app.status === 'PENDING' ? `
                <button class="btn btn-primary btn-pay-app" data-id="${app.id}" data-fee="${app.doctor.consultation_fee}" style="padding:0.35rem 0.75rem; font-size:0.8rem;">
                  Pay ₹${app.doctor.consultation_fee}
                </button>
              ` : ''}

              ${isDoctor && app.status === 'PENDING' ? `
                <button class="btn btn-success btn-update-status" data-id="${app.id}" data-status="CONFIRMED" style="padding:0.35rem 0.75rem; font-size:0.8rem;">
                  Confirm
                </button>
              ` : ''}

              ${isDoctor && app.status === 'CONFIRMED' ? `
                <button class="btn btn-primary btn-update-status" data-id="${app.id}" data-status="COMPLETED" style="padding:0.35rem 0.75rem; font-size:0.8rem;">
                  Complete
                </button>
              ` : ''}

              ${app.status !== 'CANCELLED' && app.status !== 'COMPLETED' ? `
                <button class="btn btn-danger btn-update-status" data-id="${app.id}" data-status="CANCELLED" style="padding:0.35rem 0.75rem; font-size:0.8rem;">
                  Cancel
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join('');

    // Action listeners
    document.querySelectorAll('.btn-update-status').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = e.currentTarget.getAttribute('data-id');
        const status = e.currentTarget.getAttribute('data-status');
        let clinical_notes = null;

        if (status === 'COMPLETED') {
          clinical_notes = prompt('Enter clinical consultation notes / prescription highlights:') || 'Consultation completed successfully.';
        }

        try {
          await api.patch(`/appointments/${id}/status`, { status, clinical_notes });
          showToast(`Appointment status updated to ${status}`, 'success');
          loadAppointments();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });

    document.querySelectorAll('.btn-pay-app').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const appointment_id = e.currentTarget.getAttribute('data-id');
        const amount = parseFloat(e.currentTarget.getAttribute('data-fee'));
        openPaymentModal(appointment_id, amount);
      });
    });

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="padding:2rem;">${renderErrorState(err.message)}</td></tr>`;
  }
}

export function initAppointmentsListeners() {
  const btnRefresh = document.getElementById('btn-refresh-appointments');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => loadAppointments());
  }

  loadAppointments();
}
