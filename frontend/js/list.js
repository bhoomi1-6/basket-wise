/**
 * list.js
 *
 * The shopping list / cart state for this session. In-memory only (no
 * localStorage) — a fresh cart per visit is fine for this demo, and it
 * keeps "what's in the cart" simple to reason about live. Exposed as
 * window.Cart so recommend.js can add products without this file
 * needing to know anything about search or recommendations.
 */
(function () {
  const itemList = document.getElementById("item-list");
  const emptyState = document.getElementById("empty-state");

  let items = []; // { id, name, brand, retailer, price, checked }
  let nextId = 1;

  function getTotal() {
    // Checked = "picked up", not "no longer buying" — it must keep
    // counting against the budget. Only removing an item (the × button)
    // should change the total.
    return items.reduce((sum, item) => sum + item.price, 0);
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
      name.textContent = item.name;

      const meta = document.createElement("div");
      meta.className = "item-store";
      const qty = item.quantity ? ` · ${item.quantity}` : "";
      meta.textContent = `${item.retailer} · £${item.price.toFixed(2)}${qty}`;

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
    items.push({
      id: nextId++,
      name: product.name,
      brand: product.brand,
      retailer: product.retailer,
      price: product.price,
      quantity: product.quantity,
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
