// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

mod vault_rotation;

// Simple Tauri commands for the native Hearthlink application
#[tauri::command]
fn get_app_status() -> Result<String, String> {
    Ok("Hearthlink Native App Running".to_string())
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Hearthlink Native.", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            greet,
            vault_rotation::rotate_vault_keys,
            vault_rotation::get_vault_key_status,
            vault_rotation::get_vault_rotation_history,
            vault_rotation::rollback_vault_key
        ])
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();
            window.set_focus().unwrap();
            window.show().unwrap();
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}