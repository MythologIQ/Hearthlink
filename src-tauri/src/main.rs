// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Child, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tauri::{Manager, State, SystemTray, SystemTrayMenu, SystemTrayEvent, CustomMenuItem, Window};

#[cfg(target_os = "windows")]
use windows::Win32::Foundation::HWND;
#[cfg(target_os = "windows")]
use windows::Win32::UI::WindowsAndMessaging::{FindWindowA, SetParent, SetWindowPos, SWP_NOZORDER, SWP_NOACTIVATE, HWND_TOP};

// Shared state for managing the Electron process
#[derive(Default)]
struct ElectronManager {
    process: Arc<Mutex<Option<Child>>>,
}

// Commands that can be called from the frontend
#[tauri::command]
fn start_electron_app(manager: State<ElectronManager>) -> Result<String, String> {
    let mut process_lock = manager.process.lock().unwrap();
    
    if process_lock.is_some() {
        return Ok("Electron app is already running".to_string());
    }
    
    let child = Command::new("npm")
        .args(&["run", "launch"])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start Electron app: {}", e))?;
    
    *process_lock = Some(child);
    Ok("Electron app started successfully".to_string())
}

#[tauri::command]
fn stop_electron_app(manager: State<ElectronManager>) -> Result<String, String> {
    let mut process_lock = manager.process.lock().unwrap();
    
    if let Some(mut child) = process_lock.take() {
        child.kill().map_err(|e| format!("Failed to stop Electron app: {}", e))?;
        Ok("Electron app stopped successfully".to_string())
    } else {
        Ok("Electron app is not running".to_string())
    }
}

#[tauri::command]
fn restart_electron_app(manager: State<ElectronManager>) -> Result<String, String> {
    stop_electron_app(manager.clone())?;
    thread::sleep(Duration::from_secs(2));
    start_electron_app(manager)
}

#[tauri::command]
fn get_electron_status(manager: State<ElectronManager>) -> Result<String, String> {
    let process_lock = manager.process.lock().unwrap();
    
    if let Some(child) = process_lock.as_ref() {
        match child.try_wait() {
            Ok(Some(_)) => Ok("stopped".to_string()),
            Ok(None) => Ok("running".to_string()),
            Err(_) => Ok("unknown".to_string()),
        }
    } else {
        Ok("not_started".to_string())
    }
}

fn main() {
    // Create system tray menu
    let tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show", "Show Wrapper"))
        .add_item(CustomMenuItem::new("start", "Start Hearthlink"))
        .add_item(CustomMenuItem::new("stop", "Stop Hearthlink"))
        .add_item(CustomMenuItem::new("restart", "Restart Hearthlink"))
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit", "Quit"));
    
    let system_tray = SystemTray::new().with_menu(tray_menu);
    
    tauri::Builder::default()
        .manage(ElectronManager::default())
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| {
            match event {
                SystemTrayEvent::MenuItemClick { id, .. } => {
                    let manager = app.state::<ElectronManager>();
                    match id.as_str() {
                        "show" => {
                            if let Some(window) = app.get_window("main") {
                                window.show().unwrap();
                                window.set_focus().unwrap();
                            }
                        }
                        "start" => {
                            let _ = start_electron_app(manager.clone());
                        }
                        "stop" => {
                            let _ = stop_electron_app(manager.clone());
                        }
                        "restart" => {
                            let _ = restart_electron_app(manager.clone());
                        }
                        "quit" => {
                            let _ = stop_electron_app(manager.clone());
                            std::process::exit(0);
                        }
                        _ => {}
                    }
                }
                SystemTrayEvent::LeftClick { .. } => {
                    if let Some(window) = app.get_window("main") {
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![
            start_electron_app,
            stop_electron_app,
            restart_electron_app,
            get_electron_status
        ])
        .setup(|app| {
            // Auto-start the Electron app when the native wrapper starts
            let manager = app.state::<ElectronManager>();
            if let Err(e) = start_electron_app(manager.clone()) {
                eprintln!("Failed to auto-start Electron app: {}", e);
            }
            
            // Set up the main window as a native frame
            let window = app.get_window("main").unwrap();
            window.set_title("Hearthlink Native Frame").unwrap();
            
            // Set window properties for native frame
            window.set_resizable(true).unwrap();
            window.set_min_size(Some(tauri::Size::Physical(tauri::PhysicalSize { width: 800, height: 600 }))).unwrap();
            
            // Configure window behavior
            window.center().unwrap();
            
            Ok(())
        })
        .on_window_event(|event| {
            match event.event() {
                tauri::WindowEvent::CloseRequested { api, .. } => {
                    // Minimize to system tray instead of closing
                    event.window().hide().unwrap();
                    api.prevent_close();
                }
                _ => {}
            }
        })
        .build(tauri::generate_context!())
        .expect("error while running tauri application")
        .run(|_app_handle, event| {
            match event {
                tauri::RunEvent::ExitRequested { api, .. } => {
                    // Clean up Electron process on exit
                    api.prevent_exit();
                }
                _ => {}
            }
        });
}
