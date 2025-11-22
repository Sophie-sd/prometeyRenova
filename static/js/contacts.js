/**
 * CONTACTS.JS - Contacts page logic
 * Використовує: base.js form system
 */

document.addEventListener('DOMContentLoaded', () => {
    initMapPlaceholder();
});

function initMapPlaceholder() {
    const mapPlaceholder = document.querySelector('.map-placeholder');

    if (mapPlaceholder) {
        mapPlaceholder.addEventListener('click', () => {
            console.log('Map placeholder clicked');
        });
    }
}
