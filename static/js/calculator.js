/* CALCULATOR.JS - Повна логіка калькулятора з тестом */

class ProjectCalculator {
    constructor() {
        this.testForm = document.getElementById('calculator-test');
        this.currentStep = 0;
        this.totalSteps = 5;
        this.answers = {};
        this.userInfo = {};

        this.init();
    }

    init() {
        if (!this.testForm) return;

        this.setupEventListeners();
        this.setupStepNavigation();
        this.loadSavedData();

        console.log('Project Calculator initialized');
    }

    setupEventListeners() {
        // Обробка відправки форми
        this.testForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Обробка вибору відповідей
        const radioButtons = this.testForm.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleAnswerChange(e);
            });
        });

        // Обробка полів користувача
        const userFields = this.testForm.querySelectorAll('.user-data input');
        userFields.forEach(field => {
            field.addEventListener('blur', (e) => {
                this.saveUserInfo(e.target.name, e.target.value);
            });
        });
    }

    setupStepNavigation() {
        // Можна додати кроки для більш гладкого UX
        const questions = this.testForm.querySelectorAll('.question');

        questions.forEach((question, index) => {
            question.setAttribute('data-step', index + 1);

            // Додаємо progress індикатор
            if (index === 0) {
                this.addProgressIndicator();
            }
        });
    }

    addProgressIndicator() {
        const progressBar = document.createElement('div');
        progressBar.className = 'test-progress mb-md';
        progressBar.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <span class="progress-text">Питання <span class="current">0</span> з <span class="total">${this.totalSteps}</span></span>
        `;

        // Додаємо стилі для progress bar
        if (!document.querySelector('.progress-styles')) {
            const style = document.createElement('style');
            style.className = 'progress-styles';
            style.textContent = `
                .test-progress { text-align: center; }
                .progress-bar { 
                    width: 100%; 
                    height: 8px; 
                    background: var(--color-gray); 
                    border: 1px solid var(--color-red);
                    margin-bottom: 10px;
                }
                .progress-fill { 
                    height: 100%; 
                    background: var(--color-red); 
                    transition: width 0.3s ease-out;
                }
                .progress-text { 
                    font-size: var(--font-small); 
                    color: var(--color-black);
                }
            `;
            document.head.appendChild(style);
        }

        this.testForm.insertBefore(progressBar, this.testForm.firstElementChild);
    }

    handleAnswerChange(event) {
        const questionNum = event.target.name;
        const answer = event.target.value;

        this.answers[questionNum] = answer;
        this.updateProgress();

        // Зберігаємо в sessionStorage
        sessionStorage.setItem('calculator_answers', JSON.stringify(this.answers));

        console.log('Answer recorded:', questionNum, answer);

        // Можна додати логіку автоматичного переходу до наступного питання
        this.autoAdvanceIfNeeded(questionNum);
    }

    updateProgress() {
        const answered = Object.keys(this.answers).length;
        const progress = (answered / this.totalSteps) * 100;

        const progressFill = document.querySelector('.progress-fill');
        const currentSpan = document.querySelector('.progress-text .current');

        if (progressFill) progressFill.style.width = `${progress}%`;
        if (currentSpan) currentSpan.textContent = answered;
    }

    autoAdvanceIfNeeded(questionNum) {
        // Плавний scroll до наступного питання
        const currentQuestionNum = parseInt(questionNum.split('_')[1]);
        if (currentQuestionNum < this.totalSteps) {
            setTimeout(() => {
                const nextQuestion = document.querySelector(`input[name="question_${currentQuestionNum + 1}"]`);
                if (nextQuestion) {
                    nextQuestion.closest('.question').scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }, 500);
        } else {
            // Всі питання відповіли - фокус на поля користувача
            setTimeout(() => {
                const nameField = document.querySelector('#test-name');
                if (nameField && !nameField.value) {
                    nameField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    nameField.focus();
                }
            }, 500);
        }
    }

    loadSavedData() {
        // Завантажуємо збережені відповіді
        const savedAnswers = sessionStorage.getItem('calculator_answers');
        if (savedAnswers) {
            this.answers = JSON.parse(savedAnswers);
            this.restoreAnswers();
        }

        // Завантажуємо дані користувача якщо є
        const savedUserData = sessionStorage.getItem('prometey_user_data');
        if (savedUserData) {
            const userData = JSON.parse(savedUserData);
            this.prefillUserData(userData);
        }
    }

    restoreAnswers() {
        Object.entries(this.answers).forEach(([question, answer]) => {
            const radio = document.querySelector(`input[name="${question}"][value="${answer}"]`);
            if (radio) {
                radio.checked = true;
            }
        });
        this.updateProgress();
    }

    prefillUserData(userData) {
        if (userData.name) {
            const nameField = document.querySelector('#test-name');
            if (nameField) nameField.value = userData.name;
        }

        if (userData.phone) {
            const phoneField = document.querySelector('#test-phone');
            if (phoneField) phoneField.value = userData.phone;
        }
    }

    saveUserInfo(field, value) {
        this.userInfo[field] = value;

        // Оновлюємо глобальні дані користувача
        let globalUserData = {};
        const saved = sessionStorage.getItem('prometey_user_data');
        if (saved) {
            globalUserData = JSON.parse(saved);
        }

        globalUserData[field] = value;
        globalUserData.timestamp = Date.now();
        sessionStorage.setItem('prometey_user_data', JSON.stringify(globalUserData));
    }

    async handleSubmit() {
        // Валідація
        if (!this.validateForm()) {
            return;
        }

        // Збираємо всі дані
        const formData = new FormData(this.testForm);

        // Додаємо відповіді як окремі поля
        Object.entries(this.answers).forEach(([question, answer]) => {
            formData.append(question, answer);
        });

        // Показуємо індикатор завантаження
        const submitBtn = this.testForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Розраховуємо...';
        submitBtn.disabled = true;

        try {
            // AJAX запит
            const response = await fetch('/forms/test/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showResult(result);
                this.clearSavedData();
            } else {
                throw new Error(result.message || 'Помилка розрахунку');
            }

        } catch (error) {
            console.error('Calculation error:', error);
            this.showError(error.message);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    validateForm() {
        // Перевіряємо чи всі питання відповіли
        for (let i = 1; i <= this.totalSteps; i++) {
            if (!this.answers[`question_${i}`]) {
                this.showError(`Будь ласка, дайте відповідь на питання ${i}`);

                // Скролимо до питання
                const question = document.querySelector(`input[name="question_${i}"]`);
                if (question) {
                    question.closest('.question').scrollIntoView({ behavior: 'smooth' });
                }
                return false;
            }
        }

        // Перевіряємо дані користувача
        const name = this.testForm.querySelector('#test-name').value;
        const phone = this.testForm.querySelector('#test-phone').value;

        if (!name || !phone) {
            this.showError('Будь ласка, введіть ваше ім\'я та номер телефону');
            return false;
        }

        return true;
    }

    showResult(result) {
        // Створюємо красивий результат
        const resultModal = document.createElement('div');
        resultModal.className = 'calculation-result';
        resultModal.innerHTML = `
            <div class="result-content bg-white p-md">
                <button class="modal-close" onclick="this.closest('.calculation-result').remove()">&times;</button>
                <h2 class="text-large color-red mb-sm text-center">Результат розрахунку</h2>
                <div class="price-result text-center mb-md">
                    <div class="estimated-price text-mega color-red">${result.estimated_price} грн</div>
                    <p class="text-base">Орієнтовна вартість вашого проекту</p>
                </div>
                <div class="result-details mb-md">
                    <h3 class="text-medium mb-sm">Що входить в ціну:</h3>
                    ${this.generatePriceBreakdown(result.answers)}
                </div>
                <div class="next-steps text-center">
                    <p class="text-base mb-sm">Детальний розрахунок надіслано на вашу пошту</p>
                    <button class="btn btn-primary" onclick="this.closest('.calculation-result').remove()">
                        Зрозуміло
                    </button>
                </div>
            </div>
        `;

        // Додаємо стилі для результату
        if (!document.querySelector('.result-styles')) {
            const style = document.createElement('style');
            style.className = 'result-styles';
            style.textContent = `
                .calculation-result {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    z-index: 2000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .result-content {
                    max-width: 500px;
                    width: 90%;
                    position: relative;
                    border: 2px solid var(--color-red);
                }
                .estimated-price {
                    font-size: 48px;
                    font-weight: 900;
                }
                @media (max-width: 767px) {
                    .estimated-price {
                        font-size: 36px;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(resultModal);

        // Аналітика
        this.trackCalculation(result);
    }

    generatePriceBreakdown(answers) {
        const breakdown = [];

        // Логіка на основі відповідей
        switch (answers.question_1) {
            case 'A':
                breakdown.push('✓ Розробка веб-сайту');
                breakdown.push('✓ Адаптивний дизайн');
                breakdown.push('✓ SEO оптимізація');
                break;
            case 'B':
                breakdown.push('✓ Розробка Telegram бота');
                breakdown.push('✓ Адмін панель');
                breakdown.push('✓ Інтеграції');
                break;
            case 'D':
                breakdown.push('✓ Інтернет-магазин');
                breakdown.push('✓ Система оплати');
                breakdown.push('✓ Каталог товарів');
                break;
        }

        if (answers.question_4 !== 'A') {
            breakdown.push('✓ Інтеграція платіжних систем');
        }

        if (answers.question_3 === 'A') {
            breakdown.push('⚡ Термінова розробка');
        }

        return breakdown.map(item => `<p class="text-base">${item}</p>`).join('');
    }

    showError(message) {
        if (window.prometeyApp) {
            window.prometeyApp.showError(message);
        } else {
            alert(message);
        }
    }

    clearSavedData() {
        sessionStorage.removeItem('calculator_answers');
        console.log('Calculator data cleared');
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    trackCalculation(result) {
        // Аналітика
        if (typeof gtag !== 'undefined') {
            gtag('event', 'calculator_completed', {
                'estimated_price': result.estimated_price,
                'project_type': result.answers.question_1,
                'timeline': result.answers.question_3
            });
        }

        console.log('Calculation completed:', result);
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', function () {
    console.log('Calculator page loaded');

    // Створюємо інстанс калькулятора
    window.projectCalculator = new ProjectCalculator();

    // Ініціалізація кнопки "Розпочати тест"
    const startTestBtn = document.querySelector('.start-test-btn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', showTestForm);
    }
});

// Глобальна функція для показу форми
function showTestForm() {
    const testSection = document.getElementById('test-section');
    if (testSection) {
        testSection.classList.remove('hidden');
        testSection.scrollIntoView({ behavior: 'smooth' });

        // Фокус на першому питанні
        setTimeout(() => {
            const firstQuestion = testSection.querySelector('input[type="radio"]');
            if (firstQuestion) {
                firstQuestion.closest('.question').scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        }, 500);
    }
}

// Експорт для використання в інших скриптах
window.CalculatorUtils = {
    showTestForm: showTestForm,
    getCalculatorInstance: () => window.projectCalculator
}; 