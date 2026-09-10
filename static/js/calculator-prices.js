/**
 * calculator-prices.js — EUR-база + курси для підпису (дзеркало apps/core/calculator_estimate.py)
 * Не підставляти в layout; підключати лише на сторінці калькулятора.
 */
(function (global) {
    'use strict';

    var PRICES = {
        eur_uah: 43,
        eur_czk: 24.5,
        base_min_eur: { A: 400, B: 700, C: 1000, D: 1600, E: 2800 },
        addons_eur: {
            q2_crm: 250,
            q4_pay_card: 150,
            q4_pay_multi: 300,
            q4_invoice: 80,
            q3_urgent: 150
        }
    };

    function formatNbsp(n) {
        return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0');
    }

    function minEur(answers) {
        var q1 = answers.question_1 || 'A';
        var total = PRICES.base_min_eur[q1] || 400;
        var q2 = answers.question_2 || [];
        if (typeof q2 === 'string') q2 = [q2];
        if (q2.indexOf('C') !== -1 || q2.indexOf('D') !== -1) {
            total += PRICES.addons_eur.q2_crm;
        }
        if (answers.question_3 === 'A') total += PRICES.addons_eur.q3_urgent;
        if (answers.question_4 === 'B') total += PRICES.addons_eur.q4_pay_card;
        else if (answers.question_4 === 'D') total += PRICES.addons_eur.q4_pay_multi;
        else if (answers.question_4 === 'C') total += PRICES.addons_eur.q4_invoice;
        return total;
    }

    function formatDisplay(min, lang) {
        lang = (lang || document.documentElement.lang || 'uk').split('-')[0].toLowerCase();
        var uah = Math.round(min * PRICES.eur_uah);
        var czk = Math.round(min * PRICES.eur_czk);
        if (lang === 'cs') {
            return {
                price: 'od ' + formatNbsp(min) + ' €',
                price_secondary: 'orientačně ~' + formatNbsp(czk) + ' Kč'
            };
        }
        if (lang === 'en') {
            return {
                price: 'from €' + formatNbsp(min),
                price_secondary: 'approx. ~' + formatNbsp(czk) + ' Kč'
            };
        }
        if (lang === 'ru') {
            return { price: 'от ' + formatNbsp(uah) + ' грн', price_secondary: '' };
        }
        return { price: 'від ' + formatNbsp(uah) + ' грн', price_secondary: '' };
    }

    global.CalculatorPrices = {
        data: PRICES,
        minEur: minEur,
        formatDisplay: formatDisplay
    };
})(typeof window !== 'undefined' ? window : globalThis);
