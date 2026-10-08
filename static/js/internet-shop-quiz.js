/* internet-shop-quiz.js — multi-step quiz + DKI (dynamic keyword insertion) */

/* ── DKI: read ?kw= from URL and inject into [data-dki] ─────── */
(function () {
    'use strict';
    try {
        const params = new URLSearchParams(window.location.search);
        const raw = params.get('kw');
        if (!raw) return;
        const cleaned = raw.replace(/[^a-zа-яёіїєґ\s\-]/gi, '').trim().slice(0, 60);
        if (cleaned.length < 3) return;
        const capitalized = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
        const targets = document.querySelectorAll('[data-dki]');
        targets.forEach((el) => {
            el.textContent = capitalized;
        });
    } catch (e) {
        /* fail-safe: leave fallback text intact */
    }
})();

(function () {
    'use strict';

    const form = document.getElementById('internet-shop-quiz-form');
    if (!form) return;

    const steps        = Array.from(form.querySelectorAll('.is-quiz__step'));
    const progressBar  = form.querySelector('[data-quiz-progress]');
    const stepNumEl    = form.querySelector('[data-quiz-step-num]');
    const prevBtn      = form.querySelector('.is-quiz__prev');
    const nextBtn      = form.querySelector('.is-quiz__next-btn');
    const navDiv       = form.querySelector('.is-quiz__nav');
    const detailsInput = document.getElementById('quiz-details');
    const submitBtn    = form.querySelector('.is-quiz__submit');
    const nameInput    = form.querySelector('#quiz-name');
    const phoneInput   = form.querySelector('#quiz-phone');

    const isRu = (document.documentElement.lang || '').toLowerCase().indexOf('ru') === 0
        || /^\/ru\//.test(location.pathname);
    const PHONE_MSG_EMPTY   = isRu ? 'Внесите номер телефона' : 'Внесіть номер телефону';
    const PHONE_MSG_INVALID = isRu ? 'Введите корректный номер телефона' : 'Введіть коректний номер телефону';
    const PHONE_ERROR_ID    = 'quiz-phone-error';

    const QUESTION_STEPS = steps.filter(s => !s.classList.contains('is-quiz__step--contact')).length;
    let currentIdx = 0;

    /* ── Чи є хоч одна вибрана відповідь у кроці ──────────── */
    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    /* ── Відображення кроку ─────────────────────────────────── */
    function showStep(idx) {
        steps.forEach((s, i) => { s.hidden = i !== idx; });

        const currentStep = steps[idx];
        const isContact   = currentStep?.classList.contains('is-quiz__step--contact');
        const stepNum     = isContact ? QUESTION_STEPS : idx + 1;
        const progress    = isContact ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl)   stepNumEl.textContent    = stepNum;

        /* На контактному кроці весь nav зникає; деталі збираємо одразу */
        if (navDiv) navDiv.hidden = isContact;
        if (isContact) compileDetails();

        if (!isContact) {
            if (nextBtn) {
                nextBtn.hidden   = false;
                nextBtn.disabled = !isStepAnswered(currentStep);
            }
            if (prevBtn) prevBtn.hidden = idx === 0;
        }

        currentIdx = idx;
        /* Без scrollIntoView — користувач лишається на місці */
    }

    function goNext() {
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goPrev() {
        if (currentIdx > 0) showStep(currentIdx - 1);
    }

    /* ── Логіка мульти-вибору (крок 3) ─────────────────────── */
    function handleMultiChange(input, step) {
        const option = input.closest('.is-quiz__option');

        if (input.dataset.selectAll !== undefined) {
            /* "Все з переліченого" — синхронізуємо всі інші */
            const siblings = Array.from(
                step.querySelectorAll('input[type="checkbox"]:not([data-select-all])')
            );
            const checked = input.checked;
            siblings.forEach(cb => {
                cb.checked = checked;
                cb.closest('.is-quiz__option')?.classList.toggle('is-quiz__option--selected', checked);
            });
            option?.classList.toggle('is-quiz__option--selected', checked);
        } else {
            /* Одиночний варіант */
            option?.classList.toggle('is-quiz__option--selected', input.checked);

            const selectAllCb = step.querySelector('input[data-select-all]');
            if (selectAllCb) {
                const allRegular = Array.from(
                    step.querySelectorAll('input[type="checkbox"]:not([data-select-all])')
                );
                const allChecked = allRegular.every(cb => cb.checked);
                selectAllCb.checked = allChecked;
                selectAllCb.closest('.is-quiz__option')
                    ?.classList.toggle('is-quiz__option--selected', allChecked);
            }
        }

        /* Активуємо кнопку "Далі" якщо хоч щось вибрано */
        if (nextBtn) {
            const anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    /* ── Обробник зміни значень ─────────────────────────────── */
    form.addEventListener('change', (e) => {
        const input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        const step = input.closest('.is-quiz__step');
        if (!step || step.classList.contains('is-quiz__step--contact')) return;

        const isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
        } else {
            /* Radio: позначаємо вибране, активуємо "Далі", авто-перехід */
            step.querySelectorAll('.is-quiz__option').forEach(opt =>
                opt.classList.remove('is-quiz__option--selected')
            );
            input.closest('.is-quiz__option')?.classList.add('is-quiz__option--selected');
            if (nextBtn) nextBtn.disabled = false;
            setTimeout(goNext, 340);
        }
    });

    /* ── Кнопка "Далі" ──────────────────────────────────────── */
    nextBtn?.addEventListener('click', goNext);

    /* ── Назад ──────────────────────────────────────────────── */
    prevBtn?.addEventListener('click', goPrev);

    /* ── Збираємо відповіді перед відправкою ───────────────── */
    function parseQuizLabels() {
        try {
            return JSON.parse(form.dataset.quizLabels || '{}');
        } catch (e) {
            return {};
        }
    }

    function compileDetails() {
        if (!detailsInput) return;
        const customLabels = parseQuizLabels();
        const pagePrefix = form.dataset.pagePrefix || 'Сторінка';
        const fields = [
            { name: 'q_need',       label: customLabels.q_need || 'Що потрібно' },
            { name: 'q_products',   label: customLabels.q_products || 'Кількість товарів' },
            { name: 'q_automation', label: customLabels.q_automation || 'Автоматизація', multi: true },
            { name: 'q_accounts',   label: customLabels.q_accounts || 'Особисті кабінети' },
            { name: 'q_timeline',   label: customLabels.q_timeline || 'Терміни' },
        ];
        const parts = [`${pagePrefix}: ${form.dataset.sourceLabel || 'Інтернет-магазин'}`];
        fields.forEach(({ name, label, multi }) => {
            if (multi) {
                const vals = Array.from(form.querySelectorAll(`input[name="${name}"]:checked`))
                    .filter(cb => !cb.dataset.selectAll)
                    .map(cb => cb.value);
                if (vals.length) parts.push(`${label}: ${vals.join(', ')}`);
            } else {
                const cb = form.querySelector(`input[name="${name}"]:checked`);
                if (cb) parts.push(`${label}: ${cb.value}`);
            }
        });
        detailsInput.value = parts.join('\n');
    }

    /* ── Телефон на контактному кроці ──────────────────────────
       Маска тримає префікс "+38", тож native `required` не спрацьовує
       на порожньому номері — перевіряємо цифри самі. */
    function getPhoneError() {
        if (!phoneInput) return '';
        const raw = phoneInput.value.trim();
        const digits = raw.replace(/\D/g, '');
        const national = raw.indexOf('+38') === 0 ? digits.slice(2) : digits;
        if (!national.length) return PHONE_MSG_EMPTY;
        if (digits.length < 7) return PHONE_MSG_INVALID;
        return '';
    }

    function showPhoneError(message) {
        if (!phoneInput) return;
        let err = document.getElementById(PHONE_ERROR_ID);
        if (!err) {
            err = document.createElement('p');
            err.id = PHONE_ERROR_ID;
            err.className = 'is-quiz__field-error';
            err.setAttribute('role', 'alert');
            phoneInput.parentElement.appendChild(err);
        }
        err.textContent = message;
        phoneInput.classList.add('error');
        phoneInput.setAttribute('aria-invalid', 'true');
        phoneInput.setAttribute('aria-describedby', PHONE_ERROR_ID);
    }

    function clearPhoneError() {
        if (!phoneInput) return;
        const err = document.getElementById(PHONE_ERROR_ID);
        if (err) err.remove();
        phoneInput.classList.remove('error');
        phoneInput.removeAttribute('aria-invalid');
        phoneInput.removeAttribute('aria-describedby');
    }

    submitBtn?.addEventListener('click', (e) => {
        const phoneError = getPhoneError();
        if (!phoneError) {
            clearPhoneError();
            return;
        }
        e.preventDefault();
        showPhoneError(phoneError);
        if (nameInput && !nameInput.checkValidity()) nameInput.reportValidity();
        else phoneInput.focus();
    });
    phoneInput?.addEventListener('input', clearPhoneError);

    /* ── Ініціалізація ──────────────────────────────────────── */
    showStep(0);
})();
