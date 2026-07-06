(function () {
  'use strict';

  const EXAM_KEY_PREFIX = 'ssc_exam_';
  let state = {
    examId: null,
    examToken: null,
    mode: null,
    questions: [],
    answers: {},
    marked: {},
    currentIndex: 0,
    startedAt: null,
    elapsedSeconds: 0,
    questionTimeSpent: {}, // Maps questionId -> accumulated seconds
  };

  let timerInterval = null;
  let currentQuestionStartTime = null;

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ── Timer ──
  function startTimer() {
    updateTimerDisplay();
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      state.elapsedSeconds++;
      updateTimerDisplay();
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
  }

  function updateTimerDisplay() {
    const m = String(Math.floor(state.elapsedSeconds / 60)).padStart(2, '0');
    const s = String(state.elapsedSeconds % 60).padStart(2, '0');
    const el = $('#exam-timer');
    if (el) el.textContent = `${m}:${s}`;
  }

  function saveCurrentQuestionTime() {
    if (!state.questions.length) return;
    const currentQ = state.questions[state.currentIndex];
    if (currentQuestionStartTime) {
      const diff = Math.floor((Date.now() - currentQuestionStartTime) / 1000);
      if (!state.questionTimeSpent) state.questionTimeSpent = {};
      state.questionTimeSpent[currentQ.question_id] = (state.questionTimeSpent[currentQ.question_id] || 0) + diff;
    }
    currentQuestionStartTime = Date.now();
  }

  // ── Preflight ──
  async function fetchPreflight() {
    const resp = await fetch('/api/baseline/preflight');
    return resp.json();
  }

  // ── Start exam ──
  async function startExam(mode) {
    const resp = await fetch('/api/baseline/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      showError('Failed to start exam: ' + (err.detail || resp.statusText));
      return null;
    }
    return resp.json();
  }

  // ── Submit exam ──
  async function submitExam() {
    const endedAt = new Date().toISOString();
    const submissionAnswers = state.questions.map((q) => ({
      question_id: q.question_id,
      user_answer: state.answers[q.question_id] || null,
      time_spent_seconds: state.questionTimeSpent?.[q.question_id] || 0,
      marked_for_review: !!state.marked[q.question_id],
    }));

    const resp = await fetch('/api/baseline/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exam_id: state.examId,
        exam_token: state.examToken,
        mode: state.mode,
        started_at: state.startedAt,
        ended_at: endedAt,
        answers: submissionAnswers,
      }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      showError('Submit failed: ' + (err.detail || resp.statusText));
      return null;
    }
    return resp.json();
  }

  // ── UI Helpers ──
  function showError(msg) {
    const banner = $('#error-banner');
    const msgEl = $('#error-message');
    if (banner && msgEl) {
      msgEl.textContent = msg;
      banner.classList.remove('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      alert(msg);
    }
  }

  function hideError() {
    const banner = $('#error-banner');
    if (banner) banner.classList.add('hidden');
  }

  function showSection(id) {
    const sections = ['#preflight-section', '#exam-section', '#result-section'];
    sections.forEach((sel) => {
      const el = $(sel);
      if (el) {
        el.style.display = 'none';
        el.classList.add('hidden');
      }
    });
    const target = $(id);
    if (target) {
      target.style.display = 'block';
      target.classList.remove('hidden');
    }
  }

  // ── UI: render exam ──
  function renderExam() {
    showSection('#exam-section');
    const badge = $('#exam-mode-badge');
    if (badge) {
      badge.textContent = state.mode === 'full' ? 'FULL BASELINE (200Q)' : 'SMOKE TEST (5Q)';
    }
    renderQuestion();
    renderNav();
    startTimer();
  }

  function renderQuestion() {
    const q = state.questions[state.currentIndex];
    if (!q) return;

    const area = $('#question-area');
    area.innerHTML = `
      <div class="q-meta">
        <div class="q-meta-left">
          <span class="q-index-title">Question ${state.currentIndex + 1} of ${state.questions.length}</span>
          <span class="q-badge">${escapeHtml(q.section)}</span>
          <span class="q-badge" style="text-transform: capitalize;">${escapeHtml(q.tier)}</span>
        </div>
      </div>
      <div class="q-text">${escapeHtml(q.question_text)}</div>
      <div class="q-options" id="options-area">
        ${q.options.map((o) => `
          <label class="option-row ${state.answers[q.question_id] === o.label ? 'selected' : ''}" data-value="${escapeHtml(o.label)}">
            <input type="radio" name="option" value="${escapeHtml(o.label)}" ${state.answers[q.question_id] === o.label ? 'checked' : ''}>
            <span class="option-label" style="font-family: var(--font-mono); font-weight: 700; width: 32px; height: 32px; border-radius: 50%; background-color: var(--bg-paper); border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: center; margin-right: 1.25rem; flex-shrink: 0; transition: var(--transition);">${escapeHtml(o.label)}</span>
            <span>${escapeHtml(o.text)}</span>
          </label>
        `).join('')}
      </div>
    `;

    // Option click handler
    area.querySelectorAll('.option-row').forEach((row) => {
      row.addEventListener('click', () => {
        area.querySelectorAll('.option-row').forEach((r) => r.classList.remove('selected'));
        row.classList.add('selected');
        const input = row.querySelector('input');
        input.checked = true;
        state.answers[q.question_id] = input.value;
        saveDraft();
        renderNav();
      });
    });

    updateNavActive();

    // Previous / Next button states
    const btnPrev = $('#btn-prev');
    const btnNext = $('#btn-next');
    if (btnPrev) btnPrev.disabled = state.currentIndex === 0;
    if (btnNext) btnNext.disabled = state.currentIndex === state.questions.length - 1;

    // Update Mark for review button active style
    const btnMark = $('#btn-mark');
    if (btnMark) {
      if (state.marked[q.question_id]) {
        btnMark.classList.add('btn-primary');
        btnMark.classList.remove('btn-amber');
        btnMark.textContent = '✓ Marked for Review';
      } else {
        btnMark.classList.remove('btn-primary');
        btnMark.classList.add('btn-amber');
        btnMark.textContent = 'Mark for Review';
      }
    }
  }

  function renderNav() {
    const grid = $('#nav-grid');
    if (!grid) return;
    grid.innerHTML = state.questions
      .map((q, i) => {
        const classes = ['nav-dot'];
        if (i === state.currentIndex) classes.push('current');
        if (state.answers[q.question_id]) classes.push('answered');
        if (state.marked[q.question_id]) classes.push('marked');
        return `<div class="${classes.join(' ')}" data-index="${i}">${i + 1}</div>`;
      })
      .join('');

    grid.querySelectorAll('.nav-dot').forEach((dot) => {
      dot.addEventListener('click', () => {
        saveCurrentQuestionTime();
        state.currentIndex = parseInt(dot.dataset.index, 10);
        currentQuestionStartTime = Date.now();
        renderQuestion();
      });
    });
  }

  function updateNavActive() {
    const dots = $$('.nav-dot');
    dots.forEach((d, i) => {
      d.classList.toggle('current', i === state.currentIndex);
      d.classList.toggle('answered', !!state.answers[state.questions[i]?.question_id]);
      d.classList.toggle('marked', !!state.marked[state.questions[i]?.question_id]);
    });
  }

  // ── UI: render result ──
  function renderResult(result) {
    showSection('#result-section');
    stopTimer();

    const percent = Math.round(result.accuracy * 100);
    const scorePctEl = $('#result-score-percent');
    if (scorePctEl) scorePctEl.textContent = `${percent}%`;
    const scoreFractionEl = $('#result-score-fraction');
    if (scoreFractionEl) scoreFractionEl.textContent = `${result.correct_count} / ${result.question_count} Correct`;

    const summary = $('#result-summary');
    if (summary) {
      summary.innerHTML = `
        <table class="result-table">
          <thead>
            <tr>
              <th>Section</th>
              <th>Correct</th>
              <th>Total</th>
              <th>Accuracy</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(result.by_section || {}).map(([section, data]) => {
              const secPct = data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0;
              return `
                <tr>
                  <td><strong>${escapeHtml(section)}</strong></td>
                  <td class="font-mono">${data.correct}</td>
                  <td class="font-mono">${data.total}</td>
                  <td class="font-mono">${secPct}%</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
    }

    const nextStepsContent = $('#next-steps-content');
    if (nextStepsContent) {
      let weakSections = [];
      Object.entries(result.by_section || {}).forEach(([section, data]) => {
        const pct = data.total > 0 ? (data.correct / data.total) : 0;
        if (pct < 0.70) {
          weakSections.push({ name: section, pct: pct, correct: data.correct, total: data.total });
        }
      });
      
      let html = '';
      
      if (result.mode === 'smoke') {
        html += `
          <div class="next-step-box warning" style="border-left: 4px solid var(--color-warning); padding: 1rem; background: var(--color-warning-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
            <p><strong>Note:</strong> This was a 5-question <strong>Smoke Test</strong>. Although your attempts have been successfully saved, a 5-question test is too small to unlock the daily scheduler or boss fights.</p>
            <p style="margin-top: 0.5rem;"><strong>Recommended Next Action:</strong> Return to the landing page and start the <strong>Full Baseline (200 Questions)</strong> once your database is eligible.</p>
          </div>
        `;
      } else {
        html += `
          <div class="next-step-box success" style="border-left: 4px solid var(--color-success); padding: 1rem; background: var(--color-success-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
            <p><strong>Baseline Completed:</strong> Your 200-question Phase 1 Foundation Baseline Exam has been successfully submitted and saved to the SQLite database. Spaced repetition (SM-2) review states have been initialized for these questions.</p>
          </div>
        `;
      }
      
      if (weakSections.length > 0) {
        html += `
          <div style="margin-bottom: 1.5rem;">
            <h4 style="font-weight: 600; color: var(--color-error); margin-bottom: 0.5rem;">Weak Areas Detected (&lt; 70% Accuracy)</h4>
            <p style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 0.75rem;">According to <strong>Plan.md</strong>, sections below the 70% timed accuracy gate require remediation and cannot unlock boss fights immediately.</p>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
              ${weakSections.map(ws => `
                <li style="margin-bottom: 0.25rem;">
                  <strong>${escapeHtml(ws.name)}:</strong> ${(ws.pct * 100).toFixed(0)}% accuracy (${ws.correct} / ${ws.total} correct)
                </li>
              `).join('')}
            </ul>
          </div>
          
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="background: var(--bg-paper); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius);">
              <h5 style="font-weight: 600; margin-bottom: 0.25rem;">1. Run Diagnostic Grinding</h5>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Probe your weak sections and archetypes on the command line to begin targeted grinding:</p>
              <code style="font-family: var(--font-mono); font-size: 0.85rem; background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; display: block; overflow-x: auto;">ssc-study phase3</code>
            </div>
            
            <div style="background: var(--bg-paper); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius);">
              <h5 style="font-weight: 600; margin-bottom: 0.25rem;">2. Check Diagnostic Evaluation</h5>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Check the read-only evaluation report to compare predicted paths vs actual recent outcomes:</p>
              <code style="font-family: var(--font-mono); font-size: 0.85rem; background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; display: block; overflow-x: auto;">ssc-study phase3-eval</code>
            </div>
            
            <div style="background: var(--bg-paper); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius);">
              <h5 style="font-weight: 600; margin-bottom: 0.25rem;">3. View Overall System Readiness</h5>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Monitor your progress across all final-readiness check gates (foundation pulse, archetype floors, CK topic metrics):</p>
              <code style="font-family: var(--font-mono); font-size: 0.85rem; background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; display: block; overflow-x: auto;">ssc-study readiness</code>
            </div>
          </div>
        `;
      } else {
        html += `
          <div style="margin-bottom: 1.5rem;">
            <h4 style="font-weight: 600; color: var(--color-success); margin-bottom: 0.5rem;">✓ Foundation Gate Cleared!</h4>
            <p style="font-size: 0.95rem; color: var(--text-secondary);">All sections meet or exceed the 70% timed accuracy threshold. You have unlocked standard daily scheduling and boss fight queues.</p>
          </div>
          
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="background: var(--bg-paper); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius);">
              <h5 style="font-weight: 600; margin-bottom: 0.25rem;">1. View Daily Grind Schedule</h5>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Display your exact daily 180-minute schedule (SM-2 reviews, boss fights, memory queues, English blocks):</p>
              <code style="font-family: var(--font-mono); font-size: 0.85rem; background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; display: block; overflow-x: auto;">ssc-study guardian plan</code>
            </div>
            
            <div style="background: var(--bg-paper); border: 1px solid var(--border-color); padding: 1rem; border-radius: var(--border-radius);">
              <h5 style="font-weight: 600; margin-bottom: 0.25rem;">2. Check System Readiness</h5>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Check your status across all system readiness metrics:</p>
              <code style="font-family: var(--font-mono); font-size: 0.85rem; background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; display: block; overflow-x: auto;">ssc-study readiness</code>
            </div>
          </div>
        `;
      }
      
      nextStepsContent.innerHTML = html;
    }
  }

  // ── Draft persistence (localStorage) ──
  function saveDraft() {
    if (!state.examId) return;
    const draft = {
      examId: state.examId,
      examToken: state.examToken,
      mode: state.mode,
      questions: state.questions,
      answers: state.answers,
      marked: state.marked,
      currentIndex: state.currentIndex,
      startedAt: state.startedAt,
      elapsedSeconds: state.elapsedSeconds,
      questionTimeSpent: state.questionTimeSpent,
      savedAt: Date.now()
    };
    try {
      localStorage.setItem(EXAM_KEY_PREFIX + state.examId, JSON.stringify(draft));
    } catch (_) { /* ignore */ }
  }

  function loadDraft(examId) {
    try {
      const raw = localStorage.getItem(EXAM_KEY_PREFIX + examId);
      if (raw) {
        const draft = JSON.parse(raw);
        // Expiry at 24 hours
        if (Date.now() - draft.savedAt > 24 * 60 * 60 * 1000) {
          localStorage.removeItem(EXAM_KEY_PREFIX + examId);
          return false;
        }
        Object.assign(state, draft);
        return true;
      }
    } catch (_) { /* ignore */ }
    return false;
  }

  function loadMostRecentDraft() {
    try {
      const drafts = Object.keys(localStorage)
        .filter((key) => key.startsWith(EXAM_KEY_PREFIX))
        .map((key) => {
          try {
            return JSON.parse(localStorage.getItem(key));
          } catch (_) {
            return null;
          }
        })
        .filter((draft) => draft && draft.examId && Array.isArray(draft.questions));

      drafts.sort((a, b) => (b.savedAt || 0) - (a.savedAt || 0));
      for (const draft of drafts) {
        if (loadDraft(draft.examId)) return true;
      }
    } catch (_) { /* ignore */ }
    return false;
  }

  function clearDraft() {
    if (state.examId) {
      try { localStorage.removeItem(EXAM_KEY_PREFIX + state.examId); } catch (_) {}
    }
  }

  // ── Helpers ──
  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ── Event bindings ──
  document.addEventListener('DOMContentLoaded', async () => {
    // Check error close button
    const errClose = $('#error-close-btn');
    if (errClose) errClose.addEventListener('click', hideError);

    // Check for an in-progress exam in URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const resumeExamId = urlParams.get('exam_id');

    if ((resumeExamId && loadDraft(resumeExamId)) || (!resumeExamId && loadMostRecentDraft())) {
      currentQuestionStartTime = Date.now();
      renderExam();
      return;
    }

    // Load preflight
    try {
      const preflight = await fetchPreflight();
      const btnSmoke = $('#btn-smoke');
      const btnFull = $('#btn-full');
      if (btnSmoke) btnSmoke.disabled = !preflight.smoke_ready;
      if (btnFull) btnFull.disabled = !preflight.full_ready;
    } catch (err) {
      console.error('Preflight failed:', err);
    }

    // Confirmation Modal setup
    const modalCancel = $('#modal-cancel-btn');
    if (modalCancel) {
      modalCancel.addEventListener('click', () => {
        const modal = $('#submit-modal');
        if (modal) modal.classList.add('hidden');
        currentQuestionStartTime = Date.now();
        startTimer();
      });
    }

    const modalConfirm = $('#modal-confirm-btn');
    if (modalConfirm) {
      modalConfirm.addEventListener('click', async () => {
        const modal = $('#submit-modal');
        if (modal) modal.classList.add('hidden');
        saveCurrentQuestionTime();
        const result = await submitExam();
        if (!result) {
          currentQuestionStartTime = Date.now();
          startTimer();
          return;
        }
        clearDraft();
        renderResult(result);
      });
    }

    // Restart button
    const btnRestart = $('#btn-restart');
    if (btnRestart) {
      btnRestart.addEventListener('click', () => {
        location.reload();
      });
    }
  });

  // Start smoke exam
  document.addEventListener('click', async (e) => {
    if (e.target.id === 'btn-smoke' || e.target.closest('#btn-smoke')) {
      const btn = $('#btn-smoke');
      if (btn.disabled) return;
      const data = await startExam('smoke');
      if (!data) return;
      state.examId = data.exam_id;
      state.examToken = data.exam_token;
      state.mode = 'smoke';
      state.questions = data.questions;
      state.answers = {};
      state.marked = {};
      state.currentIndex = 0;
      state.elapsedSeconds = 0;
      state.questionTimeSpent = {};
      state.startedAt = new Date().toISOString();
      currentQuestionStartTime = Date.now();
      saveDraft();
      renderExam();
    }
  });

  // Start full exam
  document.addEventListener('click', async (e) => {
    if (e.target.id === 'btn-full' || e.target.closest('#btn-full')) {
      const btn = $('#btn-full');
      if (btn.disabled) return;
      const data = await startExam('full');
      if (!data) return;
      state.examId = data.exam_id;
      state.examToken = data.exam_token;
      state.mode = 'full';
      state.questions = data.questions;
      state.answers = {};
      state.marked = {};
      state.currentIndex = 0;
      state.elapsedSeconds = 0;
      state.questionTimeSpent = {};
      state.startedAt = new Date().toISOString();
      currentQuestionStartTime = Date.now();
      saveDraft();
      renderExam();
    }
  });

  // Navigation
  document.addEventListener('click', (e) => {
    if (e.target.id === 'btn-next') {
      if (state.currentIndex < state.questions.length - 1) {
        saveCurrentQuestionTime();
        state.currentIndex++;
        currentQuestionStartTime = Date.now();
        renderQuestion();
        saveDraft();
      }
    }
    if (e.target.id === 'btn-prev') {
      if (state.currentIndex > 0) {
        saveCurrentQuestionTime();
        state.currentIndex--;
        currentQuestionStartTime = Date.now();
        renderQuestion();
        saveDraft();
      }
    }
    if (e.target.id === 'btn-mark') {
      const q = state.questions[state.currentIndex];
      if (q) {
        if (state.marked[q.question_id]) {
          delete state.marked[q.question_id];
        } else {
          state.marked[q.question_id] = true;
        }
        saveDraft();
        renderQuestion();
        renderNav();
      }
    }
  });

  // Submit Exam triggers confirmation modal
  document.addEventListener('click', (e) => {
    if (e.target.id === 'btn-submit') {
      stopTimer();
      saveCurrentQuestionTime();
      
      const unanswered = state.questions.filter((q) => !state.answers[q.question_id]).length;
      const modal = $('#submit-modal');
      const warningText = $('#modal-warning-text');
      
      if (modal && warningText) {
        if (unanswered > 0) {
          warningText.innerHTML = `You have <strong style="color:var(--color-warning);">${unanswered}</strong> unanswered question(s) out of ${state.questions.length} total. Are you sure you want to submit?`;
        } else {
          warningText.innerHTML = `All questions answered. Are you sure you want to submit the exam?`;
        }
        modal.classList.remove('hidden');
      } else {
        // Fallback to confirm box if modal elements are missing
        if (unanswered > 0) {
          if (!confirm(`${unanswered} question(s) unanswered. Submit anyway?`)) {
            startTimer();
            return;
          }
        } else {
          if (!confirm('Submit exam?')) {
            startTimer();
            return;
          }
        }
        submitExam().then(result => {
          if (!result) {
            currentQuestionStartTime = Date.now();
            startTimer();
            return;
          }
          if (result) {
            clearDraft();
            renderResult(result);
          }
        });
      }
    }
  });

})();
