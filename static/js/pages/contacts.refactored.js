/**
 * CONTACTS.JS - Refactored v2.0
 * Мінімальна логіка, форма обробляється app-core.js
 */

import analytics from '../core/analytics.js';

class ContactsPage {
    constructor() {
        this.init();
    }

    init() {
        this.initMapPlaceholder();
        this.prefillFromURL();
        this.setActiveMenuLink();
    }

    initMapPlaceholder() {
        const mapPlaceholder = document.querySelector('.map-placeholder');

        if (mapPlaceholder) {
            mapPlaceholder.addEventListener('click', () => {
                // TODO: Інтеграція Google Maps
                analytics.trackCustom('map_click');
            });
        }
    }

    prefillFromURL() {
        // Prefill форми з URL параметрів (з portfolio)
        const urlParams = new URLSearchParams(window.location.search);
        const projectType = urlParams.get('project');
        const projectName = urlParams.get('name');

        if (projectType && projectName) {
            const messageField = document.querySelector('#message');
            if (messageField && !messageField.value) {
                messageField.value = `Хочу замовити проект подібний до: ${projectName}`;
            }

            // Analytics
            analytics.trackCustom('contact_from_portfolio', {
                project_type: projectType,
                project_name: projectName,
            });
        }
    }

    setActiveMenuLink() {
        const contactsLink = document.querySelector('.nav-link[href*="contacts"]');
        contactsLink?.classList.add('active');
    }
}

// ===== AUTO INIT =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ContactsPage());
} else {
    new ContactsPage();
}

