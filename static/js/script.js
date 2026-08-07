document.addEventListener("DOMContentLoaded", () => {
  const chips = Array.from(document.querySelectorAll(".skill-chip"));
  const analyzeBtn = document.getElementById("analyze-btn");
  const targetSelect = document.getElementById("target-career");
  const errorEl = document.getElementById("tool-error");
  const resultsEmpty = document.getElementById("results-empty");
  const resultsContent = document.getElementById("results-content");

  // ---- skill chip toggle + slider wiring ----
  chips.forEach((chip) => {
    const skill = chip.dataset.skill;
    const toggle = chip.querySelector(".chip-toggle");
    const slider = chip.querySelector(".chip-slider");
    const levelLabel = chip.querySelector(".chip-level");

    toggle.addEventListener("click", () => {
      const nowActive = chip.classList.toggle("active");
      slider.disabled = !nowActive;
      levelLabel.textContent = nowActive ? slider.value : "\u2014";
    });

    slider.addEventListener("input", () => {
      levelLabel.textContent = slider.value;
    });
  });

  function collectSkills() {
    const skills = {};
    chips.forEach((chip) => {
      if (chip.classList.contains("active")) {
        const skill = chip.dataset.skill;
        const slider = chip.querySelector(".chip-slider");
        skills[skill] = parseInt(slider.value, 10);
      }
    });
    return skills;
  }

  analyzeBtn.addEventListener("click", async () => {
    errorEl.textContent = "";
    const skills = collectSkills();

    if (Object.keys(skills).length === 0) {
      errorEl.textContent = "Select at least one skill and set its level first.";
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Plotting your bearing\u2026";

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skills,
          target_career: targetSelect.value || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        errorEl.textContent = data.error || "Something went wrong. Try again.";
        return;
      }

      if (data.mode === "single") {
        renderSingle(data.result);
      } else {
        renderRecommendations(data.results);
      }

      resultsEmpty.hidden = true;
      resultsContent.hidden = false;
      document.getElementById("results").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      errorEl.textContent = "Couldn't reach the server. Is app.py running?";
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Get my report";
    }
  });

  // ---- renderers ----
  function renderSingle(result) {
    resultsContent.innerHTML = `
      <div class="gap-card">
        <div class="gauge" style="--pct:${result.match_percent}">
          <span class="gauge-value">${result.match_percent}%</span>
          <span class="gauge-label">Match</span>
        </div>
        <div>
          <h3>${escapeHtml(result.career)}</h3>
          <p class="gap-meta">Avg. salary ${escapeHtml(result.avg_salary_inr)} &middot; Demand: ${escapeHtml(result.growth)}</p>
          <p class="gap-desc">${escapeHtml(result.description)}</p>
          <div class="skill-lists">
            ${renderSkillList("Matched", "matched", result.matched_skills.map(s => `${s.skill} <span class="sub">(Lv ${s.your_level}/${s.required_level})</span>`))}
            ${renderSkillList("Needs work", "weak", result.weak_skills.map(s => `${s.skill} <span class="sub">(Lv ${s.your_level} \u2192 ${s.required_level})</span>`))}
            ${renderSkillList("Missing", "missing", result.missing_skills.map(s => `${s.skill} <span class="sub">(target Lv ${s.required_level})</span>`))}
          </div>
        </div>
      </div>
    `;
  }

  function renderSkillList(title, cls, itemsHtml) {
    const items = itemsHtml.length
      ? itemsHtml.map((html) => `<li>${html}</li>`).join("")
      : `<li class="sub">None</li>`;
    return `
      <div class="skill-list ${cls}">
        <h5>${title}</h5>
        <ul>${items}</ul>
      </div>
    `;
  }

  function renderRecommendations(results) {
    const cards = results.map((r, i) => `
      <div class="reco-card">
        <div class="reco-rank">
          <div class="reco-gauge" style="--pct:${r.match_percent}"><span>${r.match_percent}%</span></div>
        </div>
        <div class="reco-body">
          <h4>#${i + 1} &middot; ${escapeHtml(r.career)}</h4>
          <p>${escapeHtml(r.description)}</p>
          <div class="reco-tags">
            <span>${escapeHtml(r.avg_salary_inr)}</span>
            <span>Demand: ${escapeHtml(r.growth)}</span>
            <span>${r.missing_skills.length} skill${r.missing_skills.length === 1 ? "" : "s"} to learn</span>
          </div>
        </div>
        <button class="reco-cta" data-career="${escapeHtml(r.career)}">Full gap report</button>
      </div>
    `).join("");

    resultsContent.innerHTML = `<div class="reco-grid">${cards}</div>`;

    resultsContent.querySelectorAll(".reco-cta").forEach((btn) => {
      btn.addEventListener("click", () => {
        targetSelect.value = btn.dataset.career;
        analyzeBtn.click();
      });
    });
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});
