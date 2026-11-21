/**
 * Enhanced Conversions phone bridge for Google Ads (via GTM).
 *
 * Saves a normalized E.164 phone to sessionStorage (`ec_phone`) before
 * redirect to /thank-you/, so GTM User-Provided Data can hash and send it.
 * No listeners on load — call saveFromRaw only after a successful lead redirect.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'ec_phone';

    function normalizePhone(raw) {
        if (!raw) return null;
        var s = String(raw).trim();
        var digits = s.replace(/\D/g, '');
        if (!digits) return null;
        var intl = s.charAt(0) === '+' || digits.indexOf('00') === 0;
        if (digits.indexOf('00') === 0) digits = digits.slice(2);
        if (digits.indexOf('380') === 0 && digits.length >= 12) return '+380' + digits.slice(3, 12);
        if (digits.charAt(0) === '0' && digits.length >= 10) return '+38' + digits.slice(0, 10);
        if (!intl && digits.length === 9) return '+380' + digits;
        if (!intl && digits.indexOf('80') === 0 && digits.length >= 11) return '+3' + digits.slice(0, 11);
        var en = ((document.documentElement && document.documentElement.lang) || '').toLowerCase().slice(0, 2) === 'en';
        if (en && intl && digits.charAt(0) !== '0' && digits.length >= 8 && digits.length <= 15) return '+' + digits;
        if (digits.indexOf('380') === 0) return '+' + digits;
        if (digits.charAt(0) === '0') return '+38' + digits;
        if (!en) return digits.length ? '+380' + digits : null;
        return null;
    }

    function saveFromRaw(raw) {
        var phone = normalizePhone(raw);
        if (!phone) return false;
        try {
            sessionStorage.setItem(STORAGE_KEY, phone);
            return true;
        } catch (err) {
            return false;
        }
    }

    window.ECPhone = {
        normalizePhone: normalizePhone,
        saveFromRaw: saveFromRaw,
        STORAGE_KEY: STORAGE_KEY
    };
})();

window.ec_stored_phone = (function () {
    try {
        return sessionStorage.getItem('ec_phone') || '';
    } catch (e) {
        return '';
    }
})();
