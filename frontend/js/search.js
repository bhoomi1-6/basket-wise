/**
 * search.js
 *
 * Debounced typeahead: as the user types, wait 300ms after the last
 * keystroke, then hit the lightweight GET /search endpoint (plain
 * substring match, no AI, no filtering) to show instant suggestions.
 * This is a best-effort UX nicety, not the real recommendation — that
 * only happens on Enter / Search click / clicking a suggestion, via
 * recommend.js. A failed suggestion fetch fails silently on purpose.
 */
(function () {
  const API_BASE = "http://localhost:8000";
  const DEBOUNCE_MS = 300;

  const searchInput = document.getElementById("search-input");
  const searchBtn = document.getElementById("search-btn");
  const retailerSelect = document.getElementById("retailer-select");
  const suggestionsList = document.getElementById("suggestions");

  let debounceTimer = null;

  function hideSuggestions() {
    suggestionsList.style.display = "none";
    suggestionsList.innerHTML = "";
  }

  function renderSuggestions(results) {
    suggestionsList.innerHTML = "";

    if (results.length === 0) {
      hideSuggestions();
      return;
    }

    results.forEach((product) => {
      const li = document.createElement("li");
      li.className = "suggestion-row";
      li.textContent = `${product.name} — ${product.brand}`;
      li.addEventListener("click", () => {
        searchInput.value = product.name;
        hideSuggestions();
        window.Recommend.search(product.name);
      });
      suggestionsList.appendChild(li);
    });

    suggestionsList.style.display = "block";
  }

  async function fetchSuggestions(term) {
    try {
      const url = `${API_BASE}/search?q=${encodeURIComponent(term)}&retailer=${encodeURIComponent(retailerSelect.value)}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`/search returned ${res.status}`);
      renderSuggestions(await res.json());
    } catch (err) {
      hideSuggestions();
    }
  }

  searchInput.addEventListener("input", () => {
    const term = searchInput.value.trim();
    clearTimeout(debounceTimer);

    if (!term) {
      hideSuggestions();
      window.Recommend.hideResults();
      return;
    }

    debounceTimer = setTimeout(() => fetchSuggestions(term), DEBOUNCE_MS);
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    hideSuggestions();
    window.Recommend.search(searchInput.value.trim());
  });

  searchBtn.addEventListener("click", () => {
    hideSuggestions();
    window.Recommend.search(searchInput.value.trim());
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-field-wrap")) hideSuggestions();
  });
})();
