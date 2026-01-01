/**
 * CALCULATOR.JS - Calculator logic
 * Використовує: base.js form system
 * БЕЗ inline styles - всі стилі в CSS
 */

class ProjectCalculator {
    constructor() {
        this.testForm = document.getElementById('calculator-test');
        this.totalSteps = 5;
        this.answers = {};
        this.userInfo = {};

        this.init();
    }

    init() {
        if (!this.testForm) return;

        this.setupEventListeners();
        this.addProgressIndicator();
        this.loadSavedData();
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Form submission (обробляється base.js)

        // Radio buttons
        const radios = this.testForm.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => this.handleAnswerChange(e));
        });

        // Checkboxes
        const checkboxes = this.testForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.id !== 'alt-services') {
                    this.handleAnswerChange(e);
                }
            });
        });

        // User fields
        const userFields = this.testForm.querySelectorAll('[name="name"], [name="phone"]');
        userFields.forEach(field => {
            field.addEventListener('blur', (e) => {
                this.saveUserInfo(e.target.name, e.target.value);
            });
        });

        // Start test button
        const startBtn = document.querySelector('.start-test-btn');
        startBtn?.addEventListener('click', () => this.showTestForm());

        // Alternative services checkbox
        const altServicesCheckbox = document.getElementById('alt-services');
        altServicesCheckbox?.addEventListener('change', () => this.toggleTestRequired());
    }

    // ===== PROGRESS INDICATOR =====
    addProgressIndicator() {
        // Отримуємо переклади з data-атрибутів форми
        const questionLabel = this.testForm?.dataset.questionLabel || 'Питання';
        const ofLabel = this.testForm?.dataset.ofLabel || 'з';
        
        const progressHtml = `
            <div class="calculator-progress mb-md">
                <div class="calculator-progress__bar">
                    <div class="calculator-progress__fill" data-progress="0"></div>
                </div>
                <span class="calculator-progress__text">
                    ${questionLabel} <span class="calculator-progress__current">0</span> ${ofLabel} 
                    <span class="calculator-progress__total">${this.totalSteps}</span>
                </span>
            </div>
        `;

        this.testForm.insertAdjacentHTML('afterbegin', progressHtml);
    }

    // ===== ANSWER HANDLING =====
    handleAnswerChange(event) {
        const questionName = event.target.name;
        const input = event.target;

        if (input.type === 'checkbox') {
            const group = input.closest('.calc-options');
            const checkedValues = Array.from(
                group.querySelectorAll(`input[name="${questionName}"]:checked`)
            ).map(cb => cb.value);
            this.answers[questionName] = checkedValues;
        } else {
            this.answers[questionName] = input.value;
        }

        this.updateProgress();

        // Зберігаємо в sessionStorage
        try {
            sessionStorage.setItem('calculator_answers', JSON.stringify(this.answers));
        } catch (error) {
            console.error('Failed to save answers:', error);
        }

        // Auto-advance для radio
        if (input.type === 'radio') {
            this.autoAdvanceIfNeeded(questionName);
        }
    }

    updateProgress() {
        const answered = Object.keys(this.answers).length;
        const progress = (answered / this.totalSteps) * 100;

        const progressFill = document.querySelector('.calculator-progress__fill');
        const currentSpan = document.querySelector('.calculator-progress__current');

        if (progressFill) progressFill.setAttribute('data-progress', Math.round(progress));
        if (currentSpan) currentSpan.textContent = answered;
    }

    autoAdvanceIfNeeded(questionName) {
        const currentNum = parseInt(questionName.split('_')[1]);
        
        if (currentNum < this.totalSteps) {
            setTimeout(() => {
                const nextInput = document.querySelector(`input[name="question_${currentNum + 1}"]`);
                if (nextInput) {
                    nextInput.closest('.calc-question').scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }, 500);
        } else {
            // Фокус на user data
            setTimeout(() => {
                const nameField = document.querySelector('#test-name');
                if (nameField && !nameField.value) {
                    nameField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    nameField.focus();
                }
            }, 500);
        }
    }

    // ===== DATA MANAGEMENT =====
    loadSavedData() {
        // Відповіді
        try {
            const savedAnswers = sessionStorage.getItem('calculator_answers');
            if (savedAnswers) {
                this.answers = JSON.parse(savedAnswers);
                this.restoreAnswers();
            }
        } catch (error) {
            console.error('Failed to load answers:', error);
        }

        // User data
        try {
            const savedUserData = sessionStorage.getItem('prometey_user_data');
            if (savedUserData) {
                const userData = JSON.parse(savedUserData);
                this.prefillUserData(userData);
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    restoreAnswers() {
        Object.entries(this.answers).forEach(([question, answer]) => {
            if (Array.isArray(answer)) {
                // Checkbox
                answer.forEach(val => {
                    const checkbox = this.testForm.querySelector(`input[name="${question}"][value="${val}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            } else {
                // Radio
                const radio = this.testForm.querySelector(`input[name="${question}"][value="${answer}"]`);
                if (radio) radio.checked = true;
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
            if (phoneField) {
                // Використовуємо PhoneMask для правильного форматування
                const app = window.prometeyApp;
                if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                    const mask = app.phoneMasks.get(phoneField);
                    mask.formatValue(userData.phone);
                } else {
                    // Якщо PhoneMask не ініціалізований, встановлюємо значення і спробуємо ініціалізувати
                    phoneField.value = userData.phone;
                    if (app && typeof PhoneMask !== 'undefined') {
                        // Ініціалізуємо PhoneMask для цього поля
                        app.initPhoneMasksForElement(document);
                        if (app.phoneMasks && app.phoneMasks.has(phoneField)) {
                            const mask = app.phoneMasks.get(phoneField);
                            mask.formatValue(userData.phone);
                        }
                    }
                }
            }
        } else {
            // Якщо немає збереженого телефону, переконуємось що +38 відображається
            const phoneField = document.querySelector('#test-phone');
            if (phoneField) {
                const app = window.prometeyApp;
                if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                    const mask = app.phoneMasks.get(phoneField);
                    mask.ensurePrefix();
                } else if (app && typeof PhoneMask !== 'undefined') {
                    // Ініціалізуємо PhoneMask якщо не ініціалізований
                    app.initPhoneMasksForElement(document);
                }
            }
        }
    }

    saveUserInfo(field, value) {
        this.userInfo[field] = value;

        try {
            let globalData = {};
            const saved = sessionStorage.getItem('prometey_user_data');
            if (saved) globalData = JSON.parse(saved);

            globalData[field] = value;
            globalData.timestamp = Date.now();
            sessionStorage.setItem('prometey_user_data', JSON.stringify(globalData));
        } catch (error) {
            console.error('Failed to save user info:', error);
        }
    }

    // ===== SHOW TEST FORM =====
    showTestForm() {
        const testSection = document.getElementById('test-section');
        if (!testSection) return;

        testSection.classList.remove('hidden');
        
        // Скрол до заголовка
        const header = testSection.querySelector('.calc-test__header');
        if (header) {
            header.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            testSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // ===== CLEAR DATA =====
    clearSavedData() {
        try {
            sessionStorage.removeItem('calculator_answers');
            // Також очищаємо дані користувача після відправки калькулятора
            sessionStorage.removeItem('prometey_user_data');
        } catch (error) {
            console.error('Failed to clear data:', error);
        }
    }

    // ===== CLEAR FORM AFTER SUCCESS =====
    clearForm() {
        // Очистити всі radio та checkbox
        const form = this.testForm;
        if (!form) return;

        const inputs = form.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        inputs.forEach(input => {
            input.checked = false;
            input.classList.remove('error');
        });

        // Очистити поля імені та телефону
        const nameField = form.querySelector('[name="name"]');
        const phoneField = form.querySelector('[name="phone"]');

        if (nameField) {
            nameField.value = '';
            nameField.classList.remove('error');
        }
        if (phoneField) {
            // Використовуємо PhoneMask для відновлення префіксу +38 замість простого очищення
            const app = window.prometeyApp;
            if (app && app.phoneMasks && app.phoneMasks.has(phoneField)) {
                const mask = app.phoneMasks.get(phoneField);
                mask.ensurePrefix();
            } else {
                // Якщо PhoneMask не ініціалізований, встановлюємо +38 вручну
                phoneField.value = '+38';
            }
            phoneField.classList.remove('error');
        }

        // Очистити відповіді
        this.answers = {};
        
        // Очистити sessionStorage
        this.clearSavedData();
        
        // Оновити progress indicator до 0
        const progressFill = form.querySelector('.calculator-progress__fill');
        const currentSpan = form.querySelector('.calculator-progress__current');
        
        if (progressFill) progressFill.setAttribute('data-progress', '0');
        if (currentSpan) currentSpan.textContent = '0';
        
        // Очистити помилки валідації
        const errorMessages = form.querySelectorAll('.calc-field__error');
        errorMessages.forEach(msg => {
            msg.textContent = '';
            msg.classList.remove('show');
        });
    }

    // ===== ALTERNATIVE SERVICES =====
    toggleTestRequired() {
        const altServicesCheckbox = document.getElementById('alt-services');
        const radioInputs = this.testForm.querySelectorAll('input[type="radio"]');
        
        radioInputs.forEach(input => {
            input.required = !altServicesCheckbox.checked;
        });
    }
}

// ===== INITIALIZATION =====
let calculatorInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    calculatorInstance = new ProjectCalculator();
});

// ===== GLOBAL API =====
window.CalculatorUtils = {
    showTestForm() {
        calculatorInstance?.showTestForm();
    },
    getInstance() {
        return calculatorInstance;
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectCalculator;
}
