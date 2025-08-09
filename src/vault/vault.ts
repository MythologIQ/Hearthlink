export {}
import * as fs from 'fs/promises'
import * as path from 'path'

interface VaultData {
  [key: string]: any
}

export class Vault {
  private vaultPath: string
  private data: VaultData = {}
  private isLoaded = false

  constructor(vaultPath?: string) {
    // Use userData directory or default to ./vault
    this.vaultPath = vaultPath || path.join(process.cwd(), 'userData', 'vault.json')
  }

  private async ensureVaultDir(): Promise<void> {
    const dir = path.dirname(this.vaultPath)
    try {
      await fs.mkdir(dir, { recursive: true })
    } catch (error) {
      // Directory might already exist
    }
  }

  private async loadData(): Promise<void> {
    if (this.isLoaded) return

    await this.ensureVaultDir()
    
    try {
      const data = await fs.readFile(this.vaultPath, 'utf-8')
      this.data = JSON.parse(data.toString())
    } catch (error) {
      // File doesn't exist yet, start with empty data
      this.data = {}
    }
    
    this.isLoaded = true
  }

  private async saveData(): Promise<void> {
    await this.ensureVaultDir()
    
    try {
      const dataStr = JSON.stringify(this.data, null, 2)
      await fs.writeFile(this.vaultPath, dataStr, 'utf-8')
    } catch (error) {
      console.error('Failed to save vault data:', error)
      throw new Error(`Vault save failed: ${error.message}`)
    }
  }
  
  async store(key: string, value: any): Promise<void> {
    await this.loadData()
    
    // Support nested keys like 'user.preferences.theme'
    const keys = key.split('.')
    let current = this.data
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i]
      if (!(k in current) || typeof current[k] !== 'object') {
        current[k] = {}
      }
      current = current[k]
    }
    
    current[keys[keys.length - 1]] = value
    await this.saveData()
  }
  
  async retrieve(key: string): Promise<any> {
    await this.loadData()
    
    // Support nested keys
    const keys = key.split('.')
    let current = this.data
    
    for (const k of keys) {
      if (current && typeof current === 'object' && k in current) {
        current = current[k]
      } else {
        return null
      }
    }
    
    return current
  }

  async delete(key: string): Promise<boolean> {
    await this.loadData()
    
    const keys = key.split('.')
    let current = this.data
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i]
      if (!(k in current) || typeof current[k] !== 'object') {
        return false // Key doesn't exist
      }
      current = current[k]
    }
    
    const finalKey = keys[keys.length - 1]
    if (finalKey in current) {
      delete current[finalKey]
      await this.saveData()
      return true
    }
    
    return false
  }

  async exists(key: string): Promise<boolean> {
    const value = await this.retrieve(key)
    return value !== null
  }

  async list(prefix?: string): Promise<string[]> {
    await this.loadData()
    
    const keys: string[] = []
    
    const traverse = (obj: any, currentPath: string[] = []) => {
      for (const [key, value] of Object.entries(obj)) {
        const fullPath = [...currentPath, key].join('.')
        
        if (!prefix || fullPath.startsWith(prefix)) {
          keys.push(fullPath)
        }
        
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          traverse(value, [...currentPath, key])
        }
      }
    }
    
    traverse(this.data)
    return keys.sort()
  }

  async clear(): Promise<void> {
    this.data = {}
    await this.saveData()
  }

  async backup(backupPath?: string): Promise<string> {
    await this.loadData()
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const defaultBackupPath = path.join(
      path.dirname(this.vaultPath),
      `vault-backup-${timestamp}.json`
    )
    
    const finalBackupPath = backupPath || defaultBackupPath
    
    await fs.writeFile(finalBackupPath, JSON.stringify(this.data, null, 2), 'utf-8')
    return finalBackupPath
  }

  async restore(backupPath: string): Promise<void> {
    try {
      const backupData = await fs.readFile(backupPath, 'utf-8')
      this.data = JSON.parse(backupData.toString())
      await this.saveData()
      console.log(`Vault restored from: ${backupPath}`)
    } catch (error) {
      throw new Error(`Failed to restore vault from ${backupPath}: ${error.message}`)
    }
  }
}