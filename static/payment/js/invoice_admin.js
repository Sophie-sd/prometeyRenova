(function () {
  function placePdfButton() {
    var btn = document.getElementById('invoice-save-pdf-btn');
    if (!btn) return;
    var row = document.querySelector('.submit-row');
    if (!row) return;
    btn.hidden = false;
    row.insertBefore(btn, row.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', placePdfButton);
  } else {
    placePdfButton();
  }
})();
