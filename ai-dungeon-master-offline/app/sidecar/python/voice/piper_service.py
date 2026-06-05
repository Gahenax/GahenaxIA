import os
import subprocess
from pathlib import Path
from typing import Optional

class PiperService:
    def __init__(self, binary_path: Optional[str] = None, model_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parents[3] # memory -> python -> sidecar -> app
        
        self.binary_path = binary_path or str(base_dir / "engines" / "piper" / "piper")
        self.model_path = model_path or str(base_dir / "engines" / "piper" / "voices" / "es_ES-kiko-medium.onnx")

        # Handle Windows binary naming
        if os.name == "nt" and not self.binary_path.endswith(".exe"):
            self.binary_path += ".exe"

    def synthesize(self, text: str, output_wav_path: str) -> str:
        """
        Synthesizes text into a WAV file using Piper TTS.
        If the binary or model does not exist, it falls back to a simulated dummy print.
        """
        if not os.path.exists(self.binary_path) or not os.path.exists(self.model_path):
            print(f"[Piper] Binary ({self.binary_path}) or Model ({self.model_path}) not found. Mocking audio output file.")
            # Touch the output file so it exists for the frontend player
            with open(output_wav_path, "wb") as f:
                f.write(b"RIFF\xff\xff\xff\xffWAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            return output_wav_path
            
        try:
            # Command: echo "<text>" | piper -m <model> -f <output>
            # On Windows, echoing text via subprocess can be done using stdin parameter.
            cmd = [
                self.binary_path,
                "-m", self.model_path,
                "-f", output_wav_path
            ]
            
            subprocess.run(cmd, input=text, capture_output=True, text=True, check=True)
            return output_wav_path
        except Exception as e:
            print(f"[Piper] Subprocess execution error: {e}. Falling back to empty WAV.")
            with open(output_wav_path, "wb") as f:
                f.write(b"RIFF\xff\xff\xff\xffWAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            return output_wav_path
        
