(function () {
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

  // --- Continue ---
  continueBtn.addEventListener("click", () => {
    if (continueBtn.disabled) return;

    const profile = {
      allergens: Array.from(state.allergens),
      dietary: state.dietary,
      budget: state.budget
    };

    localStorage.setItem("basketwise_profile", JSON.stringify(profile));
    window.location.href = "list.html";
  });

  updateProgress();
})();
