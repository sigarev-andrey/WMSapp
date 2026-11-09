// Progressive enhancement only: navigation, filters and forms also work without JS.
document.querySelectorAll('[data-submit-form]').forEach((form) => {
  form.addEventListener('submit', () => {
    form.querySelectorAll('button[type="submit"]').forEach((button) => {
      button.disabled = true;
      button.setAttribute('aria-busy', 'true');
    });
  });
});

// Re-enable controls when returning through the browser's back/forward cache.
window.addEventListener('pageshow', () => {
  document.querySelectorAll('button[aria-busy="true"]').forEach((button) => {
    button.disabled = false;
    button.removeAttribute('aria-busy');
  });
});

const searchPanel = document.querySelector('[data-item-search]');
const itemSelect = document.querySelector('select[name="item"]');
if (searchPanel && itemSelect) {
  const input = searchPanel.querySelector('input');
  const status = searchPanel.querySelector('[data-search-status]');
  const options = Array.from(itemSelect.options);
  const selectedItem = document.querySelector('[data-selected-item]');
  const showSelection = () => {
    if (!selectedItem) return;
    selectedItem.hidden = !itemSelect.value;
    selectedItem.textContent = itemSelect.value ? itemSelect.selectedOptions[0].text : '';
  };
  itemSelect.addEventListener('change', showSelection);
  showSelection();
  searchPanel.hidden = false;
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase('ru');
    const selectedValue = itemSelect.value;
    const matches = options.filter((option) => option.value && option.text.toLocaleLowerCase('ru').includes(query));
    const visibleOptions = options.filter((option) => !option.value || option.value === selectedValue || matches.includes(option));
    itemSelect.replaceChildren(...visibleOptions);
    itemSelect.value = selectedValue;
    status.textContent = matches.length ? `Найдено позиций: ${matches.length}. Выберите нужную ниже.` : 'Ничего не найдено. Измените запрос.';
  });
}
