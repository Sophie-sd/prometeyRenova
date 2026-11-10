(function () {
    'use strict';

    function initChangelistTopFilters() {
        var form = document.getElementById('changelist-top-filters');
        if (!form) {
            return;
        }

        var autoSubmitSelector = 'select, input[type="date"], input[type="datetime-local"]';

        form.querySelectorAll(autoSubmitSelector).forEach(function (input) {
            input.addEventListener('change', function () {
                if (input.getAttribute('data-filter-nav') === '1') {
                    if (input.value) {
                        window.location.href = input.value;
                    }
                    return;
                }
                form.submit();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChangelistTopFilters);
    } else {
        initChangelistTopFilters();
    }
})();
