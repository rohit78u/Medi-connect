import { api } from '../api.js';
import { showToast } from '../components.js';
import { loadAppointments } from './appointmentsView.js';

export function renderPaymentModal() {
  return `
    <div class="modal-overlay" id="payment-modal">
      <div class="modal-card">
        <div class="modal-header">
          <h2>Razorpay Consultation Checkout</h2>
          <button class="modal-close" onclick="document.getElementById('payment-modal').classList.remove('active')">&times;</button>
        </div>

        <div style="text-align:center; margin-bottom:1.5rem;">
          <p class="page-subtitle">Total Consultation Fee</p>
          <h1 style="font-size:2.5rem; color:var(--accent-emerald);" id="pay-amount-display">₹0.00</h1>
        </div>

        <div style="padding:1rem; background:var(--bg-primary); border-radius:var(--radius-md); margin-bottom:1.5rem; border:1px solid var(--border-color);">
          <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.5rem;">Order Details:</p>
          <p style="font-size:0.9rem;">Order ID: <strong id="pay-order-id">-</strong></p>
        </div>

        <button class="btn btn-primary" id="btn-submit-payment" style="width:100%;">
          💳 Confirm & Pay via Razorpay
        </button>
      </div>
    </div>
  `;
}

let activePaymentData = null;

export async function openPaymentModal(appointment_id, amount) {
  const modal = document.getElementById('payment-modal');
  if (!modal) return;

  try {
    const payload = await api.post('/payments/create-order', { appointment_id, amount, currency: 'INR' });
    activePaymentData = payload.data;

    document.getElementById('pay-amount-display').textContent = `₹${amount.toFixed(2)}`;
    document.getElementById('pay-order-id').textContent = activePaymentData.razorpay_order_id;
    modal.classList.add('active');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

export function initPaymentListeners() {
  const btnPay = document.getElementById('btn-submit-payment');
  if (!btnPay) return;

  btnPay.addEventListener('click', async () => {
    if (!activePaymentData) return;

    btnPay.disabled = true;
    btnPay.textContent = 'Verifying HMAC Signature...';

    // Simulate Razorpay Gateway Payment ID & Signature calculation for verification
    const razorpay_payment_id = `pay_rzp_${Math.random().toString(36).substr(2, 9)}`;
    // The backend mock verifies signature matching test format or passes verification
    const razorpay_signature = 'rzp_test_signature_valid';

    try {
      await api.post('/payments/verify', {
        razorpay_order_id: activePaymentData.razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
      });

      showToast('Payment verified successfully! Appointment confirmed.', 'success');
      document.getElementById('payment-modal').classList.remove('active');
      loadAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btnPay.disabled = false;
      btnPay.textContent = '💳 Confirm & Pay via Razorpay';
    }
  });
}
