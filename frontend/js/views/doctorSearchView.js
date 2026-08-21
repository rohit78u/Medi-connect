import { api } from '../api.js';
import { renderSkeletonCards, renderEmptyState, renderErrorState, showToast } from '../components.js';
import { state } from '../state.js';

let selectedDoctorForBooking = null;

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
          <div class="form-group"><label class="form-label">Consultation Date & Time</label><input type="datetime-local" id="book-date" class="form-control" required></div>
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
    if (!doctors.length) { grid.innerHTML = renderEmptyState('No Doctors Found','Try adjusting your specialization search query.','♧'); return; }
    grid.innerHTML = doctors.map(doc => `<div class="card doctor-card"><div class="doctor-card-main"><div class="doctor-card-top"><div><h3 class="doctor-name">${doc.user.full_name}</h3><span class="doctor-specialization">${doc.specialization ? doc.specialization.name : 'General Practice'}</span></div><span class="doctor-fee">₹${doc.consultation_fee}</span></div><div class="doctor-license">♙ &nbsp; License: <strong>${doc.license_number}</strong> &nbsp;|&nbsp; Experience: <strong>${doc.years_of_experience} Yrs</strong></div><p class="doctor-bio">${doc.bio || 'Experienced clinician providing personalized patient care.'}</p></div><button class="btn btn-primary btn-book-doc" data-id="${doc.id}" data-name="${doc.user.full_name}">Book Appointment</button></div>`).join('');
    document.querySelectorAll('.btn-book-doc').forEach(btn => btn.addEventListener('click', e => {
      if (!state.token) { showToast('Please sign in to book an appointment.','info'); document.getElementById('auth-modal')?.classList.add('active'); return; }
      openBookingModal(e.currentTarget.getAttribute('data-id'),e.currentTarget.getAttribute('data-name'));
    }));
  } catch(err) { grid.innerHTML = renderErrorState(err.message); }
}

function openBookingModal(docId, docName) {
  selectedDoctorForBooking = docId;
  document.getElementById('book-doctor-id').value = docId;
  document.getElementById('booking-modal-title').textContent = `Book Consultation with ${docName}`;
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
    const dateVal = document.getElementById('book-date').value;
    const reason_for_visit = document.getElementById('book-reason').value;
    if (!dateVal) { showToast('Please select appointment date and time.','error'); return; }
    const btn = document.getElementById('btn-confirm-booking'); btn.disabled=true; btn.textContent='Processing...';
    try { await api.post('/appointments/book',{doctor_id,appointment_date:dateVal,reason_for_visit}); showToast('Appointment booked successfully!','success'); document.getElementById('booking-modal').classList.remove('active'); bookingForm.reset(); state.setView('appointments'); }
    catch(err) { showToast(err.message,'error'); }
    finally { btn.disabled=false; btn.textContent='Confirm & Book Appointment'; }
  });
  loadDoctors();
}
