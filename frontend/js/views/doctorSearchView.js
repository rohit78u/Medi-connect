import { api } from '../api.js';
import { renderSkeletonCards, renderEmptyState, renderErrorState, showToast } from '../components.js';
import { state } from '../state.js';

let selectedDoctorForBooking = null;
const doctorAvailability = new Map();

function escapeHtml(value = '') {
  return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function formatTime(value) {
  if (!value) return '';
  const [hours, minutes] = String(value).split(':').map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function formatDate(value) {
  const date = new Date(`${value}T00:00:00`);
  return date.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
}

function toIsoLocal(date, hours, minutes) {
  const pad = number => String(number).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(hours)}:${pad(minutes)}`;
}

function buildAvailableSlots(slots, daysAhead = 30) {
  const options = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (let offset = 0; offset <= daysAhead; offset += 1) {
    const date = new Date(today);
    date.setDate(today.getDate() + offset);
    const weekday = (date.getDay() + 6) % 7; // Monday=0, matching the API.
    const matchingSlots = (slots || []).filter(slot => Number(slot.day_of_week) === weekday);

    matchingSlots.forEach(slot => {
      const [startHour, startMinute] = String(slot.start_time).split(':').map(Number);
      const [endHour, endMinute] = String(slot.end_time).split(':').map(Number);
      let cursor = startHour * 60 + startMinute;
      const end = endHour * 60 + endMinute;

      while (cursor < end) {
        const hours = Math.floor(cursor / 60);
        const minutes = cursor % 60;
        const value = toIsoLocal(date, hours, minutes);
        if (new Date(value) > new Date()) {
          options.push({
            value,
            label: `${formatDate(value.slice(0, 10))} · ${formatTime(`${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`)}`
          });
        }
        cursor += 30;
      }
    });
  }

  return options;
}

export function renderDoctorSearchView() {
  return `<section class="view doctor-search-view">
    <div class="page-header">
      <span class="eyebrow">DOCTOR DIRECTORY</span>
      <h1 class="page-title">Find a Doctor & Book Appointment</h1>
      <p class="page-subtitle">Search verified medical specialists and schedule instant clinical consultations</p>
    </div>
    <div class="search-panel">
      <div class="search-input-wrap"><span class="search-icon">⌕</span><input type="text" id="search-spec" class="form-control" placeholder="Filter by Specialization (e.g. Cardiology, Neurology...)" /></div>
      <button class="btn btn-primary" id="btn-search-doctors">Search</button>
    </div>
    <div class="grid-3" id="doctors-grid">${renderSkeletonCards(3)}</div>
    <div class="modal-overlay" id="booking-modal">
      <div class="modal-card">
        <div class="modal-header"><h2 id="booking-modal-title">Book Consultation</h2><button class="modal-close" onclick="document.getElementById('booking-modal').classList.remove('active')">&times;</button></div>
        <form id="booking-form">
          <input type="hidden" id="book-doctor-id">
          <div class="form-group">
            <label class="form-label" for="book-slot">Available Consultation Date & Time</label>
            <select id="book-slot" class="form-control" required>
              <option value="">Select an available slot</option>
            </select>
            <small id="book-availability-help" style="display:block;margin-top:.5rem;color:var(--text-muted);">Choose from the doctor's configured weekly availability.</small>
          </div>
          <div class="form-group"><label class="form-label">Reason for Visit</label><textarea id="book-reason" class="form-control" rows="3" placeholder="Describe symptoms or routine checkup reason..." required></textarea></div>
          <button type="submit" class="btn btn-primary" id="btn-confirm-booking">Confirm & Book Appointment</button>
        </form>
      </div>
    </div>
  </section>`;
}

export async function loadDoctors(specialization = '') {
  const grid = document.getElementById('doctors-grid');
  if (!grid) return;
  grid.innerHTML = renderSkeletonCards(3);
  try {
    const endpoint = specialization ? `/doctors/search?specialization=${encodeURIComponent(specialization)}` : '/doctors/search';
    const payload = await api.get(endpoint);
    const doctors = payload.data || [];
    doctorAvailability.clear();

    if (!doctors.length) {
      grid.innerHTML = renderEmptyState('No Doctors Found','Try adjusting your specialization search query.','♧');
      return;
    }

    doctors.forEach(doc => doctorAvailability.set(String(doc.id), doc.availabilities || []));
    grid.innerHTML = doctors.map(doc => `<div class="card doctor-card"><div class="doctor-card-main"><div class="doctor-card-top"><div><h3 class="doctor-name">${escapeHtml(doc.user.full_name)}</h3><span class="doctor-specialization">${escapeHtml(doc.specialization ? doc.specialization.name : 'General Practice')}</span></div><span class="doctor-fee">₹${escapeHtml(doc.consultation_fee)}</span></div><div class="doctor-license">♙ &nbsp; License: <strong>${escapeHtml(doc.license_number)}</strong> &nbsp;|&nbsp; Experience: <strong>${escapeHtml(doc.years_of_experience)} Yrs</strong></div><p class="doctor-bio">${escapeHtml(doc.bio || 'Experienced clinician providing personalized patient care.')}</p></div><button class="btn btn-primary btn-book-doc" data-id="${escapeHtml(doc.id)}" data-name="${escapeHtml(doc.user.full_name)}">Book Appointment</button></div>`).join('');

    document.querySelectorAll('.btn-book-doc').forEach(btn => btn.addEventListener('click', e => {
      if (!state.token) {
        showToast('Please sign in to book an appointment.','info');
        document.getElementById('auth-modal')?.classList.add('active');
        return;
      }
      openBookingModal(e.currentTarget.getAttribute('data-id'),e.currentTarget.getAttribute('data-name'));
    }));
  } catch(err) {
    grid.innerHTML = renderErrorState(err.message);
  }
}

function openBookingModal(docId, docName) {
  selectedDoctorForBooking = docId;
  document.getElementById('book-doctor-id').value = docId;
  document.getElementById('booking-modal-title').textContent = `Book Consultation with ${docName}`;

  const slotSelect = document.getElementById('book-slot');
  const help = document.getElementById('book-availability-help');
  const slots = buildAvailableSlots(doctorAvailability.get(String(docId)) || []);

  if (!slots.length) {
    slotSelect.innerHTML = '<option value="">No upcoming availability configured</option>';
    slotSelect.disabled = true;
    help.textContent = 'This doctor has no upcoming weekly availability. Please choose another doctor or ask the doctor to configure availability.';
  } else {
    slotSelect.disabled = false;
    slotSelect.innerHTML = `<option value="">Select an available slot</option>${slots.map(slot => `<option value="${slot.value}">${slot.label}</option>`).join('')}`;
    help.textContent = 'Only times inside the doctor\'s configured weekly availability are shown. A slot can still be taken by another appointment.';
  }

  document.getElementById('booking-modal').classList.add('active');
}

export function initDoctorSearchListeners() {
  const btnSearch = document.getElementById('btn-search-doctors');
  const inputSpec = document.getElementById('search-spec');
  const bookingForm = document.getElementById('booking-form');
  btnSearch?.addEventListener('click', () => loadDoctors(inputSpec.value));
  inputSpec?.addEventListener('keydown', e => { if (e.key === 'Enter') loadDoctors(inputSpec.value); });

  bookingForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const doctor_id = document.getElementById('book-doctor-id').value;
    const dateVal = document.getElementById('book-slot').value;
    const reason_for_visit = document.getElementById('book-reason').value;
    if (!dateVal) { showToast('Please select an available appointment slot.','error'); return; }

    const btn = document.getElementById('btn-confirm-booking');
    btn.disabled=true;
    btn.textContent='Processing...';
    try {
      await api.post('/appointments/book',{doctor_id,appointment_date:dateVal,reason_for_visit});
      showToast('Appointment booked successfully!','success');
      document.getElementById('booking-modal').classList.remove('active');
      bookingForm.reset();
      state.setView('appointments');
    } catch(err) {
      showToast(err.message,'error');
    } finally {
      btn.disabled=false;
      btn.textContent='Confirm & Book Appointment';
    }
  });

  loadDoctors();
}
