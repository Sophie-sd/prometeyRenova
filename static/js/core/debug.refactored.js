/**
 * DEBUG.JS - Development debug utilities
 * Версія: 2.0
 */

import CONFIG from './config.js';

class DebugManager {
    constructor() {
        this.enabled = CONFIG.features.enableDebugLog;
        this.logs = [];
        this.maxLogs = 100;
    }

    log(category, message, data = null) {
        if (!this.enabled) return;

        const logEntry = {
            timestamp: Date.now(),
            category,
            message,
            data,
        };

        this.logs.push(logEntry);

        // Обмеження розміру
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        // Console output
        const style = this.getCategoryStyle(category);
        console.log(
            `%c[${category}] ${message}`,
            style,
            data || ''
        );
    }

    getCategoryStyle(category) {
        const styles = {
            'MobileCore': 'color: #2196F3; font-weight: bold;',
            'VideoSystem': 'color: #4CAF50; font-weight: bold;',
            'PrometeyApp': 'color: #FF9800; font-weight: bold;',
            'Portfolio': 'color: #9C27B0; font-weight: bold;',
            'Calculator': 'color: #F44336; font-weight: bold;',
            'Events': 'color: #00BCD4; font-weight: bold;',
            'Blog': 'color: #795548; font-weight: bold;',
            'Analytics': 'color: #607D8B; font-weight: bold;',
            'Error': 'color: #F44336; font-weight: bold; background: #FFEBEE;',
        };

        return styles[category] || 'color: #666;';
    }

    error(category, message, error = null) {
        console.error(`[${category}] ${message}`, error || '');
        
        this.log('Error', `${category}: ${message}`, error);
    }

    warn(category, message, data = null) {
        console.warn(`[${category}] ${message}`, data || '');
    }

    table(data, label = '') {
        if (!this.enabled) return;
        
        if (label) console.log(`[DEBUG] ${label}`);
        console.table(data);
    }

    getLogs(category = null) {
        if (category) {
            return this.logs.filter(log => log.category === category);
        }
        return this.logs;
    }

    clearLogs() {
        this.logs = [];
    }

    exportLogs() {
        return JSON.stringify(this.logs, null, 2);
    }

    // Performance markers
    mark(name) {
        if (window.performance && window.performance.mark) {
            performance.mark(name);
        }
    }

    measure(name, startMark, endMark) {
        if (window.performance && window.performance.measure) {
            try {
                performance.measure(name, startMark, endMark);
                const measure = performance.getEntriesByName(name)[0];
                this.log('Performance', `${name}: ${measure.duration.toFixed(2)}ms`);
            } catch (e) {
                // Ignore
            }
        }
    }
}

// ===== GLOBAL =====
const debug = new DebugManager();
window.Debug = debug;

export default debug;

