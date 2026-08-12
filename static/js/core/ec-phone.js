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
        var digits = String(raw).replace(/[^\d+]/g, '');
        if (!digits) return null;
        if (digits.indexOf('+') === 0) return digits;
        if (digits.indexOf('380') === 0) return '+' + digits;
        if (digits.indexOf('0') === 0) return '+38' + digits;
        return '+380' + digits;
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
