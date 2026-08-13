import { api } from '../api.js';
import { state } from '../state.js';
import { showToast } from '../components.js';

export function renderAuthModal() {
  return `
    <div class="modal-overlay active" id="auth-modal">
      <div class="modal-card">
        <div class="modal-header">
          <h2 id="auth-title">Welcome to MediConnect AI</h2>
          <button class="modal-close" onclick="document.getElementById('auth-modal').classList.remove('active')">&times;</button>
        </div>

        <!-- Toggle Tabs -->
        <div style="display:flex; gap:1rem; margin-bottom:1.5rem; border-bottom:1px solid var(--border-color); pb:0.5rem;">
          <button class="btn btn-secondary" id="tab-login" style="flex:1;">Sign In</button>
          <button class="btn btn-secondary" id="tab-register" style="flex:1;">Create Account</button>
        </div>

        <!-- Login Form -->
        <form id="login-form">
          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input type="email" id="login-email" class="form-control" placeholder="doctor@mediconnect.ai" required>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" id="login-password" class="form-control" placeholder="••••••••" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">Sign In</button>
        </form>

        <!-- Register Form (Hidden by default) -->
        <form id="register-form" style="display:none;">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input type="text" id="reg-name" class="form-control" placeholder="Dr. Jane Smith" required>
          </div>
          <div class="form-group">
            <label class="form-label">Email Address</label>
            <input type="email" id="reg-email" class="form-control" placeholder="jane@mediconnect.ai" required>
          </div>
          <div class="form-group">
            <label class="form-label">Password (Min 8 chars)</label>
            <input type="password" id="reg-password" class="form-control" minlength="8" required>
          </div>
          <div class="form-group">
            <label class="form-label">Select Account Role</label>
            <select id="reg-role" class="form-control">
              <option value="PATIENT">Patient</option>
              <option value="DOCTOR">Doctor / Clinician</option>
              <option value="ADMIN">Hospital Administrator</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">Create Account</button>
        </form>
      </div>
    </div>
  `;
}

export function initAuthListeners() {
  const loginForm = document.getElementById('login-form');
  const regForm = document.getElementById('register-form');
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');

  if (tabLogin && tabRegister) {
    tabLogin.addEventListener('click', () => {
      loginForm.style.display = 'block';
      regForm.style.display = 'none';
      tabLogin.classList.add('btn-primary');
      tabRegister.classList.remove('btn-primary');
    });

    tabRegister.addEventListener('click', () => {
      loginForm.style.display = 'none';
      regForm.style.display = 'block';
      tabRegister.classList.add('btn-primary');
      tabLogin.classList.remove('btn-primary');
    });
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;

      try {
        const payload = await api.post('/auth/login', { email, password });
        state.setUser(payload.data.user, payload.data.access_token, payload.data.refresh_token);
        showToast(`Welcome back, ${payload.data.user.full_name}!`, 'success');
        document.getElementById('auth-modal')?.classList.remove('active');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  if (regForm) {
    regForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const full_name = document.getElementById('reg-name').value;
      const email = document.getElementById('reg-email').value;
      const password = document.getElementById('reg-password').value;
      const role_name = document.getElementById('reg-role').value;

      try {
        const payload = await api.post('/auth/register', { full_name, email, password, role_name });
        showToast('Registration successful! Please sign in.', 'success');
        tabLogin.click();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
}
