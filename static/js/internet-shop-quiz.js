/* internet-shop-quiz.js — multi-step quiz */
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
    function compileDetails() {
        if (!detailsInput) return;
        const fields = [
            { name: 'q_need',       label: 'Що потрібно' },
            { name: 'q_products',   label: 'Кількість товарів' },
            { name: 'q_automation', label: 'Автоматизація', multi: true },
            { name: 'q_accounts',   label: 'Особисті кабінети' },
            { name: 'q_timeline',   label: 'Терміни' },
        ];
        const parts = ['Сторінка: Інтернет-магазин'];
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

    /* ── Ініціалізація ──────────────────────────────────────── */
    showStep(0);
})();
