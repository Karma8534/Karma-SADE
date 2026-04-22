use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      // Ascendance harness: open devtools on main window when ARKNEXUS_DEVTOOLS=1
      if std::env::var("ARKNEXUS_DEVTOOLS").unwrap_or_default() == "1" {
        if let Some(win) = app.get_webview_window("main") {
          win.open_devtools();
        }
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
