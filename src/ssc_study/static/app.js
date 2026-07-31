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
  function renderQuestionAsset(q) {
    const urls = q.asset_urls || {};
    const src = urls.crop || urls.page;
    if (!src) return '';
    return `
      <div class="q-asset-block">
        <div class="q-asset-label">Visual reference</div>
        <img class="q-asset-image" src="${escapeHtml(src)}" alt="Question visual reference">
        <div class="q-asset-error hidden">Image failed to load. Report this question before using the baseline score.</div>
      </div>
    `;
  }

  function renderPassage(q) {
    if (!q.passage_text) return '';
    return `
      <div class="baseline-passage">
        <div class="baseline-passage-label">Passage</div>
        <div class="baseline-passage-text">${escapeHtml(q.passage_text)}</div>
      </div>
    `;
  }

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
      ${renderQuestionAsset(q)}
      ${renderPassage(q)}
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

    const assetImage = area.querySelector('.q-asset-image');
    if (assetImage) {
      assetImage.addEventListener('error', () => {
        assetImage.classList.add('hidden');
        const error = area.querySelector('.q-asset-error');
        if (error) error.classList.remove('hidden');
      });
    }

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

  function buildSmokeNextStepsHtml() {
    return `
      <div class="next-step-box warning" style="border-left: 4px solid var(--color-warning); padding: 1rem; background: var(--color-warning-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
        <p><strong>Note:</strong> This was a 5-question <strong>Smoke Test</strong>. Although your attempts have been successfully saved, a 5-question test is too small to unlock the daily scheduler or boss fights.</p>
        <p style="margin-top: 0.5rem;"><strong>Recommended Next Action:</strong> Return to the landing page and start the <strong>Full Baseline (200 Questions)</strong> once your database is eligible.</p>
      </div>
    `;
  }

  function buildFullBaselineNextStepsHtml(result, ns) {
    function renderSectionAction(ws) {
      if (ws.action && ws.action.action_type !== 'stop') {
        const name = ws.action.target_archetype_name || 'unknown archetype';
        return ` <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
          ↳ Next diagnostic target: ${escapeHtml(ws.action.action_type)} on <strong>${escapeHtml(name)}</strong> (${escapeHtml(ws.action.reason)})
        </span>`;
      }
      return ` <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
        ↳ No active archetypes eligible to probe.
      </span>`;
    }

    const excluded = ns.weak_sections.filter(function(ws) { return ws.tier === 'remediation_excluded'; });
    const priority = ns.weak_sections.filter(function(ws) { return ws.tier === 'remediation_priority'; });
    const paired = ns.weak_sections.filter(function(ws) { return ws.tier === 'paired_remediation'; });

    let bucketsHtml = '';

    if (excluded.length > 0) {
      bucketsHtml += `
        <div style="margin-bottom: 1rem;">
          <h4 style="font-weight: 600; color: var(--color-error); margin-bottom: 0.25rem;">Remediation-First Priority (&lt; 55% Accuracy)</h4>
          <ul class="dashboard-list">
            ${excluded.map(function(ws) { return `
              <li class="error">
                <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                ${renderSectionAction(ws)}
              </li>
            `;}).join('')}
          </ul>
        </div>
      `;
    }

    if (priority.length > 0) {
      bucketsHtml += `
        <div style="margin-bottom: 1rem;">
          <h4 style="font-weight: 600; color: var(--color-error); margin-bottom: 0.25rem;">Remediation Priority (55–64% Accuracy)</h4>
          <ul class="dashboard-list">
            ${priority.map(function(ws) { return `
              <li class="error">
                <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                ${renderSectionAction(ws)}
              </li>
            `;}).join('')}
          </ul>
        </div>
      `;
    }

    if (paired.length > 0) {
      bucketsHtml += `
        <div style="margin-bottom: 1rem;">
          <h4 style="font-weight: 600; color: var(--color-warning); margin-bottom: 0.25rem;">Boss Fight with Paired Remediation (65–69% Accuracy)</h4>
          <ul class="dashboard-list">
            ${paired.map(function(ws) { return `
              <li class="warning">
                <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                ${renderSectionAction(ws)}
              </li>
            `;}).join('')}
          </ul>
        </div>
      `;
    }

    const weakSectionsList = (ns.weak_sections || []).map(function(ws) { return ws.section; });
    const cleared = ['Quant/DI', 'Reasoning', 'English', 'GK/GA'].filter(function(sec) {
      return weakSectionsList.indexOf(sec) === -1;
    });

    if (cleared.length > 0) {
      bucketsHtml += `
        <div style="margin-bottom: 1rem;">
          <h4 style="font-weight: 600; color: var(--color-success); margin-bottom: 0.25rem;">Boss Fights Unlocked (&ge; 70% Accuracy)</h4>
          <ul class="dashboard-list">
            ${cleared.map(function(section) {
              const secData = result.by_section?.[section] || { correct: 0, total: 0 };
              const acc = secData.total > 0 ? (secData.correct / secData.total) : 0;
              return `
                <li class="success">
                  <strong>${escapeHtml(section)}</strong>: ${(acc * 100).toFixed(0)}% (${secData.correct}/${secData.total})
                  <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
                    ↳ Timed boss fights unlocked!
                  </span>
                </li>
              `;
            }).join('')}
          </ul>
        </div>
      `;
    }

    return `
      <div class="next-step-box success" style="border-left: 4px solid var(--color-success); padding: 1rem; background: var(--color-success-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
        <p><strong>Baseline Completed:</strong> Your 200-question Phase 1 Foundation Baseline Exam has been successfully submitted and saved. Spaced repetition (SM-2) review states have been initialized.</p>
      </div>

      <div class="next-step-box warning" style="border-left: 4px solid var(--color-warning); padding: 1rem; background: var(--color-warning-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
        <p><strong>Important Advisory / CLI-Only Scope:</strong> Today's manual baseline run is complete. The dashboard recommendations and next-step schedules displayed below are <strong>advisory-only</strong>. To run Phase 3 diagnostics or Phase 4 daily study loops, you must execute the recommended commands using the command-line interface (CLI) in your terminal.</p>
      </div>

      <div class="dashboard-grid">
        <div class="dashboard-card">
          <h3>Diagnostic Status Buckets</h3>
          <div>${bucketsHtml}</div>
        </div>

        <div class="dashboard-card" id="card-phase3-next-action">
          <h3>Phase 3 Next Action</h3>
          <p style="color: var(--text-secondary); font-size: 0.9rem;">Loading Phase 3 next target...</p>
        </div>

        <div class="dashboard-card" id="card-guardian-readiness">
          <h3>Guardian & Readiness Summary</h3>
          <p style="color: var(--text-secondary); font-size: 0.9rem;">Loading Guardian planner & readiness state...</p>
        </div>
      </div>
    `;
  }

  // ── UI: render result ──
  function formatMarks(value) {
    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }

  function renderResult(result) {
    showSection('#result-section');
    stopTimer();

    const percent = Math.round(result.accuracy * 100);
    const scorePctEl = $('#result-score-percent');
    if (scorePctEl) scorePctEl.textContent = `${percent}%`;
    const scoreFractionEl = $('#result-score-fraction');
    if (scoreFractionEl) {
      scoreFractionEl.textContent = `${result.correct_count} correct, ${result.wrong_count} wrong, ${result.skipped_count} skipped`;
    }

    const summary = $('#result-summary');
    if (summary) {
      summary.innerHTML = `
        <div class="result-overall-line" style="margin-bottom: 0.9rem; font-size: 0.95rem;">
          <strong>Overall:</strong>
          ${result.correct_count} correct, ${result.wrong_count} wrong, ${result.skipped_count} skipped
          | ${percent}%
          | Marks: ${formatMarks(result.marks_earned)} / ${formatMarks(result.marks_max)}
        </div>
        <table class="result-table">
          <thead>
            <tr>
              <th>Section</th>
              <th>Correct</th>
              <th>Wrong</th>
              <th>Skipped</th>
              <th>Percent</th>
              <th>Marks</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(result.by_section || {}).map(([section, data]) => {
              const secPct = Math.round((data.accuracy || 0) * 100);
              return `
                <tr>
                  <td><strong>${escapeHtml(section)}</strong></td>
                  <td class="font-mono">${data.correct}</td>
                  <td class="font-mono">${data.wrong}</td>
                  <td class="font-mono">${data.skipped}</td>
                  <td class="font-mono">${secPct}%</td>
                  <td class="font-mono">${formatMarks(data.marks_earned)} / ${formatMarks(data.marks_max)}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
    }

    const nextStepsContent = $('#next-steps-content');
    if (nextStepsContent && result.next_steps) {
      const ns = result.next_steps;
      if (ns.mode === 'smoke') {
        nextStepsContent.innerHTML = buildSmokeNextStepsHtml();
        return;
      }
      nextStepsContent.innerHTML = buildFullBaselineNextStepsHtml(result, ns);
      loadAsyncDashboardDetails();
      return;

      let html = '';
      
      // Mode-specific message
      if (ns.mode === 'smoke') {
        html += `
          <div class="next-step-box warning" style="border-left: 4px solid var(--color-warning); padding: 1rem; background: var(--color-warning-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
            <p><strong>Note:</strong> This was a 5-question <strong>Smoke Test</strong>. Although your attempts have been successfully saved, a 5-question test is too small to unlock the daily scheduler or boss fights.</p>
            <p style="margin-top: 0.5rem;"><strong>Recommended Next Action:</strong> Return to the landing page and start the <strong>Full Baseline (200 Questions)</strong> once your database is eligible.</p>
          </div>
        `;
        nextStepsContent.innerHTML = html;
      } else {
        // Helper to render a per-section action line
        function renderSectionAction(ws) {
          if (ws.action && ws.action.action_type !== 'stop') {
            const name = ws.action.target_archetype_name || 'unknown archetype';
            return ` <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
              ↳ Next diagnostic target: ${escapeHtml(ws.action.action_type)} on <strong>${escapeHtml(name)}</strong> (${escapeHtml(ws.action.reason)})
            </span>`;
          }
          return ` <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
            ↳ No active archetypes eligible to probe.
          </span>`;
        }

        // Render weak sections grouped by Plan.md tier
        const excluded = ns.weak_sections.filter(function(ws) { return ws.tier === 'remediation_excluded'; });
        const priority = ns.weak_sections.filter(function(ws) { return ws.tier === 'remediation_priority'; });
        const paired = ns.weak_sections.filter(function(ws) { return ws.tier === 'paired_remediation'; });

        let bucketsHtml = '';

        if (excluded.length > 0) {
          bucketsHtml += `
            <div style="margin-bottom: 1rem;">
              <h4 style="font-weight: 600; color: var(--color-error); margin-bottom: 0.25rem;">Remediation-First Priority (&lt; 55% Accuracy)</h4>
              <ul class="dashboard-list">
                ${excluded.map(function(ws) { return `
                  <li class="error">
                    <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                    ${renderSectionAction(ws)}
                  </li>
                `;}).join('')}
              </ul>
            </div>
          `;
        }

        if (priority.length > 0) {
          bucketsHtml += `
            <div style="margin-bottom: 1rem;">
              <h4 style="font-weight: 600; color: var(--color-error); margin-bottom: 0.25rem;">Remediation Priority (55–64% Accuracy)</h4>
              <ul class="dashboard-list">
                ${priority.map(function(ws) { return `
                  <li class="error">
                    <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                    ${renderSectionAction(ws)}
                  </li>
                `;}).join('')}
              </ul>
            </div>
          `;
        }

        if (paired.length > 0) {
          bucketsHtml += `
            <div style="margin-bottom: 1rem;">
              <h4 style="font-weight: 600; color: var(--color-warning); margin-bottom: 0.25rem;">Boss Fight with Paired Remediation (65–69% Accuracy)</h4>
              <ul class="dashboard-list">
                ${paired.map(function(ws) { return `
                  <li class="warning">
                    <strong>${escapeHtml(ws.section)}</strong>: ${(ws.accuracy * 100).toFixed(0)}% (${ws.correct}/${ws.total})
                    ${renderSectionAction(ws)}
                  </li>
                `;}).join('')}
              </ul>
            </div>
          `;
        }

        // Add cleared sections (boss fights unlocked)
        const weakSectionsList = (ns.weak_sections || []).map(function(ws) { return ws.section; });
        const cleared = ["Quant/DI", "Reasoning", "English", "GK/GA"].filter(function(sec) {
          return weakSectionsList.indexOf(sec) === -1;
        });

        if (cleared.length > 0) {
          bucketsHtml += `
            <div style="margin-bottom: 1rem;">
              <h4 style="font-weight: 600; color: var(--color-success); margin-bottom: 0.25rem;">Boss Fights Unlocked (&ge; 70% Accuracy)</h4>
              <ul class="dashboard-list">
                ${cleared.map(function(section) {
                  const secData = result.by_section?.[section] || { correct: 0, total: 0 };
                  const acc = secData.total > 0 ? (secData.correct / secData.total) : 0;
                  return `
                    <li class="success">
                      <strong>${escapeHtml(section)}</strong>: ${(acc * 100).toFixed(0)}% (${secData.correct}/${secData.total})
                      <span style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.15rem; font-style: italic;">
                        ↳ Timed boss fights unlocked!
                      </span>
                    </li>
                  `;
                }).join('')}
              </ul>
            </div>
          `;
        }

        html += `
          <div class="next-step-box success" style="border-left: 4px solid var(--color-success); padding: 1rem; background: var(--color-success-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
            <p><strong>Baseline Completed:</strong> Your 200-question Phase 1 Foundation Baseline Exam has been successfully submitted and saved. Spaced repetition (SM-2) review states have been initialized.</p>
          </div>

          <div class="next-step-box warning" style="border-left: 4px solid var(--color-warning); padding: 1rem; background: var(--color-warning-light); border-radius: var(--border-radius); margin-bottom: 1.5rem;">
            <p><strong>Important Advisory / CLI-Only Scope:</strong> Today's manual baseline run is complete. The dashboard recommendations and next-step schedules displayed below are <strong>advisory-only</strong>. To run Phase 3 diagnostics or Phase 4 daily study loops, you must execute the recommended commands using the command-line interface (CLI) in your terminal.</p>
          </div>

          <div class="dashboard-grid">
            <!-- Card 1: Diagnostic Status -->
            <div class="dashboard-card">
              <h3>Diagnostic Status Buckets</h3>
              <div>${bucketsHtml}</div>
            </div>

            <!-- Card 2: Phase 3 Next Action -->
            <div class="dashboard-card" id="card-phase3-next-action">
              <h3>Phase 3 Next Action</h3>
              <p style="color: var(--text-secondary); font-size: 0.9rem;">Loading Phase 3 next target...</p>
            </div>

            <!-- Card 3: Guardian & Readiness -->
            <div class="dashboard-card" id="card-guardian-readiness">
              <h3>Guardian & Readiness Summary</h3>
              <p style="color: var(--text-secondary); font-size: 0.9rem;">Loading Guardian planner & readiness state...</p>
            </div>
          </div>
        `;
        nextStepsContent.innerHTML = html;

        // Trigger asynchronous details loading
        loadAsyncDashboardDetails();
      }
    }
  }

  async function loadAsyncDashboardDetails() {
    // 1. Fetch Phase 3 Next Action
    try {
      const resp = await fetch('/api/phase3/next-action');
      const card = $('#card-phase3-next-action');
      if (resp.ok && card) {
        const na = await resp.json();
        if (na.action_type === 'stop') {
          card.innerHTML = `
            <div class="dashboard-card-title">
              <h3>Phase 3 Next Action</h3>
              <span class="badge-status secondary">Stop</span>
            </div>
            <p style="font-size: 0.95rem; font-weight: 500;">No eligible Phase 3 work remains.</p>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">${escapeHtml(na.reason)}</p>
          `;
        } else {
          const badgeClass = na.action_type === 'probe' ? 'info' : (na.action_type === 'boss_fight' ? 'success' : 'warning');
          card.innerHTML = `
            <div class="dashboard-card-title">
              <h3>Phase 3 Next Action</h3>
              <span class="badge-status ${badgeClass}">${escapeHtml(na.action_type)}</span>
            </div>
            <p style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.25rem;">
              Target: ${escapeHtml(na.target_archetype_name || 'General')}
            </p>
            ${na.section ? `<p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: -0.25rem;">Section: <strong>${escapeHtml(na.section)}</strong></p>` : ''}
            <p style="font-size: 0.85rem; color: var(--text-secondary);">${escapeHtml(na.reason)}</p>
            <div style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.25rem;">
              <span style="font-size: 0.85rem; font-weight: 500;">Question Count: ${na.question_count}</span>
              <span style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Recommended CLI Command:</span>
              <code class="cli-code-block">${escapeHtml(na.cli_command)}</code>
            </div>
          `;
        }
      } else if (card) {
        throw new Error(`HTTP ${resp.status}`);
      }
    } catch (e) {
      const card = $('#card-phase3-next-action');
      if (card) {
        card.innerHTML = `
          <div class="dashboard-card-title">
            <h3>Phase 3 Next Action</h3>
            <span class="badge-status error">Unavailable</span>
          </div>
          <p style="font-size: 0.9rem; color: var(--color-error);">Failed to load next action: ${escapeHtml(e.message)}</p>
        `;
      }
    }

    // 2. Fetch Guardian & Readiness Summary
    try {
      const resp = await fetch('/api/study/summary');
      const card = $('#card-guardian-readiness');
      if (resp.ok && card) {
        const summary = await resp.json();
        const g = summary.guardian;
        const r = summary.readiness;

        let guardianHtml = '';
        if (g && g.available) {
          const modeClass = g.mode === 'planner' ? 'success' : 'warning';
          guardianHtml = `
            <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 0.75rem;">
              <div class="dashboard-card-title" style="margin-bottom: 0.5rem;">
                <h4 style="font-weight: 600; font-size: 0.95rem;">Guardian (Advisory)</h4>
                <span class="badge-status ${modeClass}">${escapeHtml(g.mode)}</span>
              </div>
              <p style="font-size: 0.85rem;"><strong>Daily capacity:</strong> ${g.total_minutes} mins</p>
              <p style="font-size: 0.85rem;"><strong>Mock Rec:</strong> ${escapeHtml(g.mock_recommendation)}</p>
              <p style="font-size: 0.85rem;"><strong>Pulse Rec:</strong> ${escapeHtml(g.pulse_recommendation)}</p>
              ${g.warnings && g.warnings.length > 0 ? `
                <div style="color: var(--color-error); font-size: 0.8rem; margin-top: 0.5rem;">
                  <strong>Warnings:</strong>
                  <ul style="margin-left: 1rem; margin-top: 0.25rem;">
                    ${g.warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}
                  </ul>
                </div>
              ` : ''}
            </div>
          `;
        } else {
          guardianHtml = `
            <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 0.75rem;">
              <div class="dashboard-card-title" style="margin-bottom: 0.5rem;">
                <h4 style="font-weight: 600; font-size: 0.95rem;">Guardian (Advisory)</h4>
                <span class="badge-status error">Unavailable</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-secondary);">${escapeHtml((g && g.warnings && g.warnings[0]) || 'Guardian scheduler is unavailable.')}</p>
            </div>
          `;
        }

        let readinessHtml = '';
        if (r && r.available) {
          const statusClass = r.status === 'ready' ? 'success' : 'warning';
          readinessHtml = `
            <div>
              <div class="dashboard-card-title" style="margin-bottom: 0.5rem;">
                <h4 style="font-weight: 600; font-size: 0.95rem;">Readiness Dashboard</h4>
                <span class="badge-status ${statusClass}">${escapeHtml(r.status.replace('_', ' '))}</span>
              </div>
              ${r.status !== 'ready' && r.missing_reasons && r.missing_reasons.length > 0 ? `
                <p style="font-size: 0.85rem; font-weight: 500; color: var(--text-secondary);">Missing Conditions:</p>
                <ul style="margin-left: 1rem; font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem; display: flex; flex-direction: column; gap: 0.25rem;">
                  ${r.missing_reasons.map(m => `<li>${escapeHtml(m.replace('_', ' '))}</li>`).join('')}
                </ul>
              ` : (r.status === 'ready' ? '<p style="font-size: 0.85rem; color: var(--color-success);">All readiness checklist requirements are satisfied!</p>' : '')}
            </div>
          `;
        } else {
          readinessHtml = `
            <div>
              <div class="dashboard-card-title" style="margin-bottom: 0.5rem;">
                <h4 style="font-weight: 600; font-size: 0.95rem;">Readiness Dashboard</h4>
                <span class="badge-status error">Unavailable</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-secondary);">${escapeHtml((r && r.missing_reasons && r.missing_reasons[0]) || 'Readiness dashboard is unavailable.')}</p>
            </div>
          `;
        }

        card.innerHTML = `
          <h3>Guardian & Readiness Summary</h3>
          <div style="display: flex; flex-direction: column;">
            ${guardianHtml}
            ${readinessHtml}
          </div>
        `;
      } else if (card) {
        throw new Error(`HTTP ${resp.status}`);
      }
    } catch (e) {
      const card = $('#card-guardian-readiness');
      if (card) {
        card.innerHTML = `
          <div class="dashboard-card-title">
            <h3>Guardian & Readiness Summary</h3>
            <span class="badge-status error">Unavailable</span>
          </div>
          <p style="font-size: 0.9rem; color: var(--color-error);">Failed to load summary: ${escapeHtml(e.message)}</p>
        `;
      }
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
    if (e.target.id === 'btn-clear-answer') {
      const q = state.questions[state.currentIndex];
      if (q && state.answers[q.question_id]) {
        delete state.answers[q.question_id];
        saveDraft();
        renderQuestion();
        renderNav();
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
