/* Admin entry-point: copy.js already wires [data-copy] handlers globally,
   so this file only needs to ensure copy.js is loaded alongside admin pages
   and reserves a hook for future admin-specific behavior. */
(function () {
    'use strict';
    if (!window.PaymentCopy) {
        return;
    }
})();
