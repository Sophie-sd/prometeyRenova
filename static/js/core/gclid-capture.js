/**
 * Google Ads GCLID & UTM Capture
 * Захоплює gclid та UTM параметри з URL, зберігає в cookies на 90 днів,
 * та автоматично додає їх до всіх форм при відправці.
 */
(function() {
    'use strict';

    const COOKIE_EXPIRY_DAYS = 90;
    const TRACKING_PARAMS = ['gclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = 'expires=' + date.toUTCString();
        const secure = location.protocol === 'https:' ? ';Secure' : '';
        document.cookie = name + '=' + encodeURIComponent(value) + ';' + expires + ';path=/' + secure + ';SameSite=Lax';
    }

    function getCookie(name) {
        const nameEQ = name + '=';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let c = cookies[i].trim();
            if (c.indexOf(nameEQ) === 0) {
                return decodeURIComponent(c.substring(nameEQ.length));
            }
        }
        return '';
    }

    function captureFromURL() {
        const params = new URLSearchParams(window.location.search);
        let hasNewParams = false;

        TRACKING_PARAMS.forEach(function(param) {
            const value = params.get(param);
            if (value) {
                setCookie('_prm_' + param, value, COOKIE_EXPIRY_DAYS);
                hasNewParams = true;
            }
        });

        return hasNewParams;
    }

    function getTrackingData() {
        const data = {};
        TRACKING_PARAMS.forEach(function(param) {
            const value = getCookie('_prm_' + param);
            if (value) {
                data[param] = value;
            }
        });
        return data;
    }

    function appendToFormData(formData) {
        const tracking = getTrackingData();
        Object.keys(tracking).forEach(function(key) {
            if (!formData.has(key)) {
                formData.append(key, tracking[key]);
            }
        });
        return formData;
    }

    captureFromURL();

    window.GCLIDCapture = {
        getTrackingData: getTrackingData,
        appendToFormData: appendToFormData
    };
})();
