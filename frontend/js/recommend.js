/**
 * recommend.js
 *
 * The real recommendation call — triggered by Enter, the Search
 * button, or clicking a suggestion. Always re-sends the full profile
 * so the backend can independently re-run its safety filter; this
 * file never assumes a product is safe just because it appeared in
 * lightweight /search suggestions.
 */
(function () {
  const API_BASE = "http://localhost:8000";

  const resultsSection = document.getElementById("results-section");
  const resultsMessage = document.getElementById("results-message");
  const topPickSlot = document.getElementById("top-pick-card");
  const alternativesEl = document.getElementById("alternatives");
  const searchInput = document.getElementById("search-input");
  const suggestionsList = document.getElementById("suggestions");

  function showMessage(text) {
    resultsSection.style.display = "block";
    resultsMessage.style.display = "block";
    resultsMessage.textContent = text;
    topPickSlot.innerHTML = "";
    alternativesEl.innerHTML = "";
  }

  function clearSearchUI() {
    searchInput.value = "";
    suggestionsList.style.display = "none";
    suggestionsList.innerHTML = "";
    hideResults();
  }

  function hideResults() {
    resultsSection.style.display = "none";
    resultsMessage.style.display = "none";
    topPickSlot.innerHTML = "";
    alternativesEl.innerHTML = "";
  }

  function productCard(product, options) {
    const card = document.createElement("div");
    card.className = options.isTopPick ? "pick-card" : "alt-card";

    const name = document.createElement("div");
    name.className = "pick-name";
    name.textContent = product.name;

    const meta = document.createElement("div");
    meta.className = "pick-meta";
    const qty = product.quantity ? ` · ${product.quantity}` : "";
    meta.textContent = `${product.brand} · ${product.retailer} · £${product.price.toFixed(2)} · ${product.rating}★${qty}`;

    card.appendChild(name);
    card.appendChild(meta);

    if (options.isTopPick && options.justification) {
      const justification = document.createElement("div");
      justification.className = "pick-justification";
      justification.textContent = options.justification;
      card.appendChild(justification);
    }

    // Ranking can still surface an over-budget item when it's the only
    // safe match (see justify.py) — the card must make that
    // unmissable and Add to list must not let it happen silently.
    const overBudget = product.price > options.remainingBudget;

    if (overBudget) {
      const overNote = document.createElement("div");
      overNote.className = "pick-over-budget";
      const overBy = product.price - options.remainingBudget;
      overNote.textContent = `£${overBy.toFixed(2)} over your remaining budget`;
      card.appendChild(overNote);
      card.classList.add("card-over-budget");
    }

    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "btn-add";

    if (overBudget) {
      addBtn.textContent = "Over budget";
      addBtn.disabled = true;
    } else {
      addBtn.textContent = "Add to list";
      addBtn.addEventListener("click", () => {
        window.Cart.add(product);
        (options.onAdded || clearSearchUI)(card);
      });
    }

    card.appendChild(addBtn);

    return card;
  }

  function renderResults(data, remainingBudget) {
    resultsSection.style.display = "block";

    if (!data.topPick) {
      showMessage("No safe matches found for this search");
      return;
    }

    resultsMessage.style.display = "none";
    topPickSlot.innerHTML = "";
    topPickSlot.appendChild(
      productCard(data.topPick, { isTopPick: true, justification: data.justification, remainingBudget })
    );

    alternativesEl.innerHTML = "";
    data.alternatives.forEach((product) => {
      alternativesEl.appendChild(productCard(product, { isTopPick: false, remainingBudget }));
    });
  }

  async function search(searchTerm) {
    if (!searchTerm) return;

    const profile = window.Budget.getProfile();
    if (!profile) {
      showMessage("Complete personalisation first to get recommendations");
      return;
    }

    const remainingBudget = window.Budget.getRemainingBudget(window.Cart.getTotal());

    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ searchTerm, profile, remainingBudget })
      });

      if (!res.ok) throw new Error(`/recommend returned ${res.status}`);

      renderResults(await res.json(), remainingBudget);
    } catch (err) {
      showMessage("Unable to search right now — please try again");
    }
  }

  // createProductCard is exposed so meal-plan.js can render matched
  // ingredients with the exact same card — one product card design
  // for the whole app, not a second one for meal plans.
  window.Recommend = { search, hideResults, createProductCard: productCard };
})();
