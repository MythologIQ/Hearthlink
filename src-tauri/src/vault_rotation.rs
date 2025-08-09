use aes_gcm::{Aes256Gcm, Key, Nonce, KeyInit};
use aes_gcm::aead::{Aead, OsRng};
use base64::{Engine as _, engine::general_purpose};
use chrono::{DateTime, Utc, Duration};
use prometheus::{Counter, Gauge, Histogram, register_counter, register_gauge, register_histogram};
use rand::RngCore;
use rusqlite::{Connection, params};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tauri::State;
use tokio::time::{sleep, Duration as TokioDuration};

// Prometheus metrics
lazy_static::lazy_static! {
    static ref KEY_ROTATION_COUNTER: Counter = register_counter!(
        "vault_key_rotation_total", 
        "Total key rotations performed"
    ).unwrap();
    
    static ref KEY_ROTATION_TIMESTAMP: Gauge = register_gauge!(
        "vault_key_rotation_timestamp", 
        "Timestamp of last key rotation"
    ).unwrap();
    
    static ref KEY_VERSION_COUNT: Gauge = register_gauge!(
        "vault_key_version_count", 
        "Number of key versions stored"
    ).unwrap();
    
    static ref KEY_ROTATION_DURATION: Histogram = register_histogram!(
        "vault_key_rotation_duration_seconds", 
        "Time taken for key rotation"
    ).unwrap();
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeyVersion {
    pub version: i64,
    pub key_data: Vec<u8>,
    pub created_at: DateTime<Utc>,
    pub rotated_at: Option<DateTime<Utc>>,
    pub is_active: bool,
    pub metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RotationPolicy {
    pub rotation_interval_days: i64,
    pub max_key_versions: i64,
    pub auto_rotation_enabled: bool,
    pub performance_threshold_seconds: f64,
    pub backup_old_keys: bool,
}

impl Default for RotationPolicy {
    fn default() -> Self {
        Self {
            rotation_interval_days: 30,
            max_key_versions: 3,
            auto_rotation_enabled: true,
            performance_threshold_seconds: 5.0,
            backup_old_keys: true,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RotationResult {
    pub success: bool,
    pub old_version: Option<i64>,
    pub new_version: Option<i64>,
    pub duration_seconds: f64,
    pub trigger_type: String,
    pub reason: Option<String>,
}

#[derive(Debug)]
pub struct VaultKeyRotationManager {
    db_path: PathBuf,
    policy: RotationPolicy,
    current_key: Arc<Mutex<Option<KeyVersion>>>,
}

impl VaultKeyRotationManager {
    pub fn new(db_path: PathBuf, policy: Option<RotationPolicy>) -> Result<Self, Box<dyn std::error::Error>> {
        let policy = policy.unwrap_or_default();
        let manager = Self {
            db_path: db_path.clone(),
            policy,
            current_key: Arc::new(Mutex::new(None)),
        };
        
        manager.init_database()?;
        manager.load_current_key()?;
        
        Ok(manager)
    }

    fn init_database(&self) -> Result<(), Box<dyn std::error::Error>> {
        let conn = Connection::open(&self.db_path)?;
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS key_versions (
                version INTEGER PRIMARY KEY,
                key_data BLOB NOT NULL,
                created_at TEXT NOT NULL,
                rotated_at TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                metadata TEXT
            )",
            [],
        )?;
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS rotation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                old_version INTEGER,
                new_version INTEGER,
                trigger_type TEXT NOT NULL,
                duration_seconds REAL,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )",
            [],
        )?;
        
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_key_versions_active 
             ON key_versions(is_active, version DESC)",
            [],
        )?;
        
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_rotation_log_timestamp 
             ON rotation_log(timestamp DESC)",
            [],
        )?;
        
        Ok(())
    }

    fn load_current_key(&self) -> Result<(), Box<dyn std::error::Error>> {
        let conn = Connection::open(&self.db_path)?;
        
        let mut stmt = conn.prepare(
            "SELECT version, key_data, created_at, rotated_at, metadata
             FROM key_versions 
             WHERE is_active = 1 
             ORDER BY version DESC 
             LIMIT 1"
        )?;
        
        let mut rows = stmt.query_map([], |row| {
            let metadata_str: Option<String> = row.get(4)?;
            let metadata = metadata_str
                .map(|s| serde_json::from_str(&s).unwrap_or_default())
                .unwrap_or_default();
            
            Ok(KeyVersion {
                version: row.get(0)?,
                key_data: row.get(1)?,
                created_at: DateTime::parse_from_rfc3339(&row.get::<_, String>(2)?)?.with_timezone(&Utc),
                rotated_at: row.get::<_, Option<String>>(3)?
                    .map(|s| DateTime::parse_from_rfc3339(&s).unwrap().with_timezone(&Utc)),
                is_active: true,
                metadata,
            })
        })?;
        
        if let Some(row_result) = rows.next() {
            let key_version = row_result?;
            *self.current_key.lock().unwrap() = Some(key_version.clone());
            println!("Loaded active key version {}", key_version.version);
        } else {
            // Generate initial key
            self.generate_initial_key()?;
        }
        
        Ok(())
    }

    fn generate_initial_key(&self) -> Result<(), Box<dyn std::error::Error>> {
        let mut key_data = vec![0u8; 32];
        OsRng.fill_bytes(&mut key_data);
        
        let now = Utc::now();
        let mut metadata = HashMap::new();
        metadata.insert("generation_method".to_string(), "initial".to_string());
        metadata.insert("bit_length".to_string(), "256".to_string());
        
        let key_version = KeyVersion {
            version: 1,
            key_data: key_data.clone(),
            created_at: now,
            rotated_at: None,
            is_active: true,
            metadata,
        };
        
        let conn = Connection::open(&self.db_path)?;
        conn.execute(
            "INSERT INTO key_versions (version, key_data, created_at, metadata)
             VALUES (?1, ?2, ?3, ?4)",
            params![
                key_version.version,
                key_version.key_data,
                key_version.created_at.to_rfc3339(),
                serde_json::to_string(&key_version.metadata)?
            ],
        )?;
        
        *self.current_key.lock().unwrap() = Some(key_version);
        KEY_VERSION_COUNT.set(1.0);
        
        println!("Generated initial master key version 1");
        Ok(())
    }

    pub fn get_current_key(&self) -> Result<KeyVersion, Box<dyn std::error::Error>> {
        let key_lock = self.current_key.lock().unwrap();
        key_lock.clone().ok_or_else(|| "No active key found".into())
    }

    pub fn get_key_by_version(&self, version: i64) -> Result<Option<KeyVersion>, Box<dyn std::error::Error>> {
        let conn = Connection::open(&self.db_path)?;
        
        let mut stmt = conn.prepare(
            "SELECT key_data, created_at, rotated_at, is_active, metadata
             FROM key_versions 
             WHERE version = ?1"
        )?;
        
        let mut rows = stmt.query_map([version], |row| {
            let metadata_str: Option<String> = row.get(4)?;
            let metadata = metadata_str
                .map(|s| serde_json::from_str(&s).unwrap_or_default())
                .unwrap_or_default();
            
            Ok(KeyVersion {
                version,
                key_data: row.get(0)?,
                created_at: DateTime::parse_from_rfc3339(&row.get::<_, String>(1)?)?.with_timezone(&Utc),
                rotated_at: row.get::<_, Option<String>>(2)?
                    .map(|s| DateTime::parse_from_rfc3339(&s).unwrap().with_timezone(&Utc)),
                is_active: row.get(3)?,
                metadata,
            })
        })?;
        
        if let Some(row_result) = rows.next() {
            Ok(Some(row_result?))
        } else {
            Ok(None)
        }
    }

    pub fn should_rotate(&self) -> Result<(bool, String), Box<dyn std::error::Error>> {
        if !self.policy.auto_rotation_enabled {
            return Ok((false, "Auto-rotation disabled".to_string()));
        }
        
        let current_key = self.get_current_key()?;
        let rotation_due = current_key.created_at + Duration::days(self.policy.rotation_interval_days);
        
        if Utc::now() >= rotation_due {
            Ok((true, format!("Key rotation due (created {} days ago)", self.policy.rotation_interval_days)))
        } else {
            Ok((false, format!("Key rotation not due until {}", rotation_due.to_rfc3339())))
        }
    }

    pub async fn rotate_key(&self, trigger_type: &str, force: bool) -> Result<RotationResult, Box<dyn std::error::Error>> {
        let start_time = std::time::Instant::now();
        let old_version = self.get_current_key().map(|k| k.version).unwrap_or(0);
        
        // Check if rotation is needed
        let (should_rotate, reason) = self.should_rotate()?;
        if !should_rotate && !force {
            return Ok(RotationResult {
                success: false,
                old_version: Some(old_version),
                new_version: None,
                duration_seconds: 0.0,
                trigger_type: trigger_type.to_string(),
                reason: Some(reason),
            });
        }
        
        let _timer = KEY_ROTATION_DURATION.start_timer();
        
        // Generate new key
        let mut new_key_data = vec![0u8; 32];
        OsRng.fill_bytes(&mut new_key_data);
        
        let new_version = old_version + 1;
        let now = Utc::now();
        
        let mut metadata = HashMap::new();
        metadata.insert("generation_method".to_string(), "rotation".to_string());
        metadata.insert("bit_length".to_string(), "256".to_string());
        metadata.insert("trigger_type".to_string(), trigger_type.to_string());
        metadata.insert("previous_version".to_string(), old_version.to_string());
        
        let new_key = KeyVersion {
            version: new_version,
            key_data: new_key_data,
            created_at: now,
            rotated_at: None,
            is_active: true,
            metadata,
        };
        
        // Store new key and deactivate old key
        let conn = Connection::open(&self.db_path)?;
        
        conn.execute(
            "INSERT INTO key_versions (version, key_data, created_at, metadata)
             VALUES (?1, ?2, ?3, ?4)",
            params![
                new_key.version,
                new_key.key_data,
                new_key.created_at.to_rfc3339(),
                serde_json::to_string(&new_key.metadata)?
            ],
        )?;
        
        // Deactivate old key
        conn.execute(
            "UPDATE key_versions 
             SET is_active = 0, rotated_at = ?1
             WHERE version = ?2",
            params![now.to_rfc3339(), old_version],
        )?;
        
        // Clean up old versions
        self.cleanup_old_versions(&conn)?;
        
        // Update current key
        *self.current_key.lock().unwrap() = Some(new_key);
        
        // Update metrics
        KEY_ROTATION_COUNTER.inc();
        KEY_ROTATION_TIMESTAMP.set(now.timestamp() as f64);
        KEY_VERSION_COUNT.set(self.count_active_versions(&conn)? as f64);
        
        let duration = start_time.elapsed().as_secs_f64();
        
        // Log successful rotation
        self.log_rotation(
            &conn,
            old_version,
            new_version,
            trigger_type,
            duration,
            true,
            None,
        )?;
        
        // Performance check
        if duration > self.policy.performance_threshold_seconds {
            eprintln!(
                "Key rotation took {:.2}s, exceeding threshold of {:.2}s",
                duration, self.policy.performance_threshold_seconds
            );
        } else {
            println!("Key rotation completed successfully in {:.2}s", duration);
        }
        
        Ok(RotationResult {
            success: true,
            old_version: Some(old_version),
            new_version: Some(new_version),
            duration_seconds: duration,
            trigger_type: trigger_type.to_string(),
            reason: None,
        })
    }

    fn cleanup_old_versions(&self, conn: &Connection) -> Result<(), Box<dyn std::error::Error>> {
        let total_versions: i64 = conn.query_row("SELECT COUNT(*) FROM key_versions", [], |row| row.get(0))?;
        
        if total_versions > self.policy.max_key_versions {
            let versions_to_delete = total_versions - self.policy.max_key_versions;
            conn.execute(
                "DELETE FROM key_versions 
                 WHERE version IN (
                     SELECT version FROM key_versions 
                     ORDER BY version ASC 
                     LIMIT ?1
                 )",
                [versions_to_delete],
            )?;
            
            println!("Cleaned up {} old key versions", versions_to_delete);
        }
        
        Ok(())
    }

    fn count_active_versions(&self, conn: &Connection) -> Result<i64, Box<dyn std::error::Error>> {
        let count: i64 = conn.query_row("SELECT COUNT(*) FROM key_versions", [], |row| row.get(0))?;
        Ok(count)
    }

    fn log_rotation(
        &self,
        conn: &Connection,
        old_version: i64,
        new_version: i64,
        trigger_type: &str,
        duration: f64,
        success: bool,
        error_message: Option<&str>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        conn.execute(
            "INSERT INTO rotation_log 
             (timestamp, old_version, new_version, trigger_type, duration_seconds, success, error_message)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                Utc::now().to_rfc3339(),
                old_version,
                new_version,
                trigger_type,
                duration,
                success,
                error_message
            ],
        )?;
        
        Ok(())
    }

    pub fn get_rotation_history(&self, limit: i64) -> Result<Vec<serde_json::Value>, Box<dyn std::error::Error>> {
        let conn = Connection::open(&self.db_path)?;
        
        let mut stmt = conn.prepare(
            "SELECT timestamp, old_version, new_version, trigger_type, 
                    duration_seconds, success, error_message
             FROM rotation_log 
             ORDER BY timestamp DESC 
             LIMIT ?1"
        )?;
        
        let rows = stmt.query_map([limit], |row| {
            Ok(serde_json::json!({
                "timestamp": row.get::<_, String>(0)?,
                "old_version": row.get::<_, i64>(1)?,
                "new_version": row.get::<_, i64>(2)?,
                "trigger_type": row.get::<_, String>(3)?,
                "duration_seconds": row.get::<_, f64>(4)?,
                "success": row.get::<_, bool>(5)?,
                "error_message": row.get::<_, Option<String>>(6)?
            }))
        })?;
        
        let mut history = Vec::new();
        for row in rows {
            history.push(row?);
        }
        
        Ok(history)
    }

    pub fn export_key_metadata(&self) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let current_key = self.get_current_key().ok();
        let history = self.get_rotation_history(10)?;
        let (should_rotate, reason) = self.should_rotate()?;
        
        Ok(serde_json::json!({
            "current_key_version": current_key.as_ref().map(|k| k.version),
            "should_rotate": should_rotate,
            "rotation_reason": reason,
            "policy": {
                "rotation_interval_days": self.policy.rotation_interval_days,
                "max_key_versions": self.policy.max_key_versions,
                "auto_rotation_enabled": self.policy.auto_rotation_enabled,
                "performance_threshold_seconds": self.policy.performance_threshold_seconds
            },
            "rotation_history": history,
            "metrics": {
                "total_rotations": KEY_ROTATION_COUNTER.get(),
                "last_rotation_timestamp": KEY_ROTATION_TIMESTAMP.get(),
                "active_versions": KEY_VERSION_COUNT.get()
            }
        }))
    }
}

// Tauri command handlers
#[tauri::command]
pub async fn rotate_vault_keys(force: Option<bool>) -> Result<RotationResult, String> {
    let force = force.unwrap_or(false);
    
    // This would be initialized with proper paths in a real implementation
    let db_path = PathBuf::from("hearthlink_data/vault_keys.db");
    let manager = VaultKeyRotationManager::new(db_path, None)
        .map_err(|e| format!("Failed to initialize key rotation manager: {}", e))?;
    
    manager.rotate_key("api", force).await
        .map_err(|e| format!("Key rotation failed: {}", e))
}

#[tauri::command]
pub async fn get_vault_key_status() -> Result<serde_json::Value, String> {
    let db_path = PathBuf::from("hearthlink_data/vault_keys.db");
    let manager = VaultKeyRotationManager::new(db_path, None)
        .map_err(|e| format!("Failed to initialize key rotation manager: {}", e))?;
    
    manager.export_key_metadata()
        .map_err(|e| format!("Failed to export key metadata: {}", e))
}

#[tauri::command]
pub async fn get_vault_rotation_history(limit: Option<i64>) -> Result<Vec<serde_json::Value>, String> {
    let limit = limit.unwrap_or(50);
    let db_path = PathBuf::from("hearthlink_data/vault_keys.db");
    let manager = VaultKeyRotationManager::new(db_path, None)
        .map_err(|e| format!("Failed to initialize key rotation manager: {}", e))?;
    
    manager.get_rotation_history(limit)
        .map_err(|e| format!("Failed to get rotation history: {}", e))
}

#[tauri::command]
pub async fn rollback_vault_key(target_version: i64) -> Result<RotationResult, String> {
    let db_path = PathBuf::from("hearthlink_data/vault_keys.db");
    let manager = VaultKeyRotationManager::new(db_path, None)
        .map_err(|e| format!("Failed to initialize key rotation manager: {}", e))?;
    
    let start_time = std::time::Instant::now();
    let current_key = manager.get_current_key()
        .map_err(|e| format!("Failed to get current key: {}", e))?;
    
    let target_key = manager.get_key_by_version(target_version)
        .map_err(|e| format!("Failed to get target key: {}", e))?
        .ok_or_else(|| format!("Key version {} not found", target_version))?;
    
    // Update database to activate target key
    let conn = Connection::open(&manager.db_path)
        .map_err(|e| format!("Failed to open database: {}", e))?;
    
    conn.execute("UPDATE key_versions SET is_active = 0 WHERE is_active = 1", [])
        .map_err(|e| format!("Failed to deactivate current key: {}", e))?;
    
    conn.execute("UPDATE key_versions SET is_active = 1 WHERE version = ?1", [target_version])
        .map_err(|e| format!("Failed to activate target key: {}", e))?;
    
    let duration = start_time.elapsed().as_secs_f64();
    
    // Log rollback
    manager.log_rotation(&conn, current_key.version, target_version, "rollback", duration, true, None)
        .map_err(|e| format!("Failed to log rollback: {}", e))?;
    
    Ok(RotationResult {
        success: true,
        old_version: Some(current_key.version),
        new_version: Some(target_version),
        duration_seconds: duration,
        trigger_type: "rollback".to_string(),
        reason: None,
    })
}