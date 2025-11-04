/**
 * FORMS.JS - Централізовані form utilities
 * Версія: 2.0
 */

import CONFIG from '../core/config.js';
import { userData } from '../core/storage.js';

/**
 * Form Validator
 */
export class FormValidator {
    static validate(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            const value = field.value.trim();
            const isEmpty = !value;

            field.classList.toggle('error', isEmpty);
            field.setAttribute('aria-invalid', isEmpty ? 'true' : 'false');

            if (isEmpty) isValid = false;
        });

        return isValid;
    }

    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validatePhone(phone) {
        const re = /^\+?[\d\s\-()]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    static clearErrors(form) {
        form.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
            field.setAttribute('aria-invalid', 'false');
        });
    }
}

/**
 * Form Prefiller
 */
export class FormPrefiller {
    static prefill(form) {
        const user = userData.get();
        if (!user || Object.keys(user).length === 0) return;

        const nameField = form.querySelector('input[name="name"]');
        const phoneField = form.querySelector('input[name="phone"]');
        const emailField = form.querySelector('input[name="email"]');

        if (nameField && user.name && !nameField.value) {
            nameField.value = user.name;
        }

        if (phoneField && user.phone && !phoneField.value) {
            phoneField.value = user.phone;
        }

        if (emailField && user.email && !emailField.value) {
            emailField.value = user.email;
        }
    }

    static saveFromForm(form) {
        const formData = new FormData(form);

        if (formData.get('name')) {
            userData.update('name', formData.get('name'));
        }

        if (formData.get('phone')) {
            userData.update('phone', formData.get('phone'));
        }

        if (formData.get('email')) {
            userData.update('email', formData.get('email'));
        }
    }
}

/**
 * Form Submitter
 */
export class FormSubmitter {
    static async submit(form, csrfToken) {
        const formData = new FormData(form);
        const formType = form.getAttribute('data-form-type');

        const url = formType === CONFIG.formTypes.test
            ? CONFIG.endpoints.formTest
            : CONFIG.endpoints.formSubmit;

        if (formType !== CONFIG.formTypes.test) {
            formData.append('form_type', formType);
        }

        return fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    }
}

// Export all
export default {
    FormValidator,
    FormPrefiller,
    FormSubmitter,
};

