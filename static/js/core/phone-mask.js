/**
 * PHONE-MASK.JS — єдина маска телефону для всього сайту (vanilla, без залежностей).
 *
 * - Україна за замовчуванням: +380 (XX) XXX-XX-XX, рівно 9 національних цифр.
 * - Лише українські номери: будь-який інший код країни (+1, +44, 0048…) відхиляється.
 * - Автозаповнення (input/change/animationstart), вставка будь-якого формату,
 *   backspace/delete посередині без стрибків каретки, мобільні клавіатури.
 * - Доступні інлайн-помилки (aria-invalid, aria-describedby), UA/RU/EN.
 * - Блокує submit форми з невалідним номером (capture-фаза, до htmx/base.js).
 * - Реініт після htmx:afterSwap / htmx:afterSettle / htmx:load.
 * Дзеркало серверної логіки: apps/core/phone.py
 *
 * Публічний API (сумісний зі старим): new PhoneMask(input) → .formatValue(v),
 * .validate() → {valid, message, cleaned}, .getCleanedValue() → E.164,
 * .ensurePrefix(), .destroy(). Статичні: PhoneMask.parse(raw), PhoneMask.initAll(root),
 * PhoneMask.check(input), PhoneMask.showError(input, msg), PhoneMask.clearError(input).
 */
(function (global) {
    'use strict';

    var UA = '380';
    var UA_LEN = 9;
    var MAX_FOREIGN = 15;
    var SELECTOR = 'input[type="tel"], input[name="phone"], input[autocomplete="tel"]';
    var PLACEHOLDER = '+380 (__) ___-__-__';

    var MESSAGES = {
        uk: {
            required: 'Введіть номер телефону',
            short: 'Номер неповний: після +380 потрібно 9 цифр',
            long: 'Забагато цифр: після +380 має бути рівно 9',
            foreign: 'Приймаємо лише українські номери +380',
            invalid: 'Введіть коректний номер телефону',
            hint: 'Формат: +380 (67) 123-45-67'
        },
        ru: {
            required: 'Введите номер телефона',
            short: 'Номер неполный: после +380 нужно 9 цифр',
            long: 'Слишком много цифр: после +380 должно быть ровно 9',
            foreign: 'Принимаем только украинские номера +380',
            invalid: 'Введите корректный номер телефона',
            hint: 'Формат: +380 (67) 123-45-67'
        },
        en: {
            required: 'Enter your phone number',
            short: 'Incomplete number: 9 digits are needed after +380',
            long: 'Too many digits: exactly 9 are needed after +380',
            foreign: 'We only accept Ukrainian numbers (+380)',
            invalid: 'Enter a valid phone number',
            hint: 'Format: +380 (67) 123-45-67'
        }
    };

    function lang() {
        var l = ((document.documentElement && document.documentElement.lang) || 'uk').toLowerCase().slice(0, 2);
        if (l === 'ua') l = 'uk';
        return MESSAGES[l] ? l : 'uk';
    }
    function msg(key, cc) {
        return MESSAGES[lang()][key].replace('{cc}', cc || '');
    }

    /**
     * Розбір довільного рядка.
     * → {empty, cc, nat, digits, partialPrefix, e164, error}
     */
    function parse(raw) {
        var s = String(raw == null ? '' : raw).trim();
        var digits = s.replace(/\D/g, '');
        var res = { empty: false, cc: UA, nat: '', digits: digits, partialPrefix: '', e164: '', error: '' };
        var hasLetters = /[^\d\s()+\-.]/.test(s);
        if (!digits) {
            res.empty = true;
            res.error = 'required';
            if (s.charAt(0) === '+') res.partialPrefix = '+';
            return res;
        }
        var intl = s.charAt(0) === '+' || digits.slice(0, 2) === '00';
        if (digits.slice(0, 2) === '00') digits = digits.slice(2);

        if (digits.indexOf(UA) === 0) {
            res.nat = digits.slice(3);
        } else if (UA.indexOf(digits) === 0) {
            // «3», «38» — користувач набирає код країни; показуємо як є
            res.partialPrefix = '+' + digits;
            res.error = 'short';
            return res;
        } else if (intl) {
            // Лише українські номери: будь-який інший код країни відхиляємо
            res.cc = null;
            res.nat = digits;
            res.error = 'foreign';
            return res;
        } else if (digits.slice(0, 2) === '80' && digits.length === 11) {
            res.nat = digits.slice(2);
        } else {
            res.nat = digits;
        }

        if (res.nat.charAt(0) === '0') res.nat = res.nat.slice(1);
        if (res.nat.length < UA_LEN) res.error = res.nat.length ? 'short' : 'required';
        else if (res.nat.length > UA_LEN) res.error = 'long';
        else res.e164 = '+' + UA + res.nat;
        if (hasLetters && res.e164) { res.e164 = ''; res.error = 'invalid'; }
        return res;
    }

    function format(p) {
        if (p.empty) return p.partialPrefix || '';
        if (p.partialPrefix) return p.partialPrefix;
        var n = p.nat;
        if (p.cc === UA) {
            var out = '+380';
            if (!n) return out + ' ';
            out += ' (' + n.slice(0, 2);
            if (n.length > 2) out += ') ' + n.slice(2, 5);
            if (n.length > 5) out += '-' + n.slice(5, 7);
            if (n.length > 7) out += '-' + n.slice(7, 9);
            if (n.length > 9) out += n.slice(9);
            return out;
        }
        // Іноземний номер: показуємо як ввели, без форматування (помилка 'foreign')
        return '+' + p.digits.replace(/^00/, '');
    }

    function maxNat(cc) { return cc === UA ? UA_LEN : MAX_FOREIGN; }

    function countDigits(str) { return (str.match(/\d/g) || []).length; }

    /** Позиція каретки, після якої лишається рівно k цифр. */
    function caretForDigitsAfter(value, k) {
        if (k <= 0) return value.length;
        var seen = 0;
        for (var i = value.length - 1; i >= 0; i--) {
            if (/\d/.test(value.charAt(i))) {
                seen++;
                if (seen === k) {
                    // каретка одразу після попередньої цифри
                    var j = i - 1;
                    while (j >= 0 && !/\d/.test(value.charAt(j))) j--;
                    return j + 1;
                }
            }
        }
        return 0;
    }

    function isVisible(el) {
        return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
    }

    var uid = 0;

    // ===== Error UI =====
    function errorHost(input) {
        var parent = input.parentElement;
        if (!parent) return null;
        var calc = parent.querySelector('.calc-field__error');
        if (calc) return { el: calc, legacy: true };
        return null;
    }

    function showError(input, message) {
        if (!input.id) input.id = 'phone-input-' + (++uid);
        var errId = input.id + '-phone-error';
        var host = errorHost(input);
        var el = document.getElementById(errId);
        if (host) {
            el = host.el;
            if (!el.id) el.id = errId;
            errId = el.id;
            el.textContent = message;
            el.classList.add('show');
        } else {
            if (!el) {
                el = document.createElement('p');
                el.id = errId;
                el.className = 'phone-field-error';
                el.setAttribute('role', 'alert');
                el.setAttribute('aria-live', 'assertive');
                var parent = input.parentElement;
                // Обгортка-рядок (іконка + інпут) → помилка під обгорткою
                var anchor = input;
                if (parent && parent.tagName !== 'FORM' && parent.children.length <= 3 &&
                    /field|input-wrap|form-group/i.test(parent.className || '')) {
                    anchor = parent;
                }
                anchor.insertAdjacentElement('afterend', el);
            }
            el.textContent = message;
            el.hidden = false;
        }
        input.classList.add('is-phone-invalid');
        input.setAttribute('aria-invalid', 'true');
        var described = (input.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        if (described.indexOf(errId) === -1) described.push(errId);
        input.setAttribute('aria-describedby', described.join(' '));
    }

    function clearError(input) {
        var errId = input.id ? input.id + '-phone-error' : '';
        var host = errorHost(input);
        if (host) {
            host.el.textContent = '';
            host.el.classList.remove('show');
            if (host.el.id) errId = host.el.id;
        }
        var el = errId && document.getElementById(errId);
        if (el && !host) el.remove();
        input.classList.remove('is-phone-invalid');
        input.removeAttribute('aria-invalid');
        var described = (input.getAttribute('aria-describedby') || '').split(/\s+/)
            .filter(function (x) { return x && x !== errId; });
        if (described.length) input.setAttribute('aria-describedby', described.join(' '));
        else input.removeAttribute('aria-describedby');
    }

    function check(input) {
        var value = (input.value || '').trim();
        var p = parse(value);
        var required = input.required || input.hasAttribute('required') || input.getAttribute('aria-required') === 'true';
        var rejected = input.__phoneMask && input.__phoneMask._rejected;
        if (p.empty || (p.cc === UA && !p.nat && !p.partialPrefix)) {
            if (rejected) return { valid: false, message: msg('invalid'), cleaned: '' };
            if (!required) return { valid: true, message: '', cleaned: '', empty: true };
            return { valid: false, message: msg('required'), cleaned: '' };
        }
        if (p.e164) return { valid: true, message: '', cleaned: p.e164 };
        return { valid: false, message: msg(p.error || 'invalid', p.cc), cleaned: '' };
    }

    // ===== Mask =====
    function PhoneMask(input) {
        if (!(this instanceof PhoneMask)) return new PhoneMask(input);
        if (input.__phoneMask) return input.__phoneMask;
        input.__phoneMask = this;
        this.input = input;
        this.prefix = '+380';
        this._touched = false;
        this._prev = { value: input.value, start: 0, end: 0 };
        this._handlers = {};
        this.init();
    }

    PhoneMask.prototype.init = function () {
        var input = this.input;
        var self = this;
        if (input.type === 'text' || !input.getAttribute('type')) input.type = 'tel';
        input.setAttribute('inputmode', 'tel');
        if (!input.getAttribute('autocomplete') || input.getAttribute('autocomplete') === 'off') {
            input.setAttribute('autocomplete', 'tel');
        }
        input.setAttribute('data-phone-mask', 'on');
        var ph = input.getAttribute('placeholder') || '';
        if (!ph || /^\+?38\s*\(?[_0]/.test(ph)) input.setAttribute('placeholder', PLACEHOLDER);
        if (input.maxLength > 0 && input.maxLength < 24) input.removeAttribute('maxlength');

        var on = function (type, fn, target) {
            var t = target || input;
            t.addEventListener(type, fn);
            self._handlers[type + (target ? ':form' : '')] = { t: t, type: type, fn: fn };
        };
        on('keydown', function (e) { self.onKeyDown(e); });
        on('beforeinput', function () { self.remember(); });
        on('input', function (e) { self.onInput(e); });
        on('change', function () { self.reformat(true); self.liveValidate(); });
        on('animationstart', function (e) {
            if (e.animationName === 'phoneMaskAutofill') { self.reformat(true); self.liveValidate(); }
        });
        on('focus', function () { self.remember(); });
        on('blur', function () { self.onBlur(); });
        var form = input.form;
        if (form) {
            on('reset', function () {
                setTimeout(function () { self._touched = false; self._rejected = false; clearError(input); }, 0);
            }, form);
        }
        if (input.value) this.reformat(true);
    };

    PhoneMask.prototype.remember = function () {
        var i = this.input;
        this._prev = { value: i.value, start: i.selectionStart || 0, end: i.selectionEnd || 0 };
    };

    PhoneMask.prototype.setCaret = function (pos) {
        var i = this.input;
        if (document.activeElement !== i) return;
        try { i.setSelectionRange(pos, pos); } catch (e) { /* type=tel не підтримує в старих браузерах */ }
    };

    PhoneMask.prototype.apply = function (raw, digitsAfter) {
        var p = parse(raw);
        var next = format(p);
        this.input.value = next;
        this.setCaret(digitsAfter == null ? next.length : caretForDigitsAfter(next, digitsAfter));
        this._prev = { value: next, start: this.input.selectionStart || 0, end: this.input.selectionEnd || 0 };
        return p;
    };

    PhoneMask.prototype.reformat = function (toEnd) {
        var v = this.input.value;
        if (!v) return;
        this.apply(v, toEnd ? null : 0);
    };

    PhoneMask.prototype.onInput = function (e) {
        var i = this.input;
        var raw = i.value;
        // Букви/сторонні символи вирізаються маскою — запам'ятовуємо, щоб показати помилку
        if (/[^\d\s()+\-.]/.test(raw)) { this._rejected = true; this._touched = true; }
        else if (/\d/.test(raw)) this._rejected = false;
        var caret = i.selectionStart == null ? raw.length : i.selectionStart;
        var after = countDigits(raw.slice(caret));
        var type = (e && e.inputType) || '';
        var p = parse(raw);
        // Ручний набір: не даємо перевищити довжину номера
        var singleKey = (type === 'insertText' || type === 'insertCompositionText') &&
            (e && typeof e.data === 'string' && e.data.length === 1);
        if (singleKey && !p.partialPrefix && !p.empty) {
            var over = p.cc ? p.nat.length - maxNat(p.cc) : p.digits.length - MAX_FOREIGN;
            var prevP = parse(this._prev.value);
            var prevOver = prevP.cc ? prevP.nat.length - maxNat(prevP.cc) : prevP.digits.length - MAX_FOREIGN;
            if (over > 0 && over > prevOver) {
                i.value = this._prev.value;
                this.setCaret(this._prev.start);
                return;
            }
        }
        if (!/\d/.test(raw)) {
            // Лише «+» або порожньо/букви
            i.value = raw.trim().charAt(0) === '+' ? '+' : '';
            this._prev = { value: i.value, start: i.value.length, end: i.value.length };
            if (this._touched) this.liveValidate();
            return;
        }
        var bulk = type === 'insertFromPaste' || type === 'insertFromDrop' || type === 'insertReplacementText' || !type;
        this.apply(raw, bulk && after === 0 ? null : after);
        this.liveValidate();
    };

    PhoneMask.prototype.liveValidate = function () {
        var r = check(this.input);
        if (r.valid) { clearError(this.input); return; }
        // Помилку показуємо лише після blur/submit, а потім оновлюємо наживо
        if (this._touched) showError(this.input, r.message);
    };

    PhoneMask.prototype.onBlur = function () {
        var i = this.input;
        var p = parse(i.value);
        // Лише префікс без цифр номера → очищаємо (працює placeholder і required)
        if (p.empty || (p.cc === UA && !p.nat && !p.partialPrefix)) i.value = '';
        else if (i.value) this.apply(i.value, null);
        if (!i.value && !this._touched && !this._rejected) { clearError(i); return; }
        this._touched = true;
        this.liveValidate();
    };

    PhoneMask.prototype.onKeyDown = function (e) {
        var i = this.input;
        var v = i.value;
        var s = i.selectionStart, end = i.selectionEnd;
        this.remember();
        if (e.key !== 'Backspace' && e.key !== 'Delete') return;
        if (s == null || s !== end || e.ctrlKey || e.metaKey || e.altKey) return;
        var p = parse(v);
        var isUA = p.cc === UA && !p.partialPrefix && !p.empty;
        var prefixLen = isUA ? 4 : 0; // "+380"
        if (e.key === 'Backspace') {
            if (isUA && s <= prefixLen + 2 && s > 0 && (!p.nat || s <= prefixLen)) {
                // Видалення в межах «+380»: порожній номер → очищаємо, інакше не ламаємо код
                e.preventDefault();
                if (!p.nat) { i.value = ''; this.remember(); this.liveValidate(); }
                else this.setCaret(prefixLen + 2);
                return;
            }
            if (s > 0 && !/\d/.test(v.charAt(s - 1))) {
                // Перед кареткою роздільник → видаляємо попередню цифру
                var j = s - 1;
                while (j >= 0 && !/\d/.test(v.charAt(j))) j--;
                if (j < 0 || (isUA && j < prefixLen)) { e.preventDefault(); return; }
                e.preventDefault();
                var after = countDigits(v.slice(s));
                this.apply(v.slice(0, j) + v.slice(j + 1), after);
                this.liveValidate();
            }
        } else if (e.key === 'Delete') {
            if (isUA && s < prefixLen) { e.preventDefault(); return; }
            if (s < v.length && !/\d/.test(v.charAt(s))) {
                var k = s;
                while (k < v.length && !/\d/.test(v.charAt(k))) k++;
                if (k >= v.length) return;
                e.preventDefault();
                var after2 = countDigits(v.slice(k + 1));
                this.apply(v.slice(0, k) + v.slice(k + 1), after2);
                this.liveValidate();
            }
        }
    };

    // ---- Сумісний API ----
    PhoneMask.prototype.formatValue = function (value) {
        this.input.value = value ? format(parse(value)) : '';
        this._prev.value = this.input.value;
    };
    PhoneMask.prototype.ensurePrefix = function () { this.reformat(true); };
    PhoneMask.prototype.formatOnBlur = function () { this.onBlur(); };
    PhoneMask.prototype.validate = function () { return check(this.input); };
    PhoneMask.prototype.getCleanedValue = function () {
        var r = check(this.input);
        return r.cleaned || (this.input.value || '').replace(/[^\d+]/g, '');
    };
    PhoneMask.prototype.showError = function (m) { this._touched = true; showError(this.input, m || check(this.input).message); };
    PhoneMask.prototype.clearError = function () { clearError(this.input); };
    PhoneMask.prototype.destroy = function () {
        var h = this._handlers;
        Object.keys(h).forEach(function (k) { h[k].t.removeEventListener(h[k].type, h[k].fn); });
        this._handlers = {};
        delete this.input.__phoneMask;
        this.input.removeAttribute('data-phone-mask');
    };

    function shouldMask(input) {
        if (!input || input.tagName !== 'INPUT') return false;
        if (input.getAttribute('data-phone-mask') === 'off') return false;
        if (input.type === 'hidden') return false;
        return true;
    }

    function initAll(root) {
        var scope = root && root.querySelectorAll ? root : document;
        var list = [];
        if (scope.matches && scope.matches(SELECTOR)) list.push(scope);
        Array.prototype.push.apply(list, scope.querySelectorAll(SELECTOR));
        list.forEach(function (input) { if (shouldMask(input)) new PhoneMask(input); });
    }

    // Блокуємо submit з невалідним телефоном (capture → раніше за htmx та обробники форм)
    function guardSubmit(e) {
        var form = e.target;
        if (!form || form.tagName !== 'FORM') return;
        var inputs = form.querySelectorAll('input[data-phone-mask="on"]');
        var firstBad = null;
        Array.prototype.forEach.call(inputs, function (input) {
            if (input.disabled || !isVisible(input)) return;
            var r = check(input);
            if (!r.valid) {
                if (input.__phoneMask) input.__phoneMask._touched = true;
                showError(input, r.message);
                if (!firstBad) firstBad = input;
            } else {
                clearError(input);
                if (r.cleaned && input.__phoneMask) input.__phoneMask.reformat(true);
            }
        });
        if (firstBad) {
            e.preventDefault();
            e.stopImmediatePropagation();
            try { firstBad.focus({ preventScroll: false }); } catch (err) { firstBad.focus(); }
        }
    }

    function boot() {
        initAll(document);
        document.addEventListener('submit', guardSubmit, true);
        ['htmx:afterSwap', 'htmx:afterSettle', 'htmx:load'].forEach(function (ev) {
            document.addEventListener(ev, function (e) {
                initAll((e.detail && e.detail.elt) || e.target || document);
            });
        });
        // Серверна валідація форм з телефоном (400/422) → показуємо фрагмент з помилкою
        document.addEventListener('htmx:beforeSwap', function (e) {
            var d = e.detail || {};
            var st = d.xhr && d.xhr.status;
            var elt = d.requestConfig && d.requestConfig.elt;
            if ((st === 400 || st === 422) && elt && elt.tagName === 'FORM' &&
                elt.querySelector('input[data-phone-mask="on"]')) {
                d.shouldSwap = true;
                d.isError = false;
            }
        });
    }

    PhoneMask.parse = parse;
    PhoneMask.format = function (raw) { return format(parse(raw)); };
    PhoneMask.normalize = function (raw) { return parse(raw).e164 || null; };
    PhoneMask.check = check;
    PhoneMask.showError = function (input, m) {
        if (input.__phoneMask) input.__phoneMask._touched = true;
        showError(input, m || check(input).message);
    };
    PhoneMask.clearError = clearError;
    PhoneMask.initAll = initAll;
    PhoneMask.messages = MESSAGES;

    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
        global.PhoneMask = PhoneMask;
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
        else boot();
    }
    if (typeof module !== 'undefined' && module.exports) module.exports = PhoneMask;
})(typeof window !== 'undefined' ? window : globalThis);
