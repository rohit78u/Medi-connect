import { api } from '../api.js';
import { showToast, renderErrorState } from '../components.js';

export function renderTriageView() {
  return `
    <div class="page-header">
      <span class="eyebrow">AI CLINICAL ASSISTANT</span>
      <h1 class="page-title">AI Clinical Assistant</h1>
      <p class="page-subtitle">Powered by Google Gemini API & LangChain Medical Engine</p>
    </div>

    <div class="grid-2">
      <div class="card triage-card">
        <h3><span>♧</span> Symptom Analysis & Triage</h3>
        <form id="triage-form">
          <div class="form-group">
            <label class="form-label">Describe Symptoms</label>
            <textarea id="symptom-text" class="form-control" rows="4" placeholder="e.g. Persistent dry cough, mild fever 100F, chest tightness for 3 days..." required></textarea>
          </div>
          <div class="grid-2" style="gap:14px;">
            <div class="form-group">
              <label class="form-label">Patient Age</label>
              <input type="number" id="patient-age" class="form-control" placeholder="35" min="0" max="120">
            </div>
            <div class="form-group">
              <label class="form-label">Gender</label>
              <select id="patient-gender" class="form-control"><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select>
            </div>
          </div>
          <button type="submit" class="btn btn-primary" id="btn-analyze"><span>✦ Run AI Clinical Analysis</span></button>
        </form>
      </div>

      <div class="card assessment-card" id="triage-results-card">
        <h3>Assessment Output</h3>
        <div id="triage-output-content" class="empty-state" style="min-height:200px;border:1px solid var(--border);">
          <div class="state-icon">▣</div>
          <p>Submit symptoms on the left to generate an AI clinical triage report.</p>
        </div>
      </div>
    </div>

    <div class="card report-card">
      <h3><span>▤</span> Medical Lab Report Parser</h3>
      <form id="report-parser-form">
        <div class="form-group">
          <label class="form-label">Paste Unstructured Lab Report Text</label>
          <textarea id="report-text" class="form-control" rows="3" placeholder="Paste CBC, Lipid Panel, or Metabolic Panel text here..." required></textarea>
        </div>
        <button type="submit" class="btn btn-secondary" id="btn-parse-report">Parse Lab Metrics</button>
      </form>
      <div id="report-output-content"></div>
    </div>
  `;
}

export function initTriageListeners() {
  const triageForm = document.getElementById('triage-form');
  const reportForm = document.getElementById('report-parser-form');
  const resultsContent = document.getElementById('triage-output-content');
  const reportOutputContent = document.getElementById('report-output-content');

  triageForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = document.getElementById('btn-analyze');
    btn.disabled = true;
    btn.innerHTML = '<span>Analyzing with Gemini AI...</span>';
    const symptoms = document.getElementById('symptom-text').value;
    const patient_age = parseInt(document.getElementById('patient-age').value) || 30;
    const gender = document.getElementById('patient-gender').value;
    try {
      const payload = await api.post('/ai/analyze-symptoms', { symptoms, patient_age, gender });
      const res = payload.data;
      resultsContent.className = '';
      resultsContent.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;gap:12px"><span class="triage-badge ${res.triage_level}">${res.triage_level} PRIORITY</span><strong style="color:var(--brand);font-size:13px">${res.recommended_specialization}</strong></div><div style="margin-bottom:16px"><h4 style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">Clinical Summary</h4><p style="font-size:13px">${res.clinical_summary}</p></div><div style="margin-bottom:16px"><h4 style="font-size:12px;color:var(--text-secondary);margin-bottom:5px">Possible Conditions Identified</h4><ul style="padding-left:18px;font-size:13px">${res.possible_conditions.map(c => `<li style="margin-bottom:4px">${c}</li>`).join('')}</ul></div><div style="padding:11px;background:var(--danger-soft);border:1px solid #f4cccc;border-radius:8px;font-size:11px;color:var(--danger)">⚠ ${res.disclaimer}</div>`;
      showToast('AI Clinical Triage Analysis Completed','success');
    } catch (err) { resultsContent.innerHTML = renderErrorState(err.message); showToast(err.message,'error'); }
    finally { btn.disabled=false; btn.innerHTML='<span>✦ Run AI Clinical Analysis</span>'; }
  });

  reportForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const report_text = document.getElementById('report-text').value;
    try {
      const payload = await api.post('/ai/parse-medical-report',{report_text});
      const res = payload.data;
      reportOutputContent.innerHTML = `<div class="report-output"><h4 style="margin-bottom:8px">Parsed ${res.report_type} Highlights</h4><ul style="padding-left:18px;margin-bottom:15px;font-size:13px">${res.diagnosis_highlights.map(h=>`<li>${h}</li>`).join('')}</ul><h5 style="margin-bottom:5px;color:var(--success)">Recommended Actions</h5><ul style="padding-left:18px;font-size:13px">${res.recommended_actions.map(a=>`<li>${a}</li>`).join('')}</ul></div>`;
      showToast('Report parsed successfully','success');
    } catch(err) { showToast(err.message,'error'); }
  });
}
