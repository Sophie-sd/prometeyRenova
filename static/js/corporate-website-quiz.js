/* corporate-website-quiz.js — multi-step quiz + DKI (dynamic keyword insertion) */

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

    const form = document.getElementById('corporate-website-quiz-form');
    if (!form) return;

    const steps        = Array.from(form.querySelectorAll('.cw-quiz__step'));
    const progressBar  = form.querySelector('[data-quiz-progress]');
    const stepNumEl    = form.querySelector('[data-quiz-step-num]');
    const prevBtn      = form.querySelector('.cw-quiz__prev');
    const nextBtn      = form.querySelector('.cw-quiz__next-btn');
    const navDiv       = form.querySelector('.cw-quiz__nav');
    const detailsInput = document.getElementById('quiz-details');
    const sourcePage   = form.dataset.sourceLabel || 'Корпоративний сайт';

    const QUESTION_STEPS = steps.filter(s => !s.classList.contains('cw-quiz__step--contact')).length;
    let currentIdx = 0;

    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    function showStep(idx) {
        steps.forEach((s, i) => { s.hidden = i !== idx; });

        const currentStep = steps[idx];
        const isContact   = currentStep?.classList.contains('cw-quiz__step--contact');
        const stepNum     = isContact ? QUESTION_STEPS : idx + 1;
        const progress    = isContact ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl)   stepNumEl.textContent    = stepNum;

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
    }

    function goNext() {
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goPrev() {
        if (currentIdx > 0) showStep(currentIdx - 1);
    }

    function handleMultiChange(input, step) {
        const option = input.closest('.cw-quiz__option');

        if (input.dataset.selectAll !== undefined) {
            const siblings = Array.from(
                step.querySelectorAll('input[type="checkbox"]:not([data-select-all])')
            );
            const checked = input.checked;
            siblings.forEach(cb => {
                cb.checked = checked;
                cb.closest('.cw-quiz__option')?.classList.toggle('cw-quiz__option--selected', checked);
            });
            option?.classList.toggle('cw-quiz__option--selected', checked);
        } else {
            option?.classList.toggle('cw-quiz__option--selected', input.checked);

            const selectAllCb = step.querySelector('input[data-select-all]');
            if (selectAllCb) {
                const allRegular = Array.from(
                    step.querySelectorAll('input[type="checkbox"]:not([data-select-all])')
                );
                const allChecked = allRegular.every(cb => cb.checked);
                selectAllCb.checked = allChecked;
                selectAllCb.closest('.cw-quiz__option')
                    ?.classList.toggle('cw-quiz__option--selected', allChecked);
            }
        }

        if (nextBtn) {
            const anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    form.addEventListener('change', (e) => {
        const input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        const step = input.closest('.cw-quiz__step');
        if (!step || step.classList.contains('cw-quiz__step--contact')) return;

        const isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
        } else {
            step.querySelectorAll('.cw-quiz__option').forEach(opt =>
                opt.classList.remove('cw-quiz__option--selected')
            );
            input.closest('.cw-quiz__option')?.classList.add('cw-quiz__option--selected');
            if (nextBtn) nextBtn.disabled = false;
            setTimeout(goNext, 340);
        }
    });

    nextBtn?.addEventListener('click', goNext);
    prevBtn?.addEventListener('click', goPrev);

    function compileDetails() {
        if (!detailsInput) return;
        const fields = [
            { name: 'q_business_type', label: 'Тип бізнесу' },
            { name: 'q_pages',         label: 'Кількість сторінок' },
            { name: 'q_marketing',     label: 'Маркетинг-пакет', multi: true },
            { name: 'q_integrations',  label: 'Інтеграції',      multi: true },
            { name: 'q_timeline',      label: 'Терміни' },
        ];
        const parts = [`Сторінка: ${sourcePage}`];
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

    showStep(0);
})();
