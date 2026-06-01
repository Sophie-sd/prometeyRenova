/* Admin entry-point: copy.js wires [data-copy] globally.
   This file adds currency-aware field visibility in the PaymentLink form. */
(function () {
    'use strict';

    function syncCurrencyFields() {
        const currencySelect = document.getElementById('id_currency');
        if (!currencySelect) return;
        const rateRow = document.querySelector('.field-exchange_rate');
        if (!rateRow) return;
        rateRow.classList.toggle('pl-hidden', currencySelect.value === 'UAH');
    }

    document.addEventListener('DOMContentLoaded', function () {
        syncCurrencyFields();
        const currencySelect = document.getElementById('id_currency');
        if (currencySelect) {
            currencySelect.addEventListener('change', syncCurrencyFields);
        }
    });
})();
