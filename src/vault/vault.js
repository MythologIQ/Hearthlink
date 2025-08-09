/**
 * Browser-compatible Vault implementation using localStorage
 * Provides persistent storage with nested key support and backup/restore functionality
 */

class Vault {
  constructor(namespace = 'hearthlink') {
    this.namespace = namespace;
    this.storageKey = `${namespace}_vault`;
    this.data = {};
    this.isLoaded = false;
  }

  /**
   * Load data from localStorage
   */
  async loadData() {
    if (this.isLoaded) return;

    try {
      const storedData = localStorage.getItem(this.storageKey);
      if (storedData) {
        this.data = JSON.parse(storedData);
      } else {
        this.data = {};
      }
    } catch (error) {
      console.warn('Failed to load vault data from localStorage:', error);
      this.data = {};
    }
    
    this.isLoaded = true;
  }

  /**
   * Save data to localStorage
   */
  async saveData() {
    try {
      const dataStr = JSON.stringify(this.data, null, 2);
      localStorage.setItem(this.storageKey, dataStr);
    } catch (error) {
      console.error('Failed to save vault data to localStorage:', error);
      throw new Error(`Vault save failed: ${error.message}`);
    }
  }

  /**
   * Store a value with the given key
   * Supports nested keys like 'user.settings.theme'
   */
  async store(key, value) {
    await this.loadData();
    
    if (key.includes('.')) {
      // Handle nested keys
      const keys = key.split('.');
      let current = this.data;
      
      // Navigate to the parent object
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
          current[keys[i]] = {};
        }
        current = current[keys[i]];
      }
      
      // Set the final value
      current[keys[keys.length - 1]] = value;
    } else {
      // Simple key
      this.data[key] = value;
    }
    
    await this.saveData();
    return true;
  }

  /**
   * Retrieve a value by key
   * Supports nested keys like 'user.settings.theme'
   */
  async retrieve(key) {
    await this.loadData();
    
    if (key.includes('.')) {
      // Handle nested keys
      const keys = key.split('.');
      let current = this.data;
      
      for (const k of keys) {
        if (current && typeof current === 'object' && k in current) {
          current = current[k];
        } else {
          return null;
        }
      }
      
      return current;
    } else {
      // Simple key
      return this.data[key] !== undefined ? this.data[key] : null;
    }
  }

  /**
   * Remove a value by key
   * Supports nested keys like 'user.settings.theme'
   */
  async remove(key) {
    await this.loadData();
    
    if (key.includes('.')) {
      // Handle nested keys
      const keys = key.split('.');
      let current = this.data;
      
      // Navigate to the parent object
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
          return false; // Key doesn't exist
        }
        current = current[keys[i]];
      }
      
      // Delete the final key
      if (keys[keys.length - 1] in current) {
        delete current[keys[keys.length - 1]];
        await this.saveData();
        return true;
      }
      return false;
    } else {
      // Simple key
      if (key in this.data) {
        delete this.data[key];
        await this.saveData();
        return true;
      }
      return false;
    }
  }

  /**
   * List all top-level keys
   */
  async list() {
    await this.loadData();
    return Object.keys(this.data);
  }

  /**
   * Check if a key exists
   */
  async exists(key) {
    const value = await this.retrieve(key);
    return value !== null;
  }

  /**
   * Clear all data
   */
  async clear() {
    this.data = {};
    await this.saveData();
    return true;
  }

  /**
   * Export all data for backup
   */
  async backup() {
    await this.loadData();
    return {
      timestamp: new Date().toISOString(),
      namespace: this.namespace,
      data: JSON.parse(JSON.stringify(this.data)) // Deep copy
    };
  }

  /**
   * Import data from backup
   */
  async restore(backupData) {
    if (!backupData || !backupData.data) {
      throw new Error('Invalid backup data');
    }
    
    this.data = JSON.parse(JSON.stringify(backupData.data)); // Deep copy
    await this.saveData();
    return true;
  }

  /**
   * Get storage statistics
   */
  async getStats() {
    await this.loadData();
    
    const dataSize = JSON.stringify(this.data).length;
    const keyCount = this.countKeys(this.data);
    
    return {
      totalKeys: keyCount,
      storageSize: dataSize,
      namespace: this.namespace,
      lastModified: new Date().toISOString()
    };
  }

  /**
   * Helper function to count nested keys
   */
  countKeys(obj) {
    let count = 0;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        count++;
        if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
          count += this.countKeys(obj[key]);
        }
      }
    }
    return count;
  }

  /**
   * Update nested object values without overwriting the entire structure
   */
  async update(key, updates) {
    const existing = await this.retrieve(key);
    
    if (existing && typeof existing === 'object' && !Array.isArray(existing)) {
      // Merge updates with existing object
      const merged = this.deepMerge(existing, updates);
      await this.store(key, merged);
      return merged;
    } else {
      // Store as new value
      await this.store(key, updates);
      return updates;
    }
  }

  /**
   * Deep merge two objects
   */
  deepMerge(target, source) {
    const result = { ...target };
    
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
          if (typeof result[key] === 'object' && result[key] !== null && !Array.isArray(result[key])) {
            result[key] = this.deepMerge(result[key], source[key]);
          } else {
            result[key] = { ...source[key] };
          }
        } else {
          result[key] = source[key];
        }
      }
    }
    
    return result;
  }
}

export { Vault };