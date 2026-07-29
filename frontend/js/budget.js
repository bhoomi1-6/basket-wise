/**
 * budget.js
 *
 * Single source of truth for reading the saved profile and rendering
 * the budget bar. Exposed as window.Budget so list.js and recommend.js
 * can both read/render budget state without duplicating this logic.
 */
(function () {
  const budgetValues = document.getElementById("budget-values");
  const budgetFill = document.getElementById("budget-fill");

  function getProfile() {
    try {
      return JSON.parse(localStorage.getItem("basketwise_profile"));
    } catch (err) {
      return null;
    }
  }

  function render(spent) {
    const profile = getProfile();
    const total = (profile && profile.budget) || 0;

    budgetValues.textContent = `£${spent.toFixed(2)} / £${total.toFixed(2)}`;

    const pct = total > 0 ? Math.min(100, (spent / total) * 100) : 0;
    budgetFill.style.width = pct + "%";
    budgetFill.classList.toggle("over-budget", total > 0 && spent > total);
  }

  function getRemainingBudget(spent) {
    const profile = getProfile();
    const total = (profile && profile.budget) || 0;
    return total - spent;
  }

  window.Budget = { getProfile, render, getRemainingBudget };
})();
