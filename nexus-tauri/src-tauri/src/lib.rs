use tauri::Manager;

#[tauri::command]
fn get_nexus_session_id() -> String {
  std::env::var("NEXUS_SESSION_ID").unwrap_or_default()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .invoke_handler(tauri::generate_handler![get_nexus_session_id])
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      // Ascendance harness G1 predicate: inject NEXUS_SESSION_ID into window before page JS runs.
      let sid = std::env::var("NEXUS_SESSION_ID").unwrap_or_default();
      if let Some(win) = app.get_webview_window("main") {
        if !sid.is_empty() {
          // Escape sid for JS literal (UUID chars are safe but defend anyway)
          let escaped = sid.replace('\\', "\\\\").replace('"', "\\\"");
          let script = format!(
            "(function(){{\
              window.__NEXUS_SESSION_ID = \"{sid}\";\
              var apply = function(){{ \
                if (document.documentElement) {{ \
                  document.documentElement.setAttribute('data-session-id', window.__NEXUS_SESSION_ID); \
                  if (!document.documentElement.getAttribute('data-hydration-state')) {{ \
                    document.documentElement.setAttribute('data-hydration-state', 'idle'); \
                  }} \
                }} \
              }}; \
              apply(); \
              if (document.readyState === 'loading') {{ \
                document.addEventListener('DOMContentLoaded', apply, {{ once: true }}); \
              }} \
            }})();",
            sid = escaped
          );
          let _ = win.eval(&script);
        }
        // Open devtools on main window when ARKNEXUS_DEVTOOLS=1
        if std::env::var("ARKNEXUS_DEVTOOLS").unwrap_or_default() == "1" {
          win.open_devtools();
        }
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
