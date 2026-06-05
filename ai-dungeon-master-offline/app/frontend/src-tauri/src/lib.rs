use std::process::Command;
use std::path::{PathBuf};

fn find_docker_compose_dir() -> Option<PathBuf> {
    // Start from current exe directory and search upwards for docker-compose.yml
    let current_exe = std::env::current_exe().ok();
    
    // Also try current working directory
    let mut search_paths = Vec::new();
    if let Some(exe) = current_exe {
        search_paths.push(exe);
    }
    if let Ok(cwd) = std::env::current_dir() {
        search_paths.push(cwd);
    }
    
    for mut path in search_paths {
        for _ in 0..10 { // limit search depth
            if path.join("docker-compose.yml").exists() {
                return Some(path);
            }
            if !path.pop() {
                break;
            }
        }
    }
    None
}

fn start_backend() {
    if let Some(dir) = find_docker_compose_dir() {
        println!("[Tauri] Starting backend services via docker compose in: {:?}", dir);
        #[cfg(target_os = "windows")]
        let status = Command::new("cmd")
            .args(&["/C", "docker compose up -d"])
            .current_dir(&dir)
            .status();
            
        #[cfg(not(target_os = "windows"))]
        let status = Command::new("docker")
            .args(&["compose", "up", "-d"])
            .current_dir(&dir)
            .status();
            
        match status {
            Ok(s) if s.success() => println!("[Tauri] Docker Compose started successfully."),
            Ok(s) => eprintln!("[Tauri] Docker Compose failed to start with status: {}", s),
            Err(e) => eprintln!("[Tauri] Error executing docker compose: {}", e),
        }
    } else {
        eprintln!("[Tauri] Warning: docker-compose.yml not found.");
    }
}

fn stop_backend() {
    if let Some(dir) = find_docker_compose_dir() {
        println!("[Tauri] Stopping backend services via docker compose in: {:?}", dir);
        #[cfg(target_os = "windows")]
        let _ = Command::new("cmd")
            .args(&["/C", "docker compose stop"])
            .current_dir(&dir)
            .status();
            
        #[cfg(not(target_os = "windows"))]
        let _ = Command::new("docker")
            .args(&["compose", "stop"])
            .current_dir(&dir)
            .status();
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      start_backend();
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");

  // Stop the background containers when the Tauri app exits
  stop_backend();
}

