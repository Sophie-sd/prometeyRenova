/**
 * PHONE-MASK.JS - Маска введення телефону для українських номерів
 * Формат: +38(___)__-__-___
 * Префікс +38 не можна видалити
 * Номер має починатися з 0 після +38
 */

class PhoneMask {
    constructor(input) {
        this.input = input;
        this.prefix = '+38';
        this.pattern = /^\+380\d{9}$/;
        
        this.init();
    }

    init() {
        // Додаємо +38 якщо поле порожнє при фокусі
        this.input.addEventListener('focus', () => this.handleFocus());
        
        // Обробка введення
        this.input.addEventListener('input', (e) => this.handleInput(e));
        
        // Заборона видалення +38
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Обробка вставки (paste)
        this.input.addEventListener('paste', (e) => this.handlePaste(e));
        
        // Форматування при втраті фокусу
        this.input.addEventListener('blur', () => this.formatOnBlur());
        
        // Ініціалізація якщо вже є значення
        if (this.input.value) {
            this.formatValue(this.input.value);
        }
    }

    handleFocus() {
        if (!this.input.value || this.input.value.trim() === '') {
            this.input.value = this.prefix;
            // Встановлюємо курсор після +38
            this.setCursorPosition(this.prefix.length);
        }
    }

    handleInput(e) {
        let value = this.input.value;
        
        // Видаляємо все крім цифр та +
        let cleaned = value.replace(/[^\d+]/g, '');
        
        // Переконуємося що починається з +38
        if (!cleaned.startsWith('+38')) {
            if (cleaned.startsWith('38')) {
                cleaned = '+' + cleaned;
            } else if (cleaned.startsWith('8')) {
                cleaned = '+38' + cleaned.substring(1);
            } else if (cleaned.match(/^\d/)) {
                cleaned = '+38' + cleaned;
            } else {
                cleaned = '+38' + cleaned.replace(/[^\d]/g, '');
            }
        }
        
        // Обмежуємо довжину (максимум 12 цифр після +38)
        const digits = cleaned.replace(/\D/g, '');
        if (digits.length > 12) {
            cleaned = '+38' + digits.substring(0, 12);
        }
        
        // Форматуємо значення
        this.formatValue(cleaned);
    }

    handleKeyDown(e) {
        const cursorPos = this.input.selectionStart;
        const value = this.input.value;
        
        // Заборона видалення +38
        if (e.key === 'Backspace' || e.key === 'Delete') {
            // Якщо курсор в межах +38, блокуємо видалення
            if (cursorPos <= this.prefix.length) {
                e.preventDefault();
                return;
            }
        }
        
        // Заборона вставки курсору перед +38
        if (e.key === 'ArrowLeft' && cursorPos <= this.prefix.length) {
            e.preventDefault();
            this.setCursorPosition(this.prefix.length);
        }
    }

    handlePaste(e) {
        e.preventDefault();
        
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        
        // Очищаємо вставлений текст
        let cleaned = pastedText.replace(/[^\d+]/g, '');
        
        // Додаємо +38 якщо немає
        if (!cleaned.startsWith('+38')) {
            if (cleaned.startsWith('38')) {
                cleaned = '+' + cleaned;
            } else if (cleaned.startsWith('8')) {
                cleaned = '+38' + cleaned.substring(1);
            } else if (cleaned.match(/^\d/)) {
                cleaned = '+38' + cleaned;
            } else {
                cleaned = '+38' + cleaned.replace(/[^\d]/g, '');
            }
        }
        
        // Обмежуємо довжину
        const digits = cleaned.replace(/\D/g, '');
        if (digits.length > 12) {
            cleaned = '+38' + digits.substring(0, 12);
        }
        
        this.formatValue(cleaned);
    }

    formatValue(value) {
        // Видаляємо все крім цифр та +
        let digits = value.replace(/[^\d]/g, '');
        
        // Переконуємося що є +38
        if (!digits.startsWith('38')) {
            if (digits.startsWith('8')) {
                digits = '38' + digits.substring(1);
            } else {
                digits = '38' + digits;
            }
        }
        
        // Обмежуємо до 12 цифр (38 + 10 цифр номера)
        if (digits.length > 12) {
            digits = digits.substring(0, 12);
        }
        
        // Форматуємо: +38(XXX)XX-XX-XXX
        if (digits.length <= 2) {
            this.input.value = '+' + digits;
        } else if (digits.length <= 5) {
            this.input.value = '+' + digits.substring(0, 2) + '(' + digits.substring(2);
        } else if (digits.length <= 7) {
            this.input.value = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5);
        } else if (digits.length <= 9) {
            this.input.value = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7);
        } else if (digits.length <= 11) {
            this.input.value = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7, 9) + '-' + digits.substring(9);
        } else {
            this.input.value = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7, 9) + '-' + digits.substring(9, 11);
        }
    }

    formatOnBlur() {
        const value = this.input.value;
        if (value && value.trim() !== '' && value !== this.prefix) {
            this.formatValue(value);
        }
    }

    setCursorPosition(position) {
        // Використовуємо setTimeout для коректної встановки позиції
        setTimeout(() => {
            this.input.setSelectionRange(position, position);
        }, 0);
    }

    /**
     * Валідація номера телефону
     * @returns {Object} {valid: boolean, message: string}
     */
    validate() {
        const value = this.input.value;
        
        if (!value || value.trim() === '' || value === this.prefix) {
            return {
                valid: false,
                message: 'Введіть номер телефону'
            };
        }
        
        // Очищаємо значення для перевірки
        const cleaned = value.replace(/[^\d+]/g, '');
        
        // Перевірка формату +380XXXXXXXXX
        if (!cleaned.startsWith('+380')) {
            return {
                valid: false,
                message: 'Номер має починатися з 0'
            };
        }
        
        // Перевірка довжини (має бути +380 + 9 цифр = 13 символів)
        if (cleaned.length !== 13) {
            return {
                valid: false,
                message: 'Введіть коректний номер телефону'
            };
        }
        
        // Перевірка що після +380 є тільки цифри
        if (!/^\+380\d{9}$/.test(cleaned)) {
            return {
                valid: false,
                message: 'Введіть коректний номер телефону'
            };
        }
        
        return {
            valid: true,
            message: '',
            cleaned: cleaned
        };
    }

    /**
     * Отримати очищене значення для відправки
     * @returns {string}
     */
    getCleanedValue() {
        const value = this.input.value;
        return value.replace(/[^\d+]/g, '');
    }
}

// Експорт для використання в інших модулях
if (typeof window !== 'undefined') {
    window.PhoneMask = PhoneMask;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhoneMask;
}

