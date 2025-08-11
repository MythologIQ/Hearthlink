// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex, OnceLock};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::path::{Path, PathBuf};
use std::env;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};

use tauri::{Manager, State, Window};
use serde::{Deserialize, Serialize};
use tokio::time::sleep;

mod vault_rotation;

// Single-instance lock management
static INSTANCE_LOCK: OnceLock<Option<File>> = OnceLock::new();

// Port profiles for different environments
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PortProfile {
    Default,  // 8000, 8001, 8002, 8888
    Qa,       // 8010, 8011, 8012, 8898
    Dev,      // 8020, 8021, 8022, 8908
}

impl PortProfile {
    fn get_ports(&self) -> (u16, u16, u16, u16) {
        match self {
            PortProfile::Default => (8000, 8001, 8002, 8888), // core, vault, synapse, alden
            PortProfile::Qa => (8010, 8011, 8012, 8898),
            PortProfile::Dev => (8020, 8021, 8022, 8908),
        }
    }
    
    fn from_env() -> Self {
        match env::var("HEARTHLINK_PORT_PROFILE").unwrap_or_default().as_str() {
            "qa" => PortProfile::Qa,
            "dev" => PortProfile::Dev,
            _ => PortProfile::Default,
        }
    }
}

// Single instance enforcement
fn acquire_instance_lock() -> Result<(), String> {
    let lock_file_path = if cfg!(windows) {
        env::temp_dir().join("hearthlink_instance.lock")
    } else {
        PathBuf::from("/tmp/hearthlink_instance.lock")
    };

    match OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(&lock_file_path)
    {
        Ok(mut file) => {
            // Write current process ID to lock file
            let pid = std::process::id().to_string();
            if file.write_all(pid.as_bytes()).is_err() {
                return Err("Failed to write to lock file".to_string());
            }
            
            // Store the lock file handle to keep it locked
            INSTANCE_LOCK.set(Some(file)).map_err(|_| "Failed to store lock file handle")?;
            
            println!("✅ Single instance lock acquired (PID: {})", pid);
            Ok(())
        }
        Err(e) => {
            // Check if another instance is running
            if lock_file_path.exists() {
                if let Ok(mut file) = File::open(&lock_file_path) {
                    let mut contents = String::new();
                    if file.read_to_string(&mut contents).is_ok() {
                        if let Ok(other_pid) = contents.trim().parse::<u32>() {
                            return Err(format!(
                                "Another Hearthlink instance is already running (PID: {}). Please close it first.",
                                other_pid
                            ));
                        }
                    }
                }
            }
            Err(format!("Failed to acquire instance lock: {}", e))
        }
    }
}

fn release_instance_lock() {
    let lock_file_path = if cfg!(windows) {
        env::temp_dir().join("hearthlink_instance.lock")
    } else {
        PathBuf::from("/tmp/hearthlink_instance.lock")
    };

    // Drop the lock file handle
    if let Some(lock) = INSTANCE_LOCK.get() {
        drop(lock);
    }
    
    // Remove the lock file
    if lock_file_path.exists() {
        if let Err(e) = std::fs::remove_file(&lock_file_path) {
            eprintln!("Warning: Failed to remove lock file: {}", e);
        } else {
            println!("✅ Single instance lock released");
        }
    }
}

// Service status tracking
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceStatus {
    pub name: String,
    pub status: String, // "starting", "running", "stopped", "error"
    pub port: u16,
    pub pid: Option<u32>,
    pub started_at: Option<u64>,
    pub health_check_url: String,
    pub last_health_check: Option<u64>,
    pub error_message: Option<String>,
    pub restart_count: u32,
    pub last_restart: Option<u64>,
    pub restart_backoff: u64, // seconds to wait before next restart
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemHealth {
    pub services: Vec<ServiceStatus>,
    pub overall_status: String,
    pub startup_time: u64,
}

// Service process management
pub struct ServiceManager {
    processes: Arc<Mutex<HashMap<String, Child>>>,
    services: Arc<Mutex<HashMap<String, ServiceStatus>>>,
    startup_time: u64,
    port_profile: PortProfile,
    shutdown_in_progress: Arc<Mutex<bool>>,
}

impl ServiceManager {
    pub fn new() -> Self {
        let port_profile = PortProfile::from_env();
        println!("🚀 Initializing ServiceManager with {:?} port profile", port_profile);
        
        Self {
            processes: Arc::new(Mutex::new(HashMap::new())),
            services: Arc::new(Mutex::new(HashMap::new())),
            startup_time: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            port_profile,
            shutdown_in_progress: Arc::new(Mutex::new(false)),
        }
    }

    pub fn start_all_services(&self, resource_dir: PathBuf) -> Result<(), String> {
        // Get ports from the current profile
        let (core_port, vault_port, synapse_port, alden_port) = self.port_profile.get_ports();
        
        println!("📡 Starting services on ports - Core:{}, Vault:{}, Synapse:{}, Alden:{}", 
                core_port, vault_port, synapse_port, alden_port);
        
        // Define Python services with their configurations using dynamic ports
        let services = vec![
            ("alden", "src/api/alden_api.py", alden_port, format!("http://127.0.0.1:{}/health", alden_port)),
            ("vault", "src/vault/vault_api_server.py", vault_port, format!("http://127.0.0.1:{}/health", vault_port)),
            ("core", "src/api/core_api.py", core_port, format!("http://127.0.0.1:{}/health", core_port)),
            ("synapse", "src/api/synapse_api_server.py", synapse_port, format!("http://127.0.0.1:{}/health", synapse_port)),
        ];
        
        // Pre-flight port availability check
        self.check_port_availability(&services)?;

        for (name, script_path, port, health_url) in services {
            self.start_service(name, script_path, port, &health_url, &resource_dir)?;
        }

        // Start health monitoring
        self.start_health_monitoring();

        Ok(())
    }

    fn start_service(
        &self,
        name: &str,
        script_path: &str,
        port: u16,
        health_url: &str,
        resource_dir: &PathBuf,
    ) -> Result<(), String> {
        let python_path = self.find_python_executable()?;
        let full_script_path = resource_dir.join(script_path);

        if !full_script_path.exists() {
            return Err(format!("Python script not found: {}", full_script_path.display()));
        }

        // Set environment variables
        let vault_key = env::var("HEARTHLINK_VAULT_KEY")
            .unwrap_or_else(|_| "yFLl9T3j6l_rsrgSIHMDqr5O_vt62MdpkJuhIEuilAM=".to_string());

        let mut cmd = Command::new(&python_path)
            .arg(full_script_path)
            .arg("--host")
            .arg("127.0.0.1")
            .arg("--port")
            .arg(port.to_string())
            .env("HEARTHLINK_VAULT_KEY", &vault_key)
            .env("PYTHONPATH", resource_dir.display().to_string())
            .env("HEARTHLINK_DATA_DIR", resource_dir.join("hearthlink_data").display().to_string())
            .stdin(Stdio::null())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to start {} service: {}", name, e))?;

        let pid = cmd.id();

        // Store process
        {
            let mut processes = self.processes.lock().unwrap();
            processes.insert(name.to_string(), cmd);
        }

        // Initialize service status
        let status = ServiceStatus {
            name: name.to_string(),
            status: "starting".to_string(),
            port,
            pid: Some(pid),
            started_at: Some(
                SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs(),
            ),
            health_check_url: health_url.to_string(),
            last_health_check: None,
            error_message: None,
            restart_count: 0,
            last_restart: None,
            restart_backoff: 1, // Start with 1 second backoff
        };

        {
            let mut services = self.services.lock().unwrap();
            services.insert(name.to_string(), status);
        }

        println!("Started {} service on port {} with PID {}", name, port, pid);
        Ok(())
    }

    fn find_python_executable(&self) -> Result<String, String> {
        // Try different Python executable names
        let python_names = vec!["python3", "python", "python.exe", "python3.exe"];
        
        for name in python_names {
            if let Ok(output) = Command::new(name).arg("--version").output() {
                if output.status.success() {
                    let version = String::from_utf8_lossy(&output.stdout);
                    if version.contains("Python 3.") {
                        println!("Found Python: {} ({})", name, version.trim());
                        return Ok(name.to_string());
                    }
                }
            }
        }

        Err("Python 3.x not found. Please ensure Python 3.x is installed and in PATH.".to_string())
    }

    fn check_port_availability(&self, services: &[(&str, &str, u16, String)]) -> Result<(), String> {
        use std::net::TcpListener;
        
        for (name, _, port, _) in services {
            match TcpListener::bind(format!("127.0.0.1:{}", port)) {
                Ok(_) => {
                    println!("✓ Port {} available for {} service", port, name);
                }
                Err(e) => {
                    return Err(format!("Port {} unavailable for {} service: {}", port, name, e));
                }
            }
        }
        Ok(())
    }
    
    fn restart_service_with_backoff(&self, service_name: &str, resource_dir: &PathBuf) -> Result<(), String> {
        let (core_port, vault_port, synapse_port, alden_port) = self.port_profile.get_ports();
        
        let service_config = match service_name {
            "alden" => ("src/api/alden_api.py", alden_port, format!("http://127.0.0.1:{}/health", alden_port)),
            "vault" => ("src/vault/vault_api_server.py", vault_port, format!("http://127.0.0.1:{}/health", vault_port)),
            "core" => ("src/api/core_api.py", core_port, format!("http://127.0.0.1:{}/health", core_port)),
            "synapse" => ("src/api/synapse_api_server.py", synapse_port, format!("http://127.0.0.1:{}/health", synapse_port)),
            _ => return Err(format!("Unknown service: {}", service_name)),
        };
        
        // Check if service should be restarted based on backoff
        let should_restart = {
            let services = self.services.lock().unwrap();
            if let Some(service) = services.get(service_name) {
                if service.restart_count >= 5 {
                    println!("Service {} has failed {} times, not restarting", service_name, service.restart_count);
                    return Err("Max restart attempts exceeded".to_string());
                }
                
                if let Some(last_restart) = service.last_restart {
                    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
                    let time_since_restart = now - last_restart;
                    if time_since_restart < service.restart_backoff {
                        println!("Service {} in backoff period, waiting {} more seconds", 
                                service_name, service.restart_backoff - time_since_restart);
                        return Ok(()); // Don't restart yet
                    }
                }
                true
            } else {
                false
            }
        };
        
        if !should_restart {
            return Ok(());
        }
        
        println!("Restarting {} service with exponential backoff", service_name);
        
        // Stop existing process if running
        self.graceful_stop_service(service_name);
        
        // Start the service again
        match self.start_service(service_name, service_config.0, service_config.1, &service_config.2, resource_dir) {
            Ok(_) => {
                // Update restart statistics
                let mut services = self.services.lock().unwrap();
                if let Some(service) = services.get_mut(service_name) {
                    service.restart_count += 1;
                    service.last_restart = Some(SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs());
                    // Exponential backoff: 1, 2, 4, 8, 16 seconds
                    service.restart_backoff = std::cmp::min(service.restart_backoff * 2, 30);
                    println!("Service {} restarted (attempt {}), next backoff: {}s", 
                            service_name, service.restart_count, service.restart_backoff);
                }
                Ok(())
            }
            Err(e) => {
                println!("Failed to restart {} service: {}", service_name, e);
                Err(e)
            }
        }
    }
    
    fn graceful_stop_service(&self, service_name: &str) {
        let mut processes = self.processes.lock().unwrap();
        if let Some(mut process) = processes.remove(service_name) {
            println!("Gracefully stopping {} service...", service_name);
            
            // Step 1: Send SIGTERM (terminate)
            let _ = process.kill();
            
            // Step 2: Wait for up to 10 seconds
            let wait_result = std::thread::spawn(move || {
                std::thread::sleep(Duration::from_secs(10));
                let _ = process.wait();
            }).join();
            
            if wait_result.is_err() {
                println!("Force killing {} service after timeout", service_name);
            }
        }
        
        // Update service status
        let mut services = self.services.lock().unwrap();
        if let Some(service) = services.get_mut(service_name) {
            service.status = "stopped".to_string();
            service.pid = None;
        }
    }
    
    fn start_health_monitoring(&self) {
        let services_clone = Arc::clone(&self.services);
        
        tokio::spawn(async move {
            let client = reqwest::Client::builder()
                .timeout(Duration::from_secs(5))
                .build()
                .unwrap();

            // Track startup phase outside the loop
            let mut startup_phase = true;
            let mut startup_elapsed = 0;
            let startup_duration = 60; // seconds

            loop {
                let probe_interval = if startup_phase { 5 } else { 30 };
                sleep(Duration::from_secs(probe_interval)).await;
                
                if startup_phase {
                    startup_elapsed += probe_interval;
                    if startup_elapsed >= startup_duration {
                        startup_phase = false;
                        println!("Health monitoring: Switching to steady-state mode (30s intervals)");
                    }
                }
                
                let service_names: Vec<String> = {
                    let services = services_clone.lock().unwrap();
                    services.keys().cloned().collect()
                };

                for name in service_names {
                    let health_url = {
                        let services = services_clone.lock().unwrap();
                        services.get(&name).map(|s| s.health_check_url.clone())
                    };

                    if let Some(url) = health_url {
                        let health_result = client.get(&url).send().await;
                        
                        let mut services = services_clone.lock().unwrap();
                        if let Some(service) = services.get_mut(&name) {
                            service.last_health_check = Some(
                                SystemTime::now()
                                    .duration_since(UNIX_EPOCH)
                                    .unwrap()
                                    .as_secs(),
                            );

                            match health_result {
                            Ok(response) if response.status().is_success() => {
                            if service.status == "starting" || service.status == "error" {
                            service.status = "running".to_string();
                            service.error_message = None;
                            // Reset restart count on successful health check
                                service.restart_count = 0;
                                    service.restart_backoff = 1;
                                    println!("{} service is healthy", name);
                            }
                            }
                            Ok(response) => {
                                let was_running = service.status == "running";
                            service.status = "error".to_string();
                            service.error_message = Some(format!("HTTP {}", response.status()));
                                
                                    if was_running {
                                        println!("{} service unhealthy (HTTP {}), scheduling restart", name, response.status());
                                    }
                                }
                                Err(e) => {
                                    let was_running = service.status == "running";
                                    service.status = "error".to_string();
                                    service.error_message = Some(e.to_string());
                                    
                                    if was_running {
                                        println!("{} service unhealthy ({}), scheduling restart", name, e);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    pub fn get_system_health(&self) -> SystemHealth {
        let services = self.services.lock().unwrap();
        let service_list: Vec<ServiceStatus> = services.values().cloned().collect();
        
        let overall_status = if service_list.iter().all(|s| s.status == "running") {
            "healthy".to_string()
        } else if service_list.iter().any(|s| s.status == "running") {
            "degraded".to_string()
        } else {
            "unhealthy".to_string()
        };

        SystemHealth {
            services: service_list,
            overall_status,
            startup_time: self.startup_time,
        }
    }

    pub fn stop_all_services(&self) {
        // Check if shutdown is already in progress
        {
            let mut shutdown_flag = self.shutdown_in_progress.lock().unwrap();
            if *shutdown_flag {
                println!("⚠️  Shutdown already in progress, skipping duplicate request");
                return;
            }
            *shutdown_flag = true;
        }
        
        println!("🛑 Initiating enhanced shutdown sequence...");
        
        // Step 1: Gracefully shutdown in reverse dependency order
        let shutdown_order = vec!["synapse", "core", "vault", "alden"];
        
        for service_name in &shutdown_order {
            self.graceful_stop_service_enhanced(service_name);
        }
        
        // Step 2: Force cleanup any remaining processes after timeout
        println!("🧹 Final cleanup: terminating any remaining processes");
        let mut processes = self.processes.lock().unwrap();
        
        for (name, mut process) in processes.drain() {
            println!("Force terminating {} service...", name);
            let _ = process.kill();
            
            // Give it a moment to terminate
            std::thread::sleep(Duration::from_millis(500));
            let _ = process.wait();
        }

        // Step 3: Update service statuses
        let mut services = self.services.lock().unwrap();
        for (_, service) in services.iter_mut() {
            service.status = "stopped".to_string();
            service.pid = None;
        }
        
        // Step 4: Release instance lock
        release_instance_lock();
        
        println!("✅ Enhanced shutdown sequence completed");
    }
    
    fn graceful_stop_service_enhanced(&self, service_name: &str) {
        let mut processes = self.processes.lock().unwrap();
        if let Some(mut process) = processes.remove(service_name) {
            println!("🔄 Gracefully stopping {} service (enhanced)...", service_name);
            
            // Step 1: Send SIGTERM (terminate) - give process chance to cleanup
            match process.kill() {
                Ok(_) => println!("  📤 SIGTERM sent to {} service", service_name),
                Err(e) => println!("  ⚠️  Failed to send SIGTERM to {}: {}", service_name, e),
            }
            
            // Step 2: Wait for up to 15 seconds for graceful shutdown
            let wait_handle = std::thread::spawn(move || {
                for i in 0..15 {
                    match process.try_wait() {
                        Ok(Some(_)) => {
                            println!("  ✅ {} service stopped gracefully after {}s", service_name, i);
                            return true;
                        }
                        Ok(None) => {
                            // Still running, wait a bit more
                            std::thread::sleep(Duration::from_secs(1));
                        }
                        Err(e) => {
                            println!("  ⚠️  Error checking {} service status: {}", service_name, e);
                            break;
                        }
                    }
                }
                
                // Force kill after timeout
                println!("  🔨 Force killing {} service after 15s timeout", service_name);
                let _ = process.kill();
                let _ = process.wait();
                false
            });
            
            // Wait for the shutdown thread to complete
            if let Err(_) = wait_handle.join() {
                println!("  ⚠️  Shutdown thread for {} service panicked", service_name);
            }
        } else {
            println!("  ℹ️  {} service not running or already stopped", service_name);
        }
        
        // Update service status
        let mut services = self.services.lock().unwrap();
        if let Some(service) = services.get_mut(service_name) {
            service.status = "stopped".to_string();
            service.pid = None;
        }
    }
}

// Tauri commands
#[tauri::command]
async fn get_system_health(
    service_manager: State<'_, ServiceManager>,
) -> Result<SystemHealth, String> {
    Ok(service_manager.get_system_health())
}

#[tauri::command]
async fn restart_service(
    service_name: String,
    service_manager: State<'_, ServiceManager>,
    app: tauri::AppHandle,
) -> Result<String, String> {
    // Get resource directory
    let resource_dir = app
        .path_resolver()
        .resource_dir()
        .ok_or("Failed to get resource directory")?;

    // Get current port profile
    let (core_port, vault_port, synapse_port, alden_port) = service_manager.port_profile.get_ports();
    
    // Find service configuration
    let service_config = match service_name.as_str() {
        "alden" => ("src/api/alden_api.py", alden_port, format!("http://127.0.0.1:{}/health", alden_port)),
        "vault" => ("src/vault/vault_api_server.py", vault_port, format!("http://127.0.0.1:{}/health", vault_port)),
        "core" => ("src/api/core_api.py", core_port, format!("http://127.0.0.1:{}/health", core_port)),
        "synapse" => ("src/api/synapse_api_server.py", synapse_port, format!("http://127.0.0.1:{}/health", synapse_port)),
        _ => return Err(format!("Unknown service: {}", service_name)),
    };

    // Stop existing process if running
    {
        let mut processes = service_manager.processes.lock().unwrap();
        if let Some(mut process) = processes.remove(&service_name) {
            let _ = process.kill();
            let _ = process.wait();
        }
    }

    // Start the service again
    service_manager.start_service(
        &service_name,
        service_config.0,
        service_config.1,
        &service_config.2,
        &resource_dir,
    )?;

    Ok(format!("{} service restarted successfully", service_name))
}

#[tauri::command]
async fn get_service_logs(service_name: String) -> Result<String, String> {
    // In a production app, you'd read from log files
    // For now, return a placeholder
    Ok(format!("Logs for {} service would appear here", service_name))
}

#[tauri::command]
fn get_app_status() -> Result<String, String> {
    Ok("Hearthlink Native App Running".to_string())
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Hearthlink Native.", name)
}

fn main() {
    // Acquire single instance lock before starting
    if let Err(e) = acquire_instance_lock() {
        eprintln!("🚫 {}", e);
        std::process::exit(1);
    }
    
    // Initialize service manager
    let service_manager = ServiceManager::new();

    tauri::Builder::default()
        .manage(service_manager)
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            greet,
            get_system_health,
            restart_service,
            get_service_logs,
            vault_rotation::rotate_vault_keys,
            vault_rotation::get_vault_key_status,
            vault_rotation::get_vault_rotation_history,
            vault_rotation::rollback_vault_key
        ])
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();
            let service_manager = app.state::<ServiceManager>();

            // Get resource directory
            let resource_dir = app
                .path_resolver()
                .resource_dir()
                .expect("Failed to get resource directory");

            println!("Resource directory: {}", resource_dir.display());

            // Start all Python services
            if let Err(e) = service_manager.start_all_services(resource_dir) {
                eprintln!("Failed to start services: {}", e);
                let _ = tauri::api::dialog::message(
                    Some(&window),
                    "Service Startup Error",
                    &format!("Failed to start backend services: {}\n\nPlease ensure Python 3.x is installed and all dependencies are available.", e),
                );
            }

            // Set up cleanup on app shutdown
            let service_manager_clone = app.state::<ServiceManager>();
            let service_manager_for_cleanup = Arc::new(service_manager_clone.inner().clone());

            // Handle window close event
            window.on_window_event({
                let service_manager = Arc::clone(&service_manager_for_cleanup);
                move |event| {
                    if let tauri::WindowEvent::CloseRequested { .. } = event {
                        println!("Application closing, stopping all services...");
                        service_manager.stop_all_services();
                    }
                }
            });

            window.set_focus().unwrap();
            window.show().unwrap();
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// Implement Clone for ServiceManager to allow it to be stored in Arc
impl Clone for ServiceManager {
    fn clone(&self) -> Self {
        Self {
            processes: Arc::clone(&self.processes),
            services: Arc::clone(&self.services),
            startup_time: self.startup_time,
            port_profile: self.port_profile.clone(),
            shutdown_in_progress: Arc::clone(&self.shutdown_in_progress),
        }
    }
}