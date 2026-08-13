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
        <button class="btn btn-primary" id="btn-submit-payment" style="width:100%;">💳 Pay securely via Razorpay</button>
      </div>
    </div>
  `;
}

let activePaymentData = null;

export async function openPaymentModal(appointment_id) {
  const modal = document.getElementById('payment-modal');
  if (!modal) return;

  try {
    // Amount is intentionally omitted. The backend calculates it from the doctor's fee.
    const payload = await api.post('/payments/create-order', { appointment_id, currency: 'INR' });
    activePaymentData = payload.data;

    document.getElementById('pay-amount-display').textContent = `₹${Number(activePaymentData.amount).toFixed(2)}`;
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
    if (!activePaymentData || !window.Razorpay) {
      showToast('Razorpay Checkout is unavailable. Please refresh and try again.', 'error');
      return;
    }

    btnPay.disabled = true;
    btnPay.textContent = 'Opening secure checkout...';

    const options = {
      key: activePaymentData.razorpay_key_id,
      amount: Math.round(Number(activePaymentData.amount) * 100),
      currency: activePaymentData.currency,
      name: 'MediConnect AI',
      description: 'Medical consultation',
      order_id: activePaymentData.razorpay_order_id,
      theme: { color: '#0f766e' },
      handler: async (response) => {
        try {
          await api.post('/payments/verify', {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
          showToast('Payment verified successfully! Appointment confirmed.', 'success');
          document.getElementById('payment-modal').classList.remove('active');
          await loadAppointments();
        } catch (err) {
          showToast(err.message, 'error');
        } finally {
          btnPay.disabled = false;
          btnPay.textContent = '💳 Pay securely via Razorpay';
        }
      },
      modal: {
        ondismiss: () => {
          btnPay.disabled = false;
          btnPay.textContent = '💳 Pay securely via Razorpay';
        },
      },
    };

    try {
      const razorpay = new window.Razorpay(options);
      razorpay.on('payment.failed', (response) => {
        showToast(response.error?.description || 'Payment failed.', 'error');
        btnPay.disabled = false;
        btnPay.textContent = '💳 Pay securely via Razorpay';
      });
      razorpay.open();
    } catch (err) {
      showToast('Unable to open Razorpay Checkout.', 'error');
      btnPay.disabled = false;
      btnPay.textContent = '💳 Pay securely via Razorpay';
    }
  });
}
