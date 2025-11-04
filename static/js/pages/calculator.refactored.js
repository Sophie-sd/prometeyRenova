/**
 * CALCULATOR.JS - Refactored v2.0
 * Використовує централізований storage
 */

import CONFIG from '../core/config.js';
import { calculatorData, userData } from '../core/storage.js';
import analytics from '../core/analytics.js';

class ProjectCalculator {
    constructor() {
        this.testForm = document.getElementById('calculator-test');
        this.totalSteps = 5;

        this.init();
    }

    init() {
        if (!this.testForm) return;

        this.setupEventListeners();
        this.addProgressIndicator();
        this.loadSavedData();

        console.log('[Calculator] Initialized');
    }

    setupEventListeners() {
        // Radio buttons
        this.testForm.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleAnswerChange(e));
        });

        // User fields (автоматичне збереження)
        this.testForm.querySelectorAll('.user-data input').forEach(field => {
            field.addEventListener('blur', (e) => {
                userData.update(e.target.name, e.target.value);
            });
        });

        // Start test button
        document.querySelector('.start-test-btn')?.addEventListener('click', () => {
            this.showTestForm();
        });
    }

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

    handleAnswerChange(event) {
        const questionName = event.target.name;
        const answer = event.target.value;

        // Зберігання через централізований storage
        calculatorData.setAnswer(questionName, answer);

        // Update UI
        this.updateProgress();

        // Auto-advance
        this.autoAdvanceIfNeeded(questionName);

        // Analytics
        analytics.trackCustom('calculator_answer', {
            question: questionName,
            answer: answer,
        });
    }

    updateProgress() {
        const progress = calculatorData.getProgress();
        const percentage = (progress / this.totalSteps) * 100;

        const progressFill = document.querySelector('.calculator-progress__fill');
        const currentSpan = document.querySelector('.calculator-progress__current');

        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
            progressFill.setAttribute('data-progress', Math.round(percentage));
        }
        if (currentSpan) currentSpan.textContent = progress;
    }

    autoAdvanceIfNeeded(questionName) {
        const currentNum = parseInt(questionName.split('_')[1]);

        if (currentNum < this.totalSteps) {
            setTimeout(() => {
                const nextInput = document.querySelector(`input[name="question_${currentNum + 1}"]`);
                if (nextInput) {
                    nextInput.closest('.calc-question').scrollIntoView({
                        behavior: CONFIG.animation.scrollBehavior,
                        block: 'center'
                    });
                }
            }, CONFIG.timing.autoAdvanceDelay);
        } else {
            // Всі питання відповіли - фокус на user data
            setTimeout(() => {
                const nameField = document.querySelector('#test-name');
                if (nameField && !nameField.value) {
                    nameField.scrollIntoView({ 
                        behavior: CONFIG.animation.scrollBehavior, 
                        block: 'center' 
                    });
                    nameField.focus();
                }
            }, CONFIG.timing.autoAdvanceDelay);
        }
    }

    loadSavedData() {
        // Відповіді (через централізований storage)
        const answers = calculatorData.get();
        if (Object.keys(answers).length > 0) {
            this.restoreAnswers(answers);
        }

        // User data
        const user = userData.get();
        if (user.name || user.phone) {
            this.prefillUserData(user);
        }
    }

    restoreAnswers(answers) {
        Object.entries(answers).forEach(([question, answer]) => {
            const radio = this.testForm.querySelector(`input[name="${question}"][value="${answer}"]`);
            if (radio) radio.checked = true;
        });
        this.updateProgress();
    }

    prefillUserData(user) {
        if (user.name) {
            const nameField = document.querySelector('#test-name');
            if (nameField) nameField.value = user.name;
        }

        if (user.phone) {
            const phoneField = document.querySelector('#test-phone');
            if (phoneField) phoneField.value = user.phone;
        }
    }

    showTestForm() {
        const testSection = document.getElementById('test-section');
        if (!testSection) return;

        testSection.classList.remove('hidden');
        testSection.scrollIntoView({ behavior: CONFIG.animation.scrollBehavior });

        setTimeout(() => {
            const firstQuestion = testSection.querySelector('input[type="radio"]');
            firstQuestion?.closest('.calc-question').scrollIntoView({
                behavior: CONFIG.animation.scrollBehavior,
                block: 'center'
            });
        }, CONFIG.timing.autoAdvanceDelay);

        // Analytics
        analytics.trackCustom('calculator_test_started');
    }

    clearSavedData() {
        calculatorData.clear();
    }
}

// ===== AUTO INIT =====
let calculatorInstance = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        calculatorInstance = new ProjectCalculator();
    });
} else {
    calculatorInstance = new ProjectCalculator();
}

// ===== GLOBAL API =====
window.CalculatorUtils = {
    showTestForm() {
        calculatorInstance?.showTestForm();
    },
    getInstance() {
        return calculatorInstance;
    },
    clearData() {
        calculatorInstance?.clearSavedData();
    }
};

