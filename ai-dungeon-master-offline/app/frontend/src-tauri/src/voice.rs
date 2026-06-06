use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::process::Command;
use crate::db::find_data_dir;

pub struct VoiceService {
    pub piper_binary: String,
    pub piper_model: String,
}

impl VoiceService {
    pub fn new() -> Self {
        let data_dir = find_data_dir();
        // Base dir is parent of data (i.e., app/)
        let base_dir = data_dir.parent().unwrap_or(&data_dir);
        
        let mut piper_binary = base_dir.join("engines").join("piper").join("piper").to_string_lossy().to_string();
        if cfg!(target_os = "windows") && !piper_binary.ends_with(".exe") {
            piper_binary.push_str(".exe");
        }

        let piper_model = base_dir
            .join("engines")
            .join("piper")
            .join("voices")
            .join("es_ES-kiko-medium.onnx")
            .to_string_lossy()
            .to_string();

        VoiceService {
            piper_binary,
            piper_model,
        }
    }

    pub fn synthesize(&self, text: &str, output_wav_path: &str) -> Result<String, std::io::Error> {
        let binary_exists = Path::new(&self.piper_binary).exists();
        let model_exists = Path::new(&self.piper_model).exists();

        if !binary_exists || !model_exists {
            println!(
                "[Piper] Binary ({}) or Model ({}) not found. Mocking audio output file.",
                self.piper_binary, self.piper_model
            );
            // Write 44 bytes of empty WAV header
            let mut file = File::create(output_wav_path)?;
            file.write_all(b"RIFF\xff\xff\xff\xffWAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")?;
            return Ok(output_wav_path.to_string());
        }

        #[cfg(target_os = "windows")]
        {
            // Run process: piper -m <model> -f <output>
            // We feed text via stdin
            let mut child = Command::new(&self.piper_binary)
                .args(&["-m", &self.piper_model, "-f", output_wav_path])
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::piped())
                .spawn()?;

            if let Some(mut stdin) = child.stdin.take() {
                stdin.write_all(text.as_bytes())?;
            }

            let output = child.wait_with_output()?;
            if !output.status.success() {
                eprintln!("[Piper] Synthesis failed: {:?}", String::from_utf8_lossy(&output.stderr));
            }
        }

        #[cfg(not(target_os = "windows"))]
        {
            let mut child = Command::new(&self.piper_binary)
                .args(&["-m", &self.piper_model, "-f", output_wav_path])
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::piped())
                .spawn()?;

            if let Some(mut stdin) = child.stdin.take() {
                stdin.write_all(text.as_bytes())?;
            }

            let _ = child.wait_with_output()?;
        }

        Ok(output_wav_path.to_string())
    }

    pub fn transcribe(&self, audio_file_path: &str) -> String {
        let data_dir = find_data_dir();
        let helper_path = data_dir.join("whisper_helper.py");
        
        println!("[Whisper] Executing whisper_helper.py with audio path: {}", audio_file_path);

        let output = Command::new("python")
            .args(&[helper_path.to_string_lossy().to_string(), audio_file_path.to_string()])
            .output();

        match output {
            Ok(out) => {
                if out.status.success() {
                    let text = String::from_utf8_lossy(&out.stdout).trim().to_string();
                    if !text.is_empty() {
                        println!("[Whisper] Transcribed text: '{}'", text);
                        return text;
                    }
                } else {
                    eprintln!(
                        "[Whisper] Helper failed with exit status: {:?}, error: {:?}",
                        out.status.code(),
                        String::from_utf8_lossy(&out.stderr)
                    );
                }
            }
            Err(e) => {
                eprintln!("[Whisper] Failed to run python subprocess: {}", e);
            }
        }

        // Fallback
        "Miro a mi alrededor buscando una salida.".to_string()
    }
}
