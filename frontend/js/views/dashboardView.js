import { api } from '../api.js';
import { state } from '../state.js';
import { showToast } from '../components.js';

function esc(value = '') {
  return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function card(title, value, subtitle = '') {
  return `<div class="card"><div style="color:var(--text-muted);font-size:.85rem">${esc(title)}</div><div style="font-size:1.8rem;font-weight:700;margin:.35rem 0">${esc(value)}</div><div style="color:var(--text-muted);font-size:.8rem">${esc(subtitle)}</div></div>`;
}

function appointmentRow(a) {
  const date = a.scheduled_at ? new Date(a.scheduled_at).toLocaleString() : 'Scheduled time unavailable';
  return `<div class="card" style="margin-top:.75rem"><div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap"><strong>${esc(a.doctor_name || a.patient_name || 'Appointment')}</strong><span class="role-badge">${esc(a.status || 'PENDING')}</span></div><div style="margin-top:.4rem;color:var(--text-muted)">${esc(date)}</div><div style="margin-top:.35rem">${esc(a.reason || 'Clinical consultation')}</div></div>`;
}

async function patientDashboard() {
  const [profileResult, appointmentsResult] = await Promise.all([api.get('/patients/me'), api.get('/appointments/my-appointments?limit=50')]);
  const profile = profileResult.data || {};
  const appointments = appointmentsResult.data || [];
  const upcoming = appointments.filter(a => !['COMPLETED','CANCELLED'].includes(a.status)).slice(0, 3);
  return `<section class="view dashboard-view"><div style="margin-bottom:1.5rem"><h1>Patient Dashboard</h1><p style="color:var(--text-muted)">Welcome back, ${esc(state.user?.full_name || 'Patient')}.</p></div><div class="grid grid-3">${card('Appointments', appointments.length, 'Total scheduled')}${card('Upcoming', upcoming.length, 'Active appointments')}${card('Blood Group', profile.blood_group || 'Not set', 'From your patient profile')}</div><div class="card" style="margin-top:1.25rem"><h2>Patient profile</h2><form id="patient-profile-form" style="display:grid;gap:.75rem;max-width:650px"><label>Date of birth<input name="date_of_birth" type="date" value="${esc(profile.date_of_birth || '')}"></label><label>Blood group<input name="blood_group" value="${esc(profile.blood_group || '')}" placeholder="e.g. O+"></label><label>Emergency contact<input name="emergency_contact" value="${esc(profile.emergency_contact || '')}"></label><label>Medical history<textarea name="medical_history" rows="4" placeholder="Relevant medical history">${esc(profile.medical_history || '')}</textarea></label><button class="btn btn-primary" type="submit">Save profile</button></form></div><div style="margin-top:1.25rem"><h2>Upcoming appointments</h2>${upcoming.length ? upcoming.map(appointmentRow).join('') : '<div class="card">No upcoming appointments.</div>'}</div></section>`;
}

async function doctorDashboard() {
  const result = await api.get('/appointments/doctor-schedule?limit=50');
  const appointments = result.data || [];
  const active = appointments.filter(a => !['COMPLETED','CANCELLED'].includes(a.status));
  return `<section class="view dashboard-view"><div style="margin-bottom:1.5rem"><h1>Doctor Dashboard</h1><p style="color:var(--text-muted)">Clinical schedule for ${esc(state.user?.full_name || 'Doctor')}.</p></div><div class="grid grid-3">${card('Total appointments', appointments.length, 'Loaded clinical schedule')}${card('Active', active.length, 'Pending or confirmed')}${card('Completed', appointments.filter(a => a.status === 'COMPLETED').length, 'Completed consultations')}</div><div class="card" style="margin-top:1.25rem"><h2>Weekly availability</h2><p style="color:var(--text-muted)">Add recurring availability slots. These slots are enforced by the booking API.</p><form id="availability-form" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.75rem"><label>Day<select name="day_of_week"><option value="0">Monday</option><option value="1">Tuesday</option><option value="2">Wednesday</option><option value="3">Thursday</option><option value="4">Friday</option><option value="5">Saturday</option><option value="6">Sunday</option></select></label><label>Start<input name="start_time" type="time" required></label><label>End<input name="end_time" type="time" required></label><div style="display:flex;align-items:end"><button class="btn btn-primary" type="submit">Add slot</button></div></form></div><div style="margin-top:1.25rem"><h2>Schedule</h2>${appointments.length ? appointments.map(appointmentRow).join('') : '<div class="card">No appointments scheduled.</div>'}</div></section>`;
}

function adminDoctorRow(doctor) {
  const name = doctor.full_name || doctor.name || 'Doctor';
  const specialization = doctor.specialization || doctor.specialization_name || 'Not specified';
  return `<div class="card admin-doctor-row" style="margin-top:.75rem"><div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap"><div><strong>${esc(name)}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(doctor.email || '')} · ${esc(specialization)}</div></div><div><button class="btn btn-primary admin-verify-doctor" data-doctor-id="${esc(doctor.id)}">Approve</button><button class="btn btn-danger admin-reject-doctor" data-doctor-id="${esc(doctor.id)}" style="margin-left:.5rem">Reject</button></div></div></div>`;
}

function adminTable(title, rows, empty) {
  return `<div class="card" style="margin-top:1.25rem"><h2>${esc(title)}</h2>${rows.length ? rows.join('') : `<p style="color:var(--text-muted)">${esc(empty)}</p>`}</div>`;
}

async function adminDashboard() {
  const [dashboard, doctors, users, appointments, payments] = await Promise.all([
    api.get('/admin/dashboard'),
    api.get('/admin/doctors/pending'),
    api.get('/admin/users'),
    api.get('/admin/appointments'),
    api.get('/admin/payments')
  ]);
  const stats = dashboard.data || {};
  const pendingDoctors = doctors.data || [];
  const userRows = (users.data || []).slice(0, 10).map(u => `<div class="card" style="margin-top:.5rem"><strong>${esc(u.full_name || 'User')}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(u.email || '')} · ${u.is_verified ? 'Verified' : 'Unverified'}</div></div>`);
  const appointmentRows = (appointments.data || []).slice(0, 10).map(a => `<div class="card" style="margin-top:.5rem"><strong>${esc(a.id)}</strong><div style="color:var(--text-muted);font-size:.85rem">Patient: ${esc(a.patient_id)} · Doctor: ${esc(a.doctor_id)} · ${esc(a.status)}</div></div>`);
  const paymentRows = (payments.data || []).slice(0, 10).map(p => `<div class="card" style="margin-top:.5rem"><strong>${esc(p.id)}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(p.status || 'UNKNOWN')} · ${esc(p.amount ?? '')}</div></div>`);
  return `<section class="view dashboard-view"><div style="margin-bottom:1.5rem"><h1>Admin Dashboard</h1><p style="color:var(--text-muted)">Platform administration and doctor verification center.</p></div><div class="grid grid-3">${card('Users', stats.users ?? 0, 'Registered users')}${card('Doctors', stats.doctors ?? 0, 'Doctor profiles')}${card('Appointments', stats.appointments ?? 0, `${stats.pending_appointments ?? 0} pending`)}</div>${adminTable('Pending doctor verification', pendingDoctors.map(adminDoctorRow), 'No doctors are waiting for verification.')}${adminTable('Recent users', userRows, 'No users found.')}${adminTable('Appointments', appointmentRows, 'No appointments found.')}${adminTable('Payments', paymentRows, 'No payment transactions found.')}</section>`;
}

export async function renderDashboardView() {
  try {
    const role = state.getUserRole();
    if (role === 'DOCTOR') return await doctorDashboard();
    if (role === 'ADMIN') return await adminDashboard();
    return await patientDashboard();
  } catch (error) {
    showToast(error.message || 'Unable to load dashboard', 'error');
    return `<section class="view"><div class="card"><h2>Dashboard unavailable</h2><p>${esc(error.message || 'Please try again.')}</p></div></section>`;
  }
}

export function initDashboardListeners() {
  document.getElementById('patient-profile-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try { await api.put('/patients/me', Object.fromEntries(form.entries())); showToast('Patient profile saved.', 'success'); }
    catch (error) { showToast(error.message || 'Profile update failed.', 'error'); }
  });
  document.getElementById('availability-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try { await api.post('/doctors/availability', {day_of_week:Number(form.get('day_of_week')), start_time:form.get('start_time'), end_time:form.get('end_time')}); showToast('Availability slot added.', 'success'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Could not add availability.', 'error'); }
  });
  document.querySelectorAll('.admin-verify-doctor').forEach(button => button.addEventListener('click', async () => {
    try { await api.post(`/admin/doctors/${button.dataset.doctorId}/verify`, {}); showToast('Doctor approved.', 'success'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Doctor approval failed.', 'error'); }
  }));
  document.querySelectorAll('.admin-reject-doctor').forEach(button => button.addEventListener('click', async () => {
    if (!window.confirm('Reject this doctor verification request?')) return;
    try { await api.post(`/admin/doctors/${button.dataset.doctorId}/reject`, {}); showToast('Doctor rejected.', 'info'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Doctor rejection failed.', 'error'); }
  }));
}
