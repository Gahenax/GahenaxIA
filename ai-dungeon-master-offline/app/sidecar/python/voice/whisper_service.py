import os
import subprocess
from pathlib import Path
from typing import Optional

# Force bypass python-whisper to save RAM/VRAM resource starvation
HAS_PYTHON_WHISPER = False

class WhisperService:
    def __init__(self, binary_path: Optional[str] = None, model_path: Optional[str] = None):
        # Default local engine structure: /app/engines/whisper.cpp/ relative to sidecar/python/
        base_dir = Path(__file__).resolve().parents[3] # memory -> python -> sidecar -> app
        
        self.binary_path = binary_path or str(base_dir / "engines" / "whisper.cpp" / "whisper")
        self.model_path = model_path or str(base_dir / "engines" / "whisper.cpp" / "models" / "ggml-base.bin")

        # Handle Windows binary naming
        if os.name == "nt" and not self.binary_path.endswith(".exe"):
            self.binary_path += ".exe"

        # Load python whisper model if available
        self.python_model = None
        if HAS_PYTHON_WHISPER:
            try:
                print("[Whisper] Loading Python Whisper 'base' model...")
                self.python_model = whisper.load_model("base")
                print("[Whisper] Python Whisper model loaded successfully.")
            except Exception as e:
                print(f"[Whisper] Failed to load Python Whisper model: {e}")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes a WAV file (16kHz, mono) using Python whisper library or whisper.cpp.
        If both are missing, falls back to a simulated dummy transcript.
        """
        # Option A: Use Python whisper library if successfully loaded
        if self.python_model is not None:
            try:
                print(f"[Whisper] Transcribing {audio_file_path} using Python Whisper library...")
                result = self.python_model.transcribe(audio_file_path, language="es")
                transcript = result.get("text", "").strip()
                print(f"[Whisper] Transcription result: '{transcript}'")
                return transcript
            except Exception as e:
                print(f"[Whisper] Python Whisper library transcription error: {e}. Trying whisper.cpp fallback.")

        # Option B: Use whisper.cpp subprocess fallback
        if os.path.exists(self.binary_path) and os.path.exists(self.model_path):
            try:
                cmd = [
                    self.binary_path,
                    "-m", self.model_path,
                    "-f", audio_file_path,
                    "--no-timestamps",
                    "-l", "es" # Force Spanish language
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                transcript = result.stdout.strip()
                return transcript
            except Exception as e:
                print(f"[Whisper] whisper.cpp subprocess execution error: {e}.")

        # Option C: Mock fallback
        print("[Whisper] No transcription engine available. Returning fallback.")
        return "Ataco al goblin con mi espada"
