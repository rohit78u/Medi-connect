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
  const date = a.scheduled_at ? new Date(a.scheduled_at).toLocaleString() : 'Scheduled time unavailable';
  return `<div class="card" style="margin-top:.75rem"><div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap"><strong>${esc(a.doctor_name || a.patient_name || 'Appointment')}</strong><span class="role-badge">${esc(a.status || 'PENDING')}</span></div><div style="margin-top:.4rem;color:var(--text-muted)">${esc(date)}</div><div style="margin-top:.35rem">${esc(a.reason || 'Clinical consultation')}</div></div>`;
}

async function patientDashboard() {
  const [profileResult, appointmentsResult] = await Promise.all([
    api.get('/patients/me'),
    api.get('/appointments/my-appointments?limit=50')
  ]);
  const profile = profileResult.data || {};
  const appointments = appointmentsResult.data || [];
  const upcoming = appointments.filter(a => !['COMPLETED','CANCELLED'].includes(a.status)).slice(0, 3);
  const firstName = (state.user?.full_name || 'Patient').split(' ')[0];
  const profileComplete = [profile.date_of_birth, profile.blood_group, profile.gender].filter(Boolean).length;

  return `<section class="view dashboard-view">
    <div class="dashboard-hero">
      <div>
        <span class="eyebrow">PATIENT PORTAL</span>
        <h1>Good to see you, ${esc(firstName)}.</h1>
        <p>Your care, appointments, and health information — all in one place.</p>
      </div>
      <span class="profile-status">⚠ Profile needs attention</span>
    </div>

    <div class="grid-3">
      ${card('Appointments', appointments.length, 'Total scheduled')}
      ${card('Upcoming', upcoming.length, 'Active appointments')}
      ${card('Blood group', profile.blood_group || 'Not set', 'From your patient profile')}
    </div>

    <div class="profile-card card">
      <div class="profile-shell">
        <div class="profile-form-area">
          <div class="profile-card-heading">
            <div>
              <h2>Your Health Details</h2>
              <div class="profile-avatar">${esc((state.user?.full_name || 'P').charAt(0).toUpperCase())}</div>
              <h3 style="font-size:17px;margin:0 0 5px;">${esc(state.user?.full_name || 'Patient')}</h3>
              <p>Keep a few essential details updated so your care team has the right context.</p>
            </div>
            <span class="profile-lock">🔒 Private & secure</span>
          </div>
          <div style="display:flex;gap:18px;border-bottom:1px solid var(--border);margin-bottom:20px;padding-bottom:10px;">
            <span style="color:var(--brand);font-size:13px;font-weight:700;border-bottom:2px solid var(--brand);padding-bottom:10px;margin-bottom:-11px;">Profile setup</span>
            <span style="color:var(--text-muted);font-size:13px;">Add essentials</span>
          </div>
          <form id="patient-profile-form" class="patient-profile-form">
            <div class="profile-field"><label for="profile-dob">Date of birth</label><input id="profile-dob" class="form-control" name="date_of_birth" type="date" value="${esc(profile.date_of_birth || '')}"></div>
            <div class="profile-field"><label for="profile-blood">Blood group</label><select id="profile-blood" class="form-control" name="blood_group"><option value="">Select blood group</option>${['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(value => `<option value="${value}" ${profile.blood_group === value ? 'selected' : ''}>${value}</option>`).join('')}</select></div>
            <div class="profile-field"><label for="profile-gender">Gender</label><select id="profile-gender" class="form-control" name="gender"><option value="">Prefer not to say</option>${['Male','Female','Other'].map(value => `<option value="${value}" ${profile.gender === value ? 'selected' : ''}>${value}</option>`).join('')}</select></div>
            <div class="profile-field"><label for="profile-contact">Emergency contact</label><input id="profile-contact" class="form-control" name="emergency_contact" value="${esc(profile.emergency_contact || '')}" placeholder="Name or phone number"></div>
            <div class="profile-field profile-field-wide"><label for="profile-history">Medical history (Optional)</label><textarea id="profile-history" class="form-control" name="medical_history_summary" rows="3" placeholder="Add allergies, ongoing conditions, medications, or relevant history">${esc(profile.medical_history_summary || '')}</textarea></div>
            <div class="profile-actions"><span>Profile completion: ${profileComplete} of 5 details added</span><button class="btn btn-primary" type="submit">Save changes</button></div>
          </form>
        </div>

        <aside class="care-timeline">
          <h2>Care timeline</h2>
          <p style="font-size:13px;font-weight:700;margin-bottom:14px;">Upcoming appointments</p>
          ${upcoming.length ? upcoming.map(appointmentRow).join('') : `<div class="care-empty"><div class="state-icon">▣</div><p>No upcoming appointments. Browse the doctor directory to book your first visit.</p></div>`}
        </aside>
      </div>
    </div>
  </section>`;
}

function doctorProfileSetup() {
  return `<section class="view dashboard-view">
    <div class="page-header">
      <span class="eyebrow">CLINICIAN PORTAL</span>
      <h1 class="page-title">Complete your doctor profile</h1>
      <p class="page-subtitle">Your doctor account is signed in, but a clinical profile has not been created yet. Add these details to unlock your schedule and availability controls.</p>
    </div>
    <div class="card" style="max-width:820px;margin-top:24px">
      <form id="doctor-profile-form" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px">
        <label>Specialization<input class="form-control" name="specialization_name" placeholder="e.g. Cardiology" required></label>
        <label>License number<input class="form-control" name="license_number" placeholder="e.g. MC-2026-1001" required></label>
        <label>Consultation fee (₹)<input class="form-control" name="consultation_fee" type="number" min="0" step="0.01" value="500" required></label>
        <label>Years of experience<input class="form-control" name="years_of_experience" type="number" min="0" step="1" value="1" required></label>
        <label style="grid-column:1/-1">Professional bio<textarea class="form-control" name="bio" rows="4" placeholder="Briefly describe your clinical experience and focus areas"></textarea></label>
        <div style="grid-column:1/-1;display:flex;justify-content:flex-end"><button class="btn btn-primary" type="submit">Create Doctor Profile</button></div>
      </form>
      <p style="margin:14px 0 0;color:var(--text-muted);font-size:.9rem">After creating the profile, add your weekly availability. Doctor verification remains controlled by the existing admin workflow.</p>
    </div>
  </section>`;
}

async function doctorDashboard() {
  try {
    const result = await api.get('/appointments/doctor-schedule?limit=50');
    const appointments = result.data || [];
    const active = appointments.filter(a => !['COMPLETED','CANCELLED'].includes(a.status));
    return `<section class="view dashboard-view"><div class="page-header"><span class="eyebrow">CLINICIAN PORTAL</span><h1 class="page-title">Doctor Dashboard</h1><p class="page-subtitle">Clinical schedule for ${esc(state.user?.full_name || 'Doctor')}.</p></div><div class="grid-3">${card('Total appointments', appointments.length, 'Loaded clinical schedule')}${card('Active', active.length, 'Pending or confirmed')}${card('Completed', appointments.filter(a => a.status === 'COMPLETED').length, 'Completed consultations')}</div><div class="card" style="margin-top:22px"><h2>Weekly availability</h2><p style="margin:8px 0 18px">Add recurring availability slots. Patients can now select only dates and times that fall inside these configured slots.</p><form id="availability-form" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px"><label>Day<select class="form-control" name="day_of_week"><option value="0">Monday</option><option value="1">Tuesday</option><option value="2">Wednesday</option><option value="3">Thursday</option><option value="4">Friday</option><option value="5">Saturday</option><option value="6">Sunday</option></select></label><label>Start<input class="form-control" name="start_time" type="time" required></label><label>End<input class="form-control" name="end_time" type="time" required></label><div style="display:flex;align-items:end"><button class="btn btn-primary" type="submit">Add slot</button></div></form></div><div style="margin-top:28px"><h2>Schedule</h2>${appointments.length ? appointments.map(appointmentRow).join('') : '<div class="card" style="margin-top:12px">No appointments scheduled.</div>'}</div></section>`;
  } catch (error) {
    if (error.statusCode === 404 && /doctor profile not found/i.test(error.message || '')) return doctorProfileSetup();
    throw error;
  }
}

function adminDoctorRow(doctor) {
  const name = doctor.full_name || doctor.name || 'Doctor';
  const specialization = doctor.specialization || doctor.specialization_name || 'Not specified';
  return `<div class="card admin-doctor-row" style="margin-top:.75rem"><div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap"><div><strong>${esc(name)}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(doctor.email || '')} · ${esc(specialization)}</div></div><div><button class="btn btn-primary admin-verify-doctor" data-doctor-id="${esc(doctor.id)}">Approve</button><button class="btn btn-danger admin-reject-doctor" data-doctor-id="${esc(doctor.id)}" style="margin-left:.5rem">Reject</button></div></div></div>`;
}
function adminTable(title, rows, empty) { return `<div class="card" style="margin-top:22px"><h2>${esc(title)}</h2>${rows.length ? rows.join('') : `<p style="margin-top:10px">${esc(empty)}</p>`}</div>`; }

async function adminDashboard() {
  const [dashboard, doctors, users, appointments, payments] = await Promise.all([api.get('/admin/dashboard'),api.get('/admin/doctors/pending'),api.get('/admin/users'),api.get('/admin/appointments'),api.get('/admin/payments')]);
  const stats = dashboard.data || {};
  const pendingDoctors = doctors.data || [];
  const userRows = (users.data || []).slice(0,10).map(u => `<div class="card" style="margin-top:.5rem"><strong>${esc(u.full_name || 'User')}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(u.email || '')} · ${u.is_verified ? 'Verified' : 'Unverified'}</div></div>`);
  const appointmentRows = (appointments.data || []).slice(0,10).map(a => `<div class="card" style="margin-top:.5rem"><strong>${esc(a.id)}</strong><div style="color:var(--text-muted);font-size:.85rem">Patient: ${esc(a.patient_id)} · Doctor: ${esc(a.doctor_id)} · ${esc(a.status)}</div></div>`);
  const paymentRows = (payments.data || []).slice(0,10).map(p => `<div class="card" style="margin-top:.5rem"><strong>${esc(p.id)}</strong><div style="color:var(--text-muted);font-size:.85rem">${esc(p.status || 'UNKNOWN')} · ${esc(p.amount ?? '')}</div></div>`);
  return `<section class="view dashboard-view"><div class="page-header"><span class="eyebrow">ADMIN PORTAL</span><h1 class="page-title">Admin Dashboard</h1><p class="page-subtitle">Platform administration and doctor verification center.</p></div><div class="grid-3">${card('Users',stats.users??0,'Registered users')}${card('Doctors',stats.doctors??0,'Doctor profiles')}${card('Appointments',stats.appointments??0,`${stats.pending_appointments??0} pending`)}</div>${adminTable('Pending doctor verification',pendingDoctors.map(adminDoctorRow),'No doctors are waiting for verification.')}${adminTable('Recent users',userRows,'No users found.')}${adminTable('Appointments',appointmentRows,'No appointments found.')}${adminTable('Payments',paymentRows,'No payment transactions found.')}</section>`;
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

  document.getElementById('doctor-profile-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      specialization_name: String(form.get('specialization_name') || '').trim(),
      license_number: String(form.get('license_number') || '').trim(),
      consultation_fee: Number(form.get('consultation_fee')),
      years_of_experience: Number(form.get('years_of_experience')),
      bio: String(form.get('bio') || '').trim() || null,
    };
    const button = event.currentTarget.querySelector('button[type="submit"]');
    if (button) { button.disabled = true; button.textContent = 'Creating profile...'; }
    try {
      await api.post('/doctors/profile', payload);
      showToast('Doctor profile created. Add your weekly availability next.', 'success');
      state.setView('dashboard');
    } catch (error) {
      showToast(error.message || 'Doctor profile creation failed.', 'error');
    } finally {
      if (button) { button.disabled = false; button.textContent = 'Create Doctor Profile'; }
    }
  });

  document.getElementById('availability-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const start = String(form.get('start_time') || '');
    const end = String(form.get('end_time') || '');
    if (!start || !end || start >= end) { showToast('End time must be later than start time.','error'); return; }
    try { await api.post('/doctors/availability', {day_of_week:Number(form.get('day_of_week')),start_time:start,end_time:end}); showToast('Availability slot added.','success'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Could not add availability.','error'); }
  });
  document.querySelectorAll('.admin-verify-doctor').forEach(button => button.addEventListener('click', async () => {
    try { await api.post(`/admin/doctors/${button.dataset.doctorId}/verify`,{}); showToast('Doctor approved.','success'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Doctor approval failed.','error'); }
  }));
  document.querySelectorAll('.admin-reject-doctor').forEach(button => button.addEventListener('click', async () => {
    if (!window.confirm('Reject this doctor verification request?')) return;
    try { await api.post(`/admin/doctors/${button.dataset.doctorId}/reject`,{}); showToast('Doctor rejected.','info'); state.setView('dashboard'); }
    catch (error) { showToast(error.message || 'Doctor rejection failed.','error'); }
  }));
}
