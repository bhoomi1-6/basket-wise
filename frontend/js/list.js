(function () {
  const itemInput = document.getElementById("item-input");
  const storeSelect = document.getElementById("store-select");
  const itemList = document.getElementById("item-list");
  const emptyState = document.getElementById("empty-state");

  let items = [];
  let nextId = 1;

  function render() {
    itemList.innerHTML = "";
    emptyState.style.display = items.length === 0 ? "block" : "none";

    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "item-row" + (item.checked ? " checked" : "");
      li.dataset.id = item.id;

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

      const store = document.createElement("div");
      store.className = "item-store";
      store.textContent = "Store " + item.store;

      info.appendChild(name);
      info.appendChild(store);

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
  }

  function addItem(name) {
    const trimmed = name.trim();
    if (!trimmed) return;

    items.push({
      id: nextId++,
      name: trimmed,
      store: storeSelect.value,
      checked: false
    });
    render();
  }

  function toggleChecked(id) {
    items = items.map((item) =>
      item.id === id ? { ...item, checked: !item.checked } : item
    );
    render();
  }

  function removeItem(id) {
    items = items.filter((item) => item.id !== id);
    render();
  }

  itemInput.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    addItem(itemInput.value);
    itemInput.value = "";
  });

  render();
})();
