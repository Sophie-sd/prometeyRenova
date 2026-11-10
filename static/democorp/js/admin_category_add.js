(function () {
    'use strict';

    // «+ Додати категорію» під полем: відкриває те саме вікно, що й меню ⋮,
    // і нова категорія одразу обирається у списку. Без JS — нова вкладка.
    document.addEventListener('click', function (event) {
        var link = event.target.closest('[data-dc-add-category]');
        if (!link) {
            return;
        }
        var popupLink = document.getElementById('add_id_category');
        if (!popupLink) {
            return;
        }
        event.preventDefault();
        popupLink.click();
    });
})();
