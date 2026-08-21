import { api } from '../api.js';
import { state } from '../state.js';
import { showToast } from '../components.js';

function esc(value = '') {
  return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function card(title, value, subtitle = '') {
  return `<div class="card"><div>${esc(title)}</div><div>${esc(value)}</div><div>${esc(subtitle)}</div></div>`;
}

function appointmentRow(a) {
  const date = a.appointment_date ? new Date(a.appointment_date).toLocaleString() : 'Scheduled time unavailable';
  const patientName = a.patient?.user?.full_name || 'Patient';
  const reason = a.reason_for_visit || 'Clinical consultation';
  const status = a.status || 'PENDING';
  const actions = status === 'PENDING' ? `<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.8rem">
    <button class="btn btn-primary doctor-appointment-action" data-appointment-id="${esc(a.id)}" data-status="CONFIRMED">Approve</button>
    <button class="btn btn-danger doctor-appointment-action" data-appointment-id="${esc(a.id)}" data-status="CANCELLED">Reject</button>
  </div>` : '';
  return `<div class="card" style="margin-top:.75rem">
    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
      <strong>${esc(patientName)}</strong><span class="role-badge ${esc(status.toLowerCase())}">${esc(status)}</span>
    </div>
    <div style="margin-top:.4rem;color:var(--text-muted)">${esc(date)}</div>
    <div style="margin-top:.35rem">${esc(reason)}</div>${actions}
  </div>`;
}

function profileSetupView() {
  return `<section class="view dashboard-view">
    <div class="page-header"><span class="eyebrow">CLINICIAN ONBOARDING</span><h1 class="page-title">Complete your doctor profile</h1>
      <p class="page-subtitle">Your login account exists, but MediConnect still needs your clinical profile before you can receive appointments.</p>
    </div>
    <div class="card" style="max-width:900px;margin-top:22px">
      <h2>Doctor Profile</h2>
      <p style="margin:8px 0 20px;color:var(--text-muted)">After you submit this form, an administrator must verify the profile before patients can find and book you.</p>
      <form id="doctor-profile-form" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px">
        <label>Specialization<input class="form-control" name="specialization_name" placeholder="e.g. Cardiology" required></label>
        <label>Medical license number<input class="form-control" name="license_number" placeholder="e.g. LIC-123456" required></label>
        <label>Consultation fee (₹)<input class="form-control" name="consultation_fee" type="number" min="0" step="0.01" value="1000" required></label>
        <label>Years of experience<input class="form-control" name="years_of_experience" type="number" min="0" value="1" required></label>
        <label style="grid-column:1/-1">Professional bio<textarea class="form-control" name="bio" rows="4" placeholder="Briefly describe your clinical experience and expertise"></textarea></label>
        <div style="grid-column:1/-1"><button class="btn btn-primary" type="submit">Create Doctor Profile</button></div>
      </form>
    </div>
  </section>`;
}

async function doctorDashboard() {
  let profile;
  try {
    const result = await api.get('/doctors/me');
    profile = result.data;
  } catch (error) {
    if (error.statusCode === 404 || /doctor profile not found/i.test(error.message || '')) return profileSetupView();
    throw error;
  }

  const result = await api.get('/appointments/doctor-schedule?limit=50');
  const appointments = result.data || [];
  const pending = appointments.filter(a => a.status === 'PENDING');
  const confirmed = appointments.filter(a => a.status === 'CONFIRMED');
  const verifiedLabel = profile?.is_verified ? 'Verified' : 'Pending admin verification';

  return `<section class="view dashboard-view">
    <div class="page-header"><span class="eyebrow">CLINICIAN PORTAL</span><h1 class="page-title">Doctor Dashboard</h1>
      <p class="page-subtitle">Clinical schedule for ${esc(state.user?.full_name || 'Doctor')}.</p>
    </div>
    <div class="grid-3">
      ${card('Total appointments', appointments.length, 'Loaded clinical schedule')}
      ${card('Pending requests', pending.length, 'Need your approval')}
      ${card('Confirmed', confirmed.length, 'Upcoming confirmed visits')}
    </div>
    <div class="card" style="margin-top:22px">
      <h2>Doctor Profile</h2>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:14px">
        <div><strong>Name</strong><div>${esc(profile.user?.full_name || state.user?.full_name || 'Doctor')}</div></div>
        <div><strong>Specialization</strong><div>${esc(profile.specialization?.name || 'Not specified')}</div></div>
        <div><strong>License</strong><div>${esc(profile.license_number)}</div></div>
        <div><strong>Experience</strong><div>${esc(profile.years_of_experience)} years</div></div>
        <div><strong>Consultation fee</strong><div>₹${esc(profile.consultation_fee)}</div></div>
        <div><strong>Verification</strong><div>${esc(verifiedLabel)}</div></div>
      </div>
      ${profile.bio ? `<p style="margin-top:14px">${esc(profile.bio)}</p>` : ''}
      ${!profile.is_verified ? '<p style="margin-top:14px;color:var(--text-muted)">Patients will not see this profile in Doctor Search until an administrator verifies it.</p>' : ''}
    </div>
    <div class="card" style="margin-top:22px"><h2>Appointment Requests</h2><p style="margin:8px 0 18px">Review patient requests and approve or reject them.</p>${pending.length ? pending.map(appointmentRow).join('') : '<div style="color:var(--text-muted)">No pending appointment requests.</div>'}</div>
    <div class="card" style="margin-top:22px"><h2>Weekly availability</h2><p style="margin:8px 0 18px">Add recurring availability slots. These slots are enforced by the booking API.</p>
      <form id="availability-form" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px">
        <label>Day<select class="form-control" name="day_of_week"><option value="0">Monday</option><option value="1">Tuesday</option><option value="2">Wednesday</option><option value="3">Thursday</option><option value="4">Friday</option><option value="5">Saturday</option><option value="6">Sunday</option></select></label>
        <label>Start<input class="form-control" name="start_time" type="time" required></label>
        <label>End<input class="form-control" name="end_time" type="time" required></label>
        <div style="display:flex;align-items:end"><button class="btn btn-primary" type="submit">Add slot</button></div>
      </form>
    </div>
    <div style="margin-top:28px"><h2>Clinical Schedule</h2>${appointments.length ? appointments.map(appointmentRow).join('') : '<div class="card" style="margin-top:12px">No appointments scheduled.</div>'}</div>
  </section>`;
}

export async function renderDoctorDashboardView() {
  try {
    return await doctorDashboard();
  } catch (error) {
    showToast(error.message || 'Unable to load doctor dashboard', 'error');
    return `<section class="view"><div class="card"><h2>Doctor dashboard unavailable</h2><p>${esc(error.message || 'Please try again.')}</p></div></section>`;
  }
}

export function initDoctorDashboardListeners() {
  document.getElementById('doctor-profile-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api.post('/doctors/profile', {
        specialization_name: form.get('specialization_name'),
        license_number: form.get('license_number'),
        consultation_fee: Number(form.get('consultation_fee')),
        years_of_experience: Number(form.get('years_of_experience')),
        bio: form.get('bio') || null
      });
      showToast('Doctor profile created. It is now waiting for admin verification.', 'success');
      state.setView('dashboard');
    } catch (error) {
      showToast(error.message || 'Could not create doctor profile.', 'error');
    }
  });

  document.getElementById('availability-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await api.post('/doctors/availability', { day_of_week: Number(form.get('day_of_week')), start_time: form.get('start_time'), end_time: form.get('end_time') });
      showToast('Availability slot added.', 'success');
      state.setView('dashboard');
    } catch (error) {
      showToast(error.message || 'Could not add availability.', 'error');
    }
  });

  document.querySelectorAll('.doctor-appointment-action').forEach(button => button.addEventListener('click', async () => {
    const appointmentId = button.dataset.appointmentId;
    const status = button.dataset.status;
    const actionText = status === 'CONFIRMED' ? 'approve' : 'reject';
    if (!window.confirm(`Are you sure you want to ${actionText} this appointment?`)) return;
    button.disabled = true;
    try {
      await api.patch(`/appointments/${appointmentId}/status`, { status });
      showToast(status === 'CONFIRMED' ? 'Appointment approved successfully.' : 'Appointment rejected.', status === 'CONFIRMED' ? 'success' : 'info');
      state.setView('dashboard');
    } catch (error) {
      button.disabled = false;
      showToast(error.message || `Could not ${actionText} appointment.`, 'error');
    }
  }));
}
