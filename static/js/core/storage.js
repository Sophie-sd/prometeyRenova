/**
 * STORAGE.JS - Централізований SessionStorage wrapper
 * Безпечна робота з storage + type safety
 * Версія: 2.0
 */

import CONFIG from './config.js';

/**
 * Storage Manager
 */
class StorageManager {
    constructor(storage = sessionStorage) {
        this.storage = storage;
        this.isAvailable = this.checkAvailability();
    }

    /**
     * Перевірка доступності storage
     */
    checkAvailability() {
        try {
            const testKey = '__storage_test__';
            this.storage.setItem(testKey, 'test');
            this.storage.removeItem(testKey);
            return true;
        } catch (error) {
            console.warn('Storage not available:', error);
            return false;
        }
    }

    /**
     * Set item (з автоматичним JSON.stringify)
     */
    set(key, value, options = {}) {
        if (!this.isAvailable) return false;

        try {
            const data = {
                value,
                timestamp: Date.now(),
                ...options,
            };
            
            this.storage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Storage set error:', error);
            return false;
        }
    }

    /**
     * Get item (з автоматичним JSON.parse)
     */
    get(key, defaultValue = null) {
        if (!this.isAvailable) return defaultValue;

        try {
            const item = this.storage.getItem(key);
            if (!item) return defaultValue;

            const data = JSON.parse(item);
            
            // Перевірка TTL якщо встановлено
            if (data.ttl && Date.now() - data.timestamp > data.ttl) {
                this.remove(key);
                return defaultValue;
            }

            return data.value;
        } catch (error) {
            console.error('Storage get error:', error);
            return defaultValue;
        }
    }

    /**
     * Remove item
     */
    remove(key) {
        if (!this.isAvailable) return false;

        try {
            this.storage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage remove error:', error);
            return false;
        }
    }

    /**
     * Clear all
     */
    clear() {
        if (!this.isAvailable) return false;

        try {
            this.storage.clear();
            return true;
        } catch (error) {
            console.error('Storage clear error:', error);
            return false;
        }
    }

    /**
     * Get all keys
     */
    keys() {
        if (!this.isAvailable) return [];

        try {
            return Object.keys(this.storage);
        } catch (error) {
            console.error('Storage keys error:', error);
            return [];
        }
    }

    /**
     * Check if key exists
     */
    has(key) {
        return this.get(key) !== null;
    }
}

// ===== SPECIALIZED STORAGE MANAGERS =====

/**
 * User Data Manager
 */
class UserDataManager {
    constructor(storage) {
        this.storage = storage;
        this.key = CONFIG.storage.userData;
    }

    get() {
        return this.storage.get(this.key, {});
    }

    set(userData) {
        const currentData = this.get();
        const mergedData = {
            ...currentData,
            ...userData,
            timestamp: Date.now(),
        };
        return this.storage.set(this.key, mergedData);
    }

    update(field, value) {
        const data = this.get();
        data[field] = value;
        data.timestamp = Date.now();
        return this.storage.set(this.key, data);
    }

    clear() {
        return this.storage.remove(this.key);
    }

    getName() {
        return this.get().name || '';
    }

    getPhone() {
        return this.get().phone || '';
    }

    getEmail() {
        return this.get().email || '';
    }
}

/**
 * Calculator Data Manager
 */
class CalculatorDataManager {
    constructor(storage) {
        this.storage = storage;
        this.key = CONFIG.storage.calculatorAnswers;
    }

    get() {
        return this.storage.get(this.key, {});
    }

    set(answers) {
        return this.storage.set(this.key, answers);
    }

    setAnswer(question, answer) {
        const answers = this.get();
        answers[question] = answer;
        return this.set(answers);
    }

    getAnswer(question) {
        return this.get()[question] || null;
    }

    clear() {
        return this.storage.remove(this.key);
    }

    getProgress() {
        const answers = this.get();
        return Object.keys(answers).length;
    }

    isComplete(totalQuestions) {
        return this.getProgress() >= totalQuestions;
    }
}

// ===== GLOBAL INSTANCES =====
const storage = new StorageManager(sessionStorage);
const localStorage = new StorageManager(window.localStorage);

const userData = new UserDataManager(storage);
const calculatorData = new CalculatorDataManager(storage);

// ===== GLOBAL EXPORT (HYBRID) =====
window.Storage = {
    session: storage,
    local: localStorage,
    userData,
    calculatorData,
};

window.UserData = userData;
window.CalculatorData = calculatorData;

// ES Module export
export {
    storage,
    localStorage as localStore,
    userData,
    calculatorData,
    StorageManager,
};

export default storage;

