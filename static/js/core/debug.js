/**
 * DEBUG UTILITIES (2025)
 * Умовне логування для dev/prod
 */

class DebugManager {
    constructor() {
        this.enabled = this.isDevMode();
        this.levels = {
            log: true,
            warn: true,
            error: true,
            info: true
        };
    }
    
    isDevMode() {
        return window.location.hostname === 'localhost' ||
               window.location.hostname === '127.0.0.1' ||
               localStorage.getItem('prometey_debug') === 'true';
    }
    
    log(...args) {
        if (this.enabled && this.levels.log) {
            console.log('[Prometey]', ...args);
        }
    }
    
    warn(...args) {
        if (this.enabled && this.levels.warn) {
            console.warn('[Prometey]', ...args);
        }
    }
    
    error(...args) {
        if (this.levels.error) { // Завжди показувати помилки
            console.error('[Prometey]', ...args);
        }
    }
    
    info(...args) {
        if (this.enabled && this.levels.info) {
            console.info('[Prometey]', ...args);
        }
    }
    
    enable() {
        this.enabled = true;
        localStorage.setItem('prometey_debug', 'true');
        this.log('Debug mode enabled');
    }
    
    disable() {
        this.enabled = false;
        localStorage.removeItem('prometey_debug');
    }
}

// Global instance
window.Debug = new DebugManager();

// Export for modules
export default DebugManager;

