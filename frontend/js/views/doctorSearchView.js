import { api } from '../api.js';
import { renderSkeletonCards, renderEmptyState, renderErrorState, showToast } from '../components.js';
import { state } from '../state.js';

let selectedDoctorForBooking = null;

export function renderDoctorSearchView() {
  return `
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 class="page-title">Find a Doctor & Book Appointment</h1>
        <p class="page-subtitle">Search verified medical specialists and schedule instant clinical consultations</p>
      </div>
      <div style="display:flex; gap:1rem;">
        <input type="text" id="search-spec" class="form-control" placeholder="Filter by Specialization (e.g. Cardiology)..." style="min-width:280px;">
        <button class="btn btn-primary" id="btn-search-doctors">Search</button>
      </div>
    </div>

    <!-- Doctor Cards Grid -->
    <div class="grid-3" id="doctors-grid">
      ${renderSkeletonCards(3)}
    </div>

    <!-- Appointment Booking Modal Overlay -->
    <div class="modal-overlay" id="booking-modal">
      <div class="modal-card">
        <div class="modal-header">
          <h2 id="booking-modal-title">Book Consultation</h2>
          <button class="modal-close" onclick="document.getElementById('booking-modal').classList.remove('active')">&times;</button>
        </div>

        <form id="booking-form">
          <input type="hidden" id="book-doctor-id">
          
          <div class="form-group">
            <label class="form-label">Consultation Date & Time</label>
            <input type="datetime-local" id="book-date" class="form-control" required>
          </div>

          <div class="form-group">
            <label class="form-label">Reason for Visit</label>
            <textarea id="book-reason" class="form-control" rows="3" placeholder="Describe symptoms or routine checkup reason..." required></textarea>
          </div>

          <button type="submit" class="btn btn-primary" id="btn-confirm-booking" style="width:100%;">
            Confirm & Book Appointment
          </button>
        </form>
      </div>
    </div>
  `;
}

export async function loadDoctors(specialization = '') {
  const grid = document.getElementById('doctors-grid');
  if (!grid) return;

  grid.innerHTML = renderSkeletonCards(3);

  try {
    const endpoint = specialization ? `/doctors/search?specialization=${encodeURIComponent(specialization)}` : '/doctors/search';
    const payload = await api.get(endpoint);
    const doctors = payload.data || [];

    if (doctors.length === 0) {
      grid.innerHTML = renderEmptyState('No Doctors Found', 'Try adjusting your specialization search query.', '👨‍⚕️');
      return;
    }

    grid.innerHTML = doctors.map(doc => `
      <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <div>
              <h3 style="font-size:1.15rem;">${doc.user.full_name}</h3>
              <span style="font-size:0.85rem; color:var(--accent-cyan); font-weight:600;">${doc.specialization ? doc.specialization.name : 'General Practice'}</span>
            </div>
            <span style="font-size:0.9rem; font-weight:700; color:var(--accent-emerald);">₹${doc.consultation_fee}</span>
          </div>

          <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.75rem;">
            License: <strong>${doc.license_number}</strong> | Experience: <strong>${doc.years_of_experience} Yrs</strong>
          </p>

          <p style="font-size:0.9rem; margin-bottom:1rem; color:var(--text-muted);">
            ${doc.bio || 'Experienced clinician providing personalized patient care.'}
          </p>
          <p style="font-size:0.82rem; color:var(--accent-emerald); margin-bottom:1rem;">● Available Monday–Friday, 9:00 AM–5:00 PM</p>
        </div>

        <button class="btn btn-primary btn-book-doc" data-id="${doc.id}" data-name="${doc.user.full_name}" style="width:100%;">
          Book Appointment
        </button>
      </div>
    `).join('');

    // Attach click listeners to booking buttons
    document.querySelectorAll('.btn-book-doc').forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (!state.token) {
          showToast('Please sign in to book an appointment.', 'info');
          document.getElementById('auth-modal')?.classList.add('active');
          return;
        }
        const docId = e.currentTarget.getAttribute('data-id');
        const docName = e.currentTarget.getAttribute('data-name');
        openBookingModal(docId, docName);
      });
    });

  } catch (err) {
    grid.innerHTML = renderErrorState(err.message);
  }
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

  if (btnSearch && inputSpec) {
    btnSearch.addEventListener('click', () => {
      loadDoctors(inputSpec.value);
    });
  }

  if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const doctor_id = document.getElementById('book-doctor-id').value;
      const dateVal = document.getElementById('book-date').value;
      const reason_for_visit = document.getElementById('book-reason').value;

      if (!dateVal) {
        showToast('Please select appointment date and time.', 'error');
        return;
      }

      // Keep the patient-selected local date/time intact; the API validates it against the doctor's local clinic hours.
      const appointment_date = dateVal;

      const btn = document.getElementById('btn-confirm-booking');
      btn.disabled = true;
      btn.textContent = 'Processing...';

      try {
        const payload = await api.post('/appointments/book', { doctor_id, appointment_date, reason_for_visit });
        showToast('Appointment booked successfully!', 'success');
        document.getElementById('booking-modal').classList.remove('active');
        bookingForm.reset();
        state.setView('appointments');
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Confirm & Book Appointment';
      }
    });
  }

  // Initial load
  loadDoctors();
}
