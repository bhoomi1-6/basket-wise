(function () {
  const API_BASE = "http://localhost:8000";

  const state = {
    allergens: new Set(),
    dietary: null,
    budget: Number(document.getElementById("budget-slider").value)
  };

  const allergenChips = document.getElementById("allergen-chips");
  const allergensOther = document.getElementById("allergens-other");
  const dietaryChips = document.getElementById("dietary-chips");
  const dietaryOther = document.getElementById("dietary-other");
  const budgetSlider = document.getElementById("budget-slider");
  const budgetValue = document.getElementById("budget-value");
  const continueBtn = document.getElementById("continue-btn");
  const segments = document.querySelectorAll(".progress-bar .segment");

  const modal = document.getElementById("filter-modal");
  const modalAllergens = document.getElementById("modal-allergens");
  const modalCount = document.getElementById("modal-count");
  const modalBudget = document.getElementById("modal-budget");
  const modalDismiss = document.getElementById("modal-dismiss");
  const toast = document.getElementById("toast");

  function updateProgress() {
    segments[0].classList.toggle("done", state.allergens.size > 0);
    segments[1].classList.toggle("done", Boolean(state.dietary));
    segments[2].classList.toggle("done", true);

    const ready = state.allergens.size > 0 && Boolean(state.dietary);
    continueBtn.disabled = !ready;
    continueBtn.classList.toggle("disabled", !ready);
  }

  function addChip(container, otherButton, value, selected) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip" + (selected ? " selected" : "");
    chip.dataset.value = value;
    chip.textContent = value;
    container.insertBefore(chip, otherButton);
    return chip;
  }

  // --- Allergens (multi-select) ---
  allergenChips.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;

    if (chip.dataset.other) {
      allergensOther.style.display = allergensOther.style.display === "none" ? "block" : "none";
      if (allergensOther.style.display === "block") allergensOther.focus();
      return;
    }

    const value = chip.dataset.value;

    if (value === "None") {
      allergenChips.querySelectorAll(".chip.selected").forEach((c) => c.classList.remove("selected"));
      state.allergens.clear();
      chip.classList.add("selected");
      state.allergens.add("None");
    } else {
      const noneChip = allergenChips.querySelector('.chip[data-value="None"]');
      if (noneChip) {
        noneChip.classList.remove("selected");
        state.allergens.delete("None");
      }
      chip.classList.toggle("selected");
      if (chip.classList.contains("selected")) {
        state.allergens.add(value);
      } else {
        state.allergens.delete(value);
      }
    }

    updateProgress();
  });

  allergensOther.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" || !allergensOther.value.trim()) return;
    e.preventDefault();

    const noneChip = allergenChips.querySelector('.chip[data-value="None"]');
    if (noneChip) {
      noneChip.classList.remove("selected");
      state.allergens.delete("None");
    }

    allergensOther.value
      .split(",")
      .map((v) => v.trim())
      .filter(Boolean)
      .forEach((value) => {
        const otherBtn = allergenChips.querySelector("[data-other]");
        addChip(allergenChips, otherBtn, value, true);
        state.allergens.add(value);
      });

    allergensOther.value = "";
    allergensOther.style.display = "none";
    updateProgress();
  });

  // --- Dietary preference (single-select) ---
  dietaryChips.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;

    if (chip.dataset.other) {
      dietaryOther.style.display = dietaryOther.style.display === "none" ? "block" : "none";
      if (dietaryOther.style.display === "block") dietaryOther.focus();
      return;
    }

    dietaryChips.querySelectorAll(".chip.selected").forEach((c) => c.classList.remove("selected"));
    chip.classList.add("selected");
    state.dietary = chip.dataset.value;
    dietaryOther.style.display = "none";
    updateProgress();
  });

  dietaryOther.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" || !dietaryOther.value.trim()) return;
    e.preventDefault();

    const value = dietaryOther.value.trim();
    dietaryChips.querySelectorAll(".chip.selected").forEach((c) => c.classList.remove("selected"));
    const otherBtn = dietaryChips.querySelector("[data-other]");
    addChip(dietaryChips, otherBtn, value, true);
    state.dietary = value;

    dietaryOther.value = "";
    dietaryOther.style.display = "none";
    updateProgress();
  });

  // --- Budget (slider) ---
  budgetSlider.addEventListener("input", () => {
    state.budget = Number(budgetSlider.value);
    budgetValue.textContent = "$" + state.budget;
  });

  // --- Continue: confirm the profile with /filter, then hand off to shop.html ---

  function buildProfile() {
    return {
      allergens: Array.from(state.allergens),
      dietaryPreference: state.dietary,
      budget: state.budget
    };
  }

  function goToShop(profile) {
    localStorage.setItem("basketwise_profile", JSON.stringify(profile));
    window.location.href = "shop.html";
  }

  function showFilterModal(profile, result) {
    const allergensText = profile.allergens.length ? profile.allergens.join(", ") : "nothing";
    modalAllergens.textContent = `Excluded products with: ${allergensText}`;
    modalCount.textContent = `${result.safeCount} of ${result.safeCount + result.excludedCount} products available`;
    modalBudget.textContent = `Budget-aware recommendations are now active for £${profile.budget}`;
    modal.style.display = "flex";

    modalDismiss.onclick = () => {
      modal.style.display = "none";
      goToShop(profile);
    };
  }

  function showToastAndContinue(profile, message) {
    toast.textContent = message;
    toast.style.display = "block";
    setTimeout(() => goToShop(profile), 900);
  }

  async function handleContinue() {
    if (continueBtn.disabled) return;
    continueBtn.disabled = true;

    const profile = buildProfile();

    // /filter is a confirmation nicety, not a dependency — /recommend
    // independently re-filters on every real search regardless, so a
    // failure here must never block the user from reaching the shop.
    try {
      const res = await fetch(`${API_BASE}/filter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile })
      });

      if (!res.ok) throw new Error(`/filter returned ${res.status}`);

      const result = await res.json();
      showFilterModal(profile, result);
    } catch (err) {
      showToastAndContinue(profile, "Personalization saved locally");
    }
  }

  continueBtn.addEventListener("click", handleContinue);

  updateProgress();
})();
