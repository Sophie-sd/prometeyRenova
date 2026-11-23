/* corporate-website-v2-quiz.js — multi-step quiz */

(function () {
    'use strict';

    var form = document.getElementById('pl-corp-quiz-form');
    if (!form) return;

    var isRu = (document.documentElement.lang || '').toLowerCase().indexOf('ru') === 0
        || /^\/ru\//.test(location.pathname);
    var isEn = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0;
    var PHONE_MSG_EMPTY = isRu ? 'Внесите номер телефона' : isEn ? 'Enter your phone number' : 'Внесіть номер телефону';
    var PHONE_MSG_INVALID = isRu ? 'Введите корректный номер телефона' : isEn ? 'Enter a valid phone number' : 'Введіть коректний номер телефону';

    var steps = Array.from(form.querySelectorAll('.pl-corp__quiz-step'));
    var stage = form.querySelector('.pl-corp__quiz-stage');
    var progressBar = form.querySelector('[data-quiz-progress]');
    var stepNumEl = form.querySelector('[data-quiz-step-num]');
    var prevBtn = form.querySelector('.pl-corp__quiz-prev');
    var skipBtn = form.querySelector('.pl-corp__quiz-skip');
    var nextBtn = form.querySelector('.pl-corp__quiz-next');
    var navDiv = form.querySelector('.pl-corp__quiz-nav');
    var revealBtn = form.querySelector('[data-quiz-reveal]');
    var nameInput = form.querySelector('#pl-corp-quiz-name');
    var phoneInput = form.querySelector('#pl-corp-quiz-phone');
    var detailsInput = document.getElementById('pl-corp-quiz-details');

    var questionSteps = steps.filter(function (s) {
        return !s.classList.contains('pl-corp__quiz-step--contact');
    });
    var QUESTION_STEPS = questionSteps.length;

    var currentIdx = 0;
    var resizeTimer;
    var lockedStageHeight = 0;
    var isMeasuring = false;

    function setNavSlot(btn, visible) {
        if (!btn) return;
        btn.classList.toggle('pl-corp__quiz-nav-slot--hidden', !visible);
        btn.setAttribute('aria-hidden', visible ? 'false' : 'true');
        btn.tabIndex = visible ? 0 : -1;
    }

    function measureStageHeight() {
        if (!stage || !steps.length || isMeasuring) return;

        isMeasuring = true;
        var activeIdx = currentIdx;
        var max = 0;
        var measureSteps = questionSteps.length ? questionSteps : steps;

        stage.classList.add('pl-corp__quiz-stage--measure');
        stage.style.removeProperty('height');
        stage.style.removeProperty('min-height');
        form.style.removeProperty('--pl-corp-quiz-stage-h');

        measureSteps.forEach(function (step) {
            steps.forEach(function (item) {
                item.classList.remove('pl-corp__quiz-step--active', 'pl-corp__quiz-step--measure-target');
            });
            step.classList.add('pl-corp__quiz-step--active', 'pl-corp__quiz-step--measure-target');
            max = Math.max(max, stage.offsetHeight);
        });

        stage.classList.remove('pl-corp__quiz-stage--measure');
        lockedStageHeight = Math.max(lockedStageHeight, max);
        applyStageHeight();
        showStep(activeIdx);
        isMeasuring = false;
    }

    function applyStageHeight() {
        if (!stage) return;

        var currentStep = steps[currentIdx];
        var isFluidStep = currentStep && currentStep.classList.contains('pl-corp__quiz-step--contact');

        stage.classList.toggle('pl-corp__quiz-stage--fluid', !!isFluidStep);

        if (isFluidStep) {
            stage.style.height = 'auto';
            stage.style.minHeight = '0';
            form.style.removeProperty('--pl-corp-quiz-stage-h');
            return;
        }

        stage.classList.remove('pl-corp__quiz-stage--fluid');

        if (!lockedStageHeight) return;
        var heightValue = lockedStageHeight + 'px';
        stage.style.height = heightValue;
        stage.style.minHeight = heightValue;
        form.style.setProperty('--pl-corp-quiz-stage-h', heightValue);
    }

    function scheduleMeasure() {
        if (isMeasuring) return;
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(measureStageHeight, 60);
    }

    function countDigits(str) {
        return (str.match(/\d/g) || []).length;
    }

    function getCheckedValue(name) {
        var input = form.querySelector('input[name="' + name + '"]:checked');
        return input ? input.value : null;
    }

    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    function isQuestionStep(step) {
        return step && !step.classList.contains('pl-corp__quiz-step--contact');
    }

    function showPhoneError(message) {
        if (!phoneInput) return;
        if (window.PhoneMask && window.PhoneMask.showError) {
            window.PhoneMask.showError(phoneInput, message);
            return;
        }
        phoneInput.classList.add('error');
        var existing = phoneInput.parentElement.querySelector('.pl-corp__quiz-field-error');
        if (existing) existing.remove();
        var err = document.createElement('p');
        err.className = 'pl-corp__quiz-field-error';
        err.setAttribute('role', 'alert');
        err.textContent = message;
        phoneInput.parentElement.appendChild(err);
    }

    function clearPhoneError() {
        if (!phoneInput) return;
        if (window.PhoneMask && window.PhoneMask.clearError) window.PhoneMask.clearError(phoneInput);
        phoneInput.classList.remove('error');
        var existing = phoneInput.parentElement.querySelector('.pl-corp__quiz-field-error');
        if (existing) existing.remove();
    }

    function compileDetails() {
        if (!detailsInput) return;

        var fields = [
            { name: 'q_business', label: 'Тип бізнесу' },
            { name: 'q_goal', label: 'Бізнес-ціль' },
            { name: 'q_pages', label: 'Кількість сторінок' },
            { name: 'q_options', label: 'Додаткові опції' },
            { name: 'q_timeline', label: 'Терміни' }
        ];

        var parts = ['Сторінка: ' + (form.dataset.sourceLabel || 'Корпоративний сайт v2')];

        fields.forEach(function (field) {
            var val = getCheckedValue(field.name);
            if (val) parts.push(field.label + ': ' + val);
        });

        detailsInput.value = parts.join('\n');
    }

    function showStep(idx) {
        steps.forEach(function (s, i) {
            var isActive = i === idx;
            s.classList.toggle('pl-corp__quiz-step--active', isActive);
            s.removeAttribute('hidden');
            s.setAttribute('aria-hidden', isActive ? 'false' : 'true');
        });

        applyStageHeight();

        var currentStep = steps[idx];
        var isContact = currentStep && currentStep.classList.contains('pl-corp__quiz-step--contact');
        var isQuestion = isQuestionStep(currentStep);
        var stepNum = isContact ? QUESTION_STEPS : idx + 1;
        var progress = isContact ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl) stepNumEl.textContent = String(stepNum);

        var showPrev = idx > 0 && isQuestion;
        var showNext = isQuestion;
        var showSkip = isQuestion;

        if (navDiv) navDiv.hidden = !showPrev && !showNext && !showSkip;

        setNavSlot(prevBtn, showPrev);
        setNavSlot(skipBtn, showSkip);

        if (nextBtn) {
            setNavSlot(nextBtn, showNext);
            if (showNext) {
                nextBtn.disabled = !isStepAnswered(currentStep);
            }
        }

        currentIdx = idx;
    }

    function prepareSubmit() {
        compileDetails();
    }

    function goNext() {
        var currentStep = steps[currentIdx];
        if (!isQuestionStep(currentStep)) return;
        if (!isStepAnswered(currentStep)) return;
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goSkip() {
        var currentStep = steps[currentIdx];
        if (!isQuestionStep(currentStep)) return;
        if (currentIdx < steps.length - 1) showStep(currentIdx + 1);
    }

    function goPrev() {
        if (currentIdx > 0) showStep(currentIdx - 1);
    }

    function handleMultiChange(input, step) {
        var option = input.closest('.pl-corp__quiz-option');
        if (option) option.classList.toggle('pl-corp__quiz-option--selected', input.checked);

        if (nextBtn) {
            var anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    form.addEventListener('change', function (e) {
        var input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        var step = input.closest('.pl-corp__quiz-step');
        if (!step || !isQuestionStep(step)) return;

        var isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
            return;
        }

        step.querySelectorAll('.pl-corp__quiz-option').forEach(function (opt) {
            opt.classList.remove('pl-corp__quiz-option--selected');
        });
        var selected = input.closest('.pl-corp__quiz-option');
        if (selected) selected.classList.add('pl-corp__quiz-option--selected');
        if (nextBtn) nextBtn.disabled = false;
    });

    form.addEventListener('submit', function () {
        compileDetails();
    });

    if (phoneInput) {
        phoneInput.addEventListener('input', clearPhoneError);
    }

    /* Phone mask keeps a non-removable "+38" prefix, so native `required`
       passes on an empty number — check digits before letting the form submit. */
    function getPhoneError() {
        if (!phoneInput) return '';
        if (window.PhoneMask && window.PhoneMask.check) {
            var r = window.PhoneMask.check(phoneInput);
            return r.valid ? '' : r.message;
        }
        var raw = phoneInput.value.trim();
        var digits = countDigits(raw);
        var national = raw.indexOf('+38') === 0 ? digits - 2 : digits;
        if (national <= 0 && raw.replace(/^\+38/, '').trim().length === 0) return PHONE_MSG_EMPTY;
        if (digits < 7) return PHONE_MSG_INVALID;
        return '';
    }

    function handleRevealClick(e) {
        var phoneError = getPhoneError();
        if (phoneError) {
            e.preventDefault();
            showPhoneError(phoneError);
            if (nameInput && !nameInput.checkValidity()) {
                nameInput.reportValidity();
            } else if (phoneInput) {
                phoneInput.focus();
            }
            return;
        }
        clearPhoneError();
        prepareSubmit();
    }

    if (revealBtn) revealBtn.addEventListener('click', handleRevealClick);
    /* Enter on a question step = "Next" (never Skip, never the contact submit) */
    form.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' || e.isComposing) return;
        if (!isQuestionStep(steps[currentIdx])) return;
        var tag = e.target && e.target.tagName;
        if (tag === 'BUTTON' || tag === 'TEXTAREA' || tag === 'A') return;
        e.preventDefault();
        goNext();
    });

    if (skipBtn) skipBtn.addEventListener('click', goSkip);
    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);

    showStep(0);
    measureStageHeight();

    window.addEventListener('resize', scheduleMeasure, { passive: true });

    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(measureStageHeight);
    }
})();
