/**
 * meal-plan.js
 *
 * A floating "Meal Assistant" button that expands into a panel:
 * "What are you cooking?" -> POST /meal-plan -> one row per ingredient.
 * Matched ingredients reuse window.Recommend.createProductCard, the
 * exact same card used for normal search results — there is only one
 * product card design in the app. Unmatched ingredients (not in our
 * 144-product catalog) get a simpler placeholder row instead of being
 * dropped, so the shopper's list never silently loses an item.
 */
(function () {
  const API_BASE = "http://localhost:8000";

  const fab = document.getElementById("meal-assistant-fab");
  const panel = document.getElementById("meal-assistant-panel");
  const closeBtn = document.getElementById("meal-assistant-close");
  const dishInput = document.getElementById("meal-plan-input");
  const generateBtn = document.getElementById("meal-plan-btn");
  const statusEl = document.getElementById("meal-plan-status");
  const resultsEl = document.getElementById("meal-plan-results");

  fab.addEventListener("click", () => {
    panel.style.display = "block";
    fab.style.display = "none";
    dishInput.focus();
  });

  closeBtn.addEventListener("click", () => {
    panel.style.display = "none";
    fab.style.display = "flex";
  });

  function showStatus(text) {
    statusEl.style.display = "block";
    statusEl.textContent = text;
  }

  function hideStatus() {
    statusEl.style.display = "none";
  }

  function unmatchedRow(item) {
    const row = document.createElement("div");
    row.className = "unmatched-card";

    const name = document.createElement("div");
    name.className = "pick-name";
    name.textContent = item.ingredient;

    const note = document.createElement("div");
    note.className = "unmatched-note";
    note.textContent = item.note;

    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "btn-add";
    addBtn.textContent = "Add to list";
    addBtn.addEventListener("click", () => {
      // Name-only add: no price, so it doesn't affect the budget total.
      window.Cart.add({ name: item.ingredient, brand: "", retailer: "", price: 0, quantity: "" });
      row.remove(); // added — stop showing it as an outstanding ingredient
    });

    row.appendChild(name);
    row.appendChild(note);
    row.appendChild(addBtn);
    return row;
  }

  function renderItems(items) {
    resultsEl.innerHTML = "";
    const remainingBudget = window.Budget.getRemainingBudget(window.Cart.getTotal());

    items.forEach((item) => {
      if (item.matched) {
        resultsEl.appendChild(
          window.Recommend.createProductCard(item.product, {
            isTopPick: true,
            justification: item.justification,
            remainingBudget,
            // Remove just this card once added — stays on the rest of the
            // meal-plan results (unlike the search flow, which clears everything).
            onAdded: (card) => card.remove()
          })
        );
      } else {
        resultsEl.appendChild(unmatchedRow(item));
      }
    });
  }

  async function generate() {
    const dish = dishInput.value.trim();
    if (!dish) return;

    const profile = window.Budget.getProfile();
    if (!profile) {
      showStatus("Complete personalisation first to generate a meal plan");
      return;
    }

    resultsEl.innerHTML = "";
    generateBtn.disabled = true;
    showStatus("Generating your meal plan — this can take a few seconds...");

    try {
      const res = await fetch(`${API_BASE}/meal-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dish, profile })
      });

      if (!res.ok) throw new Error(`/meal-plan returned ${res.status}`);

      const data = await res.json();

      if (data.message) {
        showStatus(data.message);
        return;
      }

      hideStatus();
      renderItems(data.items);
    } catch (err) {
      showStatus("Couldn't generate a meal plan right now — try searching ingredients manually instead.");
    } finally {
      generateBtn.disabled = false;
    }
  }

  generateBtn.addEventListener("click", generate);
  dishInput.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    generate();
  });
})();
