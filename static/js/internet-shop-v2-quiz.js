/* internet-shop-v2-quiz.js — multi-step quiz + package recommendation */

(function () {
    'use strict';

    var form = document.getElementById('pl-shop-quiz-form');
    if (!form) return;

    var PKG_MAP = {
        base: {
            label: 'BASE',
            price: 'від 800\u00a0€',
            term: '3–4 тижні',
            features: [
                'Базовий конверсійний дизайн під нішу',
                'ШІ-контент та базова SEO-підготовка',
                'Розгортання під ключ на вашому домені'
            ]
        },
        premium: {
            label: 'PREMIUM',
            price: 'від 1\u00a0500\u00a0€',
            term: '5–8 тижнів',
            features: [
                'Індивідуальний UI/UX дизайн з нуля',
                'Інтеграції: платежі, логістика, CRM',
                'Контент-маркетинг та SEO-статті'
            ]
        },
        platinum: {
            label: 'PLATINUM',
            price: 'від 7\u00a0000\u00a0€',
            term: '2–4 місяці',
            features: [
                'Premium UI/UX + кінематографічна анімація',
                'AI-екосистема адмінки та Telegram-бот',
                '6 місяців контент-маркетингу та медіакампанії'
            ]
        }
    };

    var steps = Array.from(form.querySelectorAll('.pl-shop__quiz-step'));
    var progressBar = form.querySelector('[data-quiz-progress]');
    var stepNumEl = form.querySelector('[data-quiz-step-num]');
    var prevBtn = form.querySelector('.pl-shop__quiz-prev');
    var skipBtn = form.querySelector('.pl-shop__quiz-skip');
    var nextBtn = form.querySelector('.pl-shop__quiz-next');
    var navDiv = form.querySelector('.pl-shop__quiz-nav');
    var revealBtn = form.querySelector('[data-quiz-reveal]');
    var nameInput = form.querySelector('#pl-shop-quiz-name');
    var phoneInput = form.querySelector('#pl-shop-quiz-phone');
    var detailsInput = document.getElementById('pl-shop-quiz-details');
    var resultRoot = form.querySelector('[data-quiz-result]');

    var QUESTION_STEPS = steps.filter(function (s) {
        return !s.classList.contains('pl-shop__quiz-step--contact')
            && !s.classList.contains('pl-shop__quiz-step--result');
    }).length;

    var resultStepIdx = steps.findIndex(function (s) {
        return s.classList.contains('pl-shop__quiz-step--result');
    });

    var currentIdx = 0;

    function getPkgHint() {
        try {
            return sessionStorage.getItem('pl_shop_pkg_hint');
        } catch (e) {
            return null;
        }
    }

    function clearPkgHint() {
        try {
            sessionStorage.removeItem('pl_shop_pkg_hint');
        } catch (e) { /* ignore */ }
    }

    function getCheckedValue(name) {
        var input = form.querySelector('input[name="' + name + '"]:checked');
        return input ? input.value : null;
    }

    function getCheckedFeatures() {
        return Array.from(form.querySelectorAll('input[name="q_features"]:checked'))
            .map(function (cb) { return cb.value; });
    }

    function recommendPackage() {
        var score = { base: 0, premium: 0, platinum: 0 };
        var start = getCheckedValue('q_start');
        var products = getCheckedValue('q_products');
        var features = getCheckedFeatures();
        var timeline = getCheckedValue('q_timeline');

        if (start === 'Старт з нуля') score.base += 2;
        if (start === 'Міграція з Prom / OLX') score.premium += 2;
        if (start === 'Масштабування + маркетинг під ключ') score.platinum += 3;
        if (start === 'Ще не визначився') score.premium += 1;

        if (products === 'До 100 товарів') score.base += 2;
        if (products === '100–1000 товарів') score.premium += 2;
        if (products === '1000–10 000 товарів') score.platinum += 2;
        if (products === 'Більше 10 000 товарів') score.platinum += 3;

        features.forEach(function (val) {
            if (val === 'CRM + Telegram') { score.premium += 2; }
            if (val === 'SEO + статті') { score.premium += 2; score.platinum += 1; }
            if (val === 'AI-адмінка + бот') { score.platinum += 3; }
            if (val === 'Реклама та просування') { score.platinum += 2; }
        });

        if (features.length <= 1) score.base += 1;
        if (features.length >= 2 && features.length <= 3) score.premium += 1;
        if (features.length >= 4) score.platinum += 2;

        if (timeline === 'Якнайшвидше (до 2 тижнів)') score.base += 2;
        if (timeline === 'Протягом місяця') score.premium += 2;
        if (timeline === '1–3 місяці') score.platinum += 1;
        if (timeline === 'Терміни гнучкі') score.platinum += 1;

        var pkgHint = getPkgHint();
        if (pkgHint && PKG_MAP[pkgHint]) {
            score[pkgHint] += 1;
        }

        var best = 'premium';
        var bestScore = -1;
        Object.keys(score).forEach(function (key) {
            if (score[key] > bestScore) {
                bestScore = score[key];
                best = key;
            }
        });

        return best;
    }

    function updateResultPreview(pkgKey) {
        var data = PKG_MAP[pkgKey];
        if (!data || !resultRoot) return;

        var pkgEl = resultRoot.querySelector('[data-quiz-result-pkg]');
        var priceEl = resultRoot.querySelector('[data-quiz-result-price]');
        var termEl = resultRoot.querySelector('[data-quiz-result-term]');
        var featuresEl = resultRoot.querySelector('[data-quiz-result-features]');

        if (pkgEl) pkgEl.textContent = data.label;
        if (priceEl) priceEl.textContent = data.price;
        if (termEl) termEl.textContent = data.term;

        if (featuresEl) {
            featuresEl.innerHTML = '';
            data.features.forEach(function (text) {
                var li = document.createElement('li');
                li.textContent = text;
                featuresEl.appendChild(li);
            });
        }
    }

    function isStepAnswered(step) {
        return !!step.querySelector('input[type="radio"]:checked, input[type="checkbox"]:checked');
    }

    function isQuestionStep(step) {
        return step
            && !step.classList.contains('pl-shop__quiz-step--contact')
            && !step.classList.contains('pl-shop__quiz-step--result');
    }

    function validateContactFields() {
        var valid = true;

        if (nameInput) {
            if (!nameInput.checkValidity()) {
                nameInput.reportValidity();
                valid = false;
            }
        }

        if (phoneInput) {
            if (!phoneInput.checkValidity()) {
                phoneInput.reportValidity();
                valid = false;
            }
        }

        return valid;
    }

    function compileDetails() {
        if (!detailsInput) return;

        var pkgKey = recommendPackage();
        var data = PKG_MAP[pkgKey];
        var pkgHint = getPkgHint();
        var fields = [
            { name: 'q_start', label: 'Старт проєкту' },
            { name: 'q_products', label: 'Кількість товарів' },
            { name: 'q_features', label: 'Додаткові опції', multi: true },
            { name: 'q_timeline', label: 'Терміни' }
        ];

        var parts = ['Сторінка: ' + (form.dataset.sourceLabel || 'Інтернет-магазин v2')];

        if (data) {
            parts.push('Рекомендований пакет: ' + data.label + ' · ' + data.price + ' · ' + data.term);
        }

        fields.forEach(function (field) {
            if (field.multi) {
                var vals = getCheckedFeatures();
                if (vals.length) parts.push(field.label + ': ' + vals.join(', '));
            } else {
                var val = getCheckedValue(field.name);
                if (val) parts.push(field.label + ': ' + val);
            }
        });

        if (pkgHint && PKG_MAP[pkgHint]) {
            parts.push('Підказка з картки пакета: ' + PKG_MAP[pkgHint].label);
        }

        detailsInput.value = parts.join('\n');
    }

    function showStep(idx) {
        steps.forEach(function (s, i) { s.hidden = i !== idx; });

        var currentStep = steps[idx];
        var isContact = currentStep && currentStep.classList.contains('pl-shop__quiz-step--contact');
        var isResult = currentStep && currentStep.classList.contains('pl-shop__quiz-step--result');
        var isQuestion = isQuestionStep(currentStep);
        var stepNum = isResult ? QUESTION_STEPS : (isContact ? QUESTION_STEPS : idx + 1);
        var progress = (isContact || isResult) ? 100 : ((idx + 1) / QUESTION_STEPS) * 100;

        if (progressBar) progressBar.style.width = progress + '%';
        if (stepNumEl) stepNumEl.textContent = String(stepNum);

        var showPrev = idx > 0;
        var showNext = isQuestion;
        var showSkip = isQuestion;

        if (navDiv) navDiv.hidden = !showPrev && !showNext && !showSkip;

        if (prevBtn) prevBtn.hidden = !showPrev;

        if (skipBtn) skipBtn.hidden = !showSkip;

        if (nextBtn) {
            nextBtn.hidden = !showNext;
            if (showNext) {
                nextBtn.disabled = !isStepAnswered(currentStep);
            }
        }

        currentIdx = idx;
    }

    function prepareSubmit() {
        compileDetails();
        clearPkgHint();
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
        var option = input.closest('.pl-shop__quiz-option');
        if (option) option.classList.toggle('pl-shop__quiz-option--selected', input.checked);

        if (nextBtn) {
            var anyChecked = step.querySelector('input[type="checkbox"]:checked');
            nextBtn.disabled = !anyChecked;
        }
    }

    form.addEventListener('change', function (e) {
        var input = e.target;
        if (input.type !== 'radio' && input.type !== 'checkbox') return;

        var step = input.closest('.pl-shop__quiz-step');
        if (!step || !isQuestionStep(step)) return;

        var isMulti = step.dataset.multi === 'true';

        if (isMulti) {
            handleMultiChange(input, step);
            return;
        }

        step.querySelectorAll('.pl-shop__quiz-option').forEach(function (opt) {
            opt.classList.remove('pl-shop__quiz-option--selected');
        });
        var selected = input.closest('.pl-shop__quiz-option');
        if (selected) selected.classList.add('pl-shop__quiz-option--selected');
        if (nextBtn) nextBtn.disabled = false;
    });

    if (revealBtn) revealBtn.addEventListener('click', prepareSubmit);
    if (skipBtn) skipBtn.addEventListener('click', goSkip);
    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);

    showStep(0);
})();
