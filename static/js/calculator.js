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
        const userFields = this.testForm.querySelectorAll('[name="name"], [name="phone"], [name="email"]');
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
        const progressHtml = `
            <div class="calculator-progress mb-md">
                <div class="calculator-progress__bar">
                    <div class="calculator-progress__fill" data-progress="0"></div>
                </div>
                <span class="calculator-progress__text">
                    Питання <span class="calculator-progress__current">0</span> з 
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
            if (phoneField) phoneField.value = userData.phone;
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
        testSection.scrollIntoView({ behavior: 'smooth' });

        setTimeout(() => {
            const firstQuestion = testSection.querySelector('input[type="radio"]');
            firstQuestion?.closest('.calc-question').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }, 500);
    }

    // ===== CLEAR DATA =====
    clearSavedData() {
        try {
            sessionStorage.removeItem('calculator_answers');
        } catch (error) {
            console.error('Failed to clear data:', error);
        }
    }

    // ===== VALIDATION =====
    validateName(name) {
        if (!name || name.trim().length < 2) return false;
        if (/^\d+$/.test(name)) return false;
        if (!/[a-z]/i.test(name)) return false;
        return true;
    }

    validatePhone(phone) {
        const clean = phone.replace(/[^\d+]/g, '');
        const digitCount = clean.replace(/\D/g, '').length;
        return digitCount >= 10 && clean.length <= 20;
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
