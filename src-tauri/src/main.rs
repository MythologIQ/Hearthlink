// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::path::{Path, PathBuf};
use std::env;

use tauri::{Manager, State, Window};
use serde::{Deserialize, Serialize};
use tokio::time::sleep;

mod vault_rotation;

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
}

impl ServiceManager {
    pub fn new() -> Self {
        Self {
            processes: Arc::new(Mutex::new(HashMap::new())),
            services: Arc::new(Mutex::new(HashMap::new())),
            startup_time: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        }
    }

    pub fn start_all_services(&self, resource_dir: PathBuf) -> Result<(), String> {
        // Define Python services with their configurations
        let services = vec![
            ("alden", "src/api/alden_api.py", 8888, "http://127.0.0.1:8888/health"),
            ("vault", "src/vault/vault.py", 8001, "http://127.0.0.1:8001/health"),
            ("core", "src/api/core_api.py", 8000, "http://127.0.0.1:8000/health"),
            ("synapse", "src/api/synapse_api_server.py", 8002, "http://127.0.0.1:8002/health"),
        ];

        for (name, script_path, port, health_url) in services {
            self.start_service(name, script_path, port, health_url, &resource_dir)?;
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

    fn start_health_monitoring(&self) {
        let services_clone = Arc::clone(&self.services);
        
        tokio::spawn(async move {
            let client = reqwest::Client::builder()
                .timeout(Duration::from_secs(5))
                .build()
                .unwrap();

            loop {
                sleep(Duration::from_secs(30)).await;
                
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
                                        println!("{} service is healthy", name);
                                    }
                                }
                                Ok(response) => {
                                    service.status = "error".to_string();
                                    service.error_message = Some(format!("HTTP {}", response.status()));
                                }
                                Err(e) => {
                                    service.status = "error".to_string();
                                    service.error_message = Some(e.to_string());
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
        let mut processes = self.processes.lock().unwrap();
        
        for (name, mut process) in processes.drain() {
            println!("Stopping {} service...", name);
            let _ = process.kill();
            let _ = process.wait();
        }

        // Update service statuses
        let mut services = self.services.lock().unwrap();
        for (_, service) in services.iter_mut() {
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

    // Find service configuration
    let service_config = match service_name.as_str() {
        "alden" => ("src/api/alden_api.py", 8888, "http://127.0.0.1:8888/health"),
        "vault" => ("src/vault/vault.py", 8001, "http://127.0.0.1:8001/health"),
        "core" => ("src/api/core_api.py", 8000, "http://127.0.0.1:8000/health"),
        "synapse" => ("src/api/synapse_api_server.py", 8002, "http://127.0.0.1:8002/health"),
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
        service_config.2,
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
        }
    }
}