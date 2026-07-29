/**
 * list.js
 *
 * The shopping list / cart state for this session. In-memory only (no
 * localStorage) — a fresh cart per visit is fine for this demo, and it
 * keeps "what's in the cart" simple to reason about live. Exposed as
 * window.Cart so recommend.js / meal-plan.js can add products without
 * this file needing to know anything about search or recommendations.
 *
 * Adding the same product twice doesn't create a duplicate row — it
 * bumps that row's count and tells the user, since a shopping list
 * with the same item listed 3 separate times is confusing to check off.
 */
(function () {
  const itemList = document.getElementById("item-list");
  const emptyState = document.getElementById("empty-state");
  const toast = document.getElementById("toast");

  let items = []; // { id, key, name, brand, retailer, price, quantity, count, checked }
  let nextId = 1;
  let toastTimer = null;

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = "block";
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.style.display = "none"; }, 2200);
  }

  // Same product = same backend id (matched products), or same
  // name+brand+retailer (name-only meal-plan adds have no id).
  function keyFor(product) {
    return product.id || `${product.name}|${product.brand}|${product.retailer}`;
  }

  function getTotal() {
    // Checked = "picked up", not "no longer buying" — it must keep
    // counting against the budget. Only removing an item (the × button)
    // should change the total.
    return items.reduce((sum, item) => sum + item.price * item.count, 0);
  }

  function render() {
    itemList.innerHTML = "";
    emptyState.style.display = items.length === 0 ? "block" : "none";

    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "item-row" + (item.checked ? " checked" : "");

      const checkbox = document.createElement("button");
      checkbox.type = "button";
      checkbox.className = "item-checkbox";
      checkbox.textContent = item.checked ? "✓" : "";
      checkbox.addEventListener("click", () => toggleChecked(item.id));

      const info = document.createElement("div");
      info.className = "item-info";

      const name = document.createElement("div");
      name.className = "item-name";
      name.textContent = item.count > 1 ? `${item.name} × ${item.count}` : item.name;

      const meta = document.createElement("div");
      meta.className = "item-store";
      const pack = item.quantity ? ` · ${item.quantity}` : "";
      meta.textContent = `${item.retailer} · £${item.price.toFixed(2)} each${pack}`;

      info.appendChild(name);
      info.appendChild(meta);

      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "item-remove";
      remove.textContent = "×";
      remove.addEventListener("click", () => removeItem(item.id));

      li.appendChild(checkbox);
      li.appendChild(info);
      li.appendChild(remove);
      itemList.appendChild(li);
    });

    window.Budget.render(getTotal());
  }

  function add(product) {
    const key = keyFor(product);
    const existing = items.find((item) => item.key === key);

    if (existing) {
      existing.count += 1;
      render();
      showToast(`Already in your list — ${product.name} is now × ${existing.count}`);
      return;
    }

    items.push({
      id: nextId++,
      key,
      name: product.name,
      brand: product.brand,
      retailer: product.retailer,
      price: product.price,
      quantity: product.quantity,
      count: 1,
      checked: false
    });
    render();
  }

  function toggleChecked(id) {
    items = items.map((item) => (item.id === id ? { ...item, checked: !item.checked } : item));
    render();
  }

  function removeItem(id) {
    items = items.filter((item) => item.id !== id);
    render();
  }

  window.Cart = { add, removeItem, toggleChecked, getTotal, render };

  render();
})();
