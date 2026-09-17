/* Countdown timers: compact pill — one textContent update per tick */

function pad(n) {
    return String(n).padStart(2, '0');
}

function formatRemaining(remaining, dayLabel) {
    const days = Math.floor(remaining / 86400);
    const hh = pad(Math.floor((remaining % 86400) / 3600));
    const mm = pad(Math.floor((remaining % 3600) / 60));
    const ss = pad(remaining % 60);
    return days > 0 ? `${days}${dayLabel} ${hh}:${mm}:${ss}` : `${hh}:${mm}:${ss}`;
}

function tickTimers(root) {
    const now = Math.floor(Date.now() / 1000);
    (root || document).querySelectorAll('[data-countdown]').forEach((el) => {
        const end = parseInt(el.getAttribute('data-countdown'), 10);
        if (!end) return;
        const remaining = end - now;
        if (remaining <= 0) {
            el.textContent = el.getAttribute('data-expired-label') || 'Акція завершена';
            el.removeAttribute('data-countdown');
            return;
        }
        const dayLabel = el.getAttribute('data-label-days') || 'д';
        const next = formatRemaining(remaining, dayLabel);
        if (el.textContent !== next) el.textContent = next;
    });
}

function initTimers(root) {
    tickTimers(root || document);
}

let timerInterval = null;
function startTimerLoop() {
    if (timerInterval) return;
    timerInterval = window.setInterval(() => tickTimers(document), 1000);
}

window.dsInitTimers = initTimers;
window.dsStartTimerLoop = startTimerLoop;

document.addEventListener('DOMContentLoaded', () => {
    initTimers(document);
    startTimerLoop();
});
