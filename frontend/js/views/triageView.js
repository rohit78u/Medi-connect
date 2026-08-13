import { api } from '../api.js';
import { showToast, renderErrorState } from '../components.js';

export function renderTriageView() {
  return `
    <div class="page-header">
      <h1 class="page-title">AI Clinical Assistant</h1>
      <p class="page-subtitle">Powered by Google Gemini API & LangChain Medical Engine</p>
    </div>

    <div class="grid-2">
      <!-- Symptom Analysis Form -->
      <div class="card">
        <h3 style="margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;">
          <span>🩺</span> Symptom Analysis & Triage
        </h3>
        <form id="triage-form">
          <div class="form-group">
            <label class="form-label">Describe Symptoms</label>
            <textarea id="symptom-text" class="form-control" rows="4" placeholder="e.g. Persistent dry cough, mild fever 100F, chest tightness for 3 days..." required></textarea>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Patient Age</label>
              <input type="number" id="patient-age" class="form-control" placeholder="35" min="0" max="120">
            </div>
            <div class="form-group">
              <label class="form-label">Gender</label>
              <select id="patient-gender" class="form-control">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
          <button type="submit" class="btn btn-primary" id="btn-analyze" style="width:100%;">
            <span>✨ Run AI Clinical Analysis</span>
          </button>
        </form>
      </div>

      <!-- Triage Results Card -->
      <div class="card" id="triage-results-card">
        <h3 style="margin-bottom:1rem;">Assessment Output</h3>
        <div id="triage-output-content" class="empty-state" style="padding:2rem;">
          <div class="state-icon">🤖</div>
          <p>Submit symptoms on the left to generate an AI clinical triage report.</p>
        </div>
      </div>
    </div>

    <!-- Medical Document Parser Section -->
    <div class="card" style="margin-top:2rem;">
      <h3 style="margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;">
        <span>📄</span> Medical Lab Report Parser
      </h3>
      <form id="report-parser-form">
        <div class="form-group">
          <label class="form-label">Paste Unstructured Lab Report Text</label>
          <textarea id="report-text" class="form-control" rows="3" placeholder="Paste CBC, Lipid Panel, or Metabolic Panel text here..." required></textarea>
        </div>
        <button type="submit" class="btn btn-secondary" id="btn-parse-report">Parse Lab Metrics</button>
      </form>

      <div id="report-output-content" style="margin-top:1.5rem;"></div>
    </div>
  `;
}

export function initTriageListeners() {
  const triageForm = document.getElementById('triage-form');
  const reportForm = document.getElementById('report-parser-form');
  const resultsContent = document.getElementById('triage-output-content');
  const reportOutputContent = document.getElementById('report-output-content');

  if (triageForm) {
    triageForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('btn-analyze');
      btn.disabled = true;
      btn.innerHTML = `<span>⏳ Analyzing with Gemini AI...</span>`;

      const symptoms = document.getElementById('symptom-text').value;
      const patient_age = parseInt(document.getElementById('patient-age').value) || 30;
      const gender = document.getElementById('patient-gender').value;

      try {
        const payload = await api.post('/ai/analyze-symptoms', { symptoms, patient_age, gender });
        const res = payload.data;

        resultsContent.className = '';
        resultsContent.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <span class="triage-badge ${res.triage_level}">${res.triage_level} PRIORITY</span>
            <span style="font-weight:600; color:var(--accent-cyan);">${res.recommended_specialization}</span>
          </div>

          <div style="margin-bottom:1rem;">
            <h4 style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:0.35rem;">Clinical Summary</h4>
            <p style="font-size:0.95rem;">${res.clinical_summary}</p>
          </div>

          <div style="margin-bottom:1rem;">
            <h4 style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:0.35rem;">Possible Conditions Identified</h4>
            <ul style="padding-left:1.25rem;">
              ${res.possible_conditions.map(c => `<li style="margin-bottom:0.25rem;">${c}</li>`).join('')}
            </ul>
          </div>

          <div style="padding:0.75rem; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:var(--radius-md); font-size:0.8rem; color:var(--accent-rose);">
            ⚠️ ${res.disclaimer}
          </div>
        `;
        showToast('AI Clinical Triage Analysis Completed', 'success');
      } catch (err) {
        resultsContent.innerHTML = renderErrorState(err.message);
        showToast(err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>✨ Run AI Clinical Analysis</span>`;
      }
    });
  }

  if (reportForm) {
    reportForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const report_text = document.getElementById('report-text').value;

      try {
        const payload = await api.post('/ai/parse-medical-report', { report_text });
        const res = payload.data;

        reportOutputContent.innerHTML = `
          <div style="padding:1rem; background:var(--bg-secondary); border-radius:var(--radius-md); border:1px solid var(--border-color);">
            <h4 style="margin-bottom:0.5rem;">Parsed ${res.report_type} Highlights</h4>
            <ul style="padding-left:1.25rem; margin-bottom:1rem;">
              ${res.diagnosis_highlights.map(h => `<li>${h}</li>`).join('')}
            </ul>
            <h5 style="margin-bottom:0.35rem; color:var(--accent-emerald);">Recommended Actions</h5>
            <ul style="padding-left:1.25rem;">
              ${res.recommended_actions.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>
        `;
        showToast('Report parsed successfully', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
}
