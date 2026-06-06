import os
from pathlib import Path
from typing import Optional

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    HAS_FASTER_WHISPER = False

class WhisperService:
    def __init__(self, model_size: str = "base"):
        self.model = None
        if HAS_FASTER_WHISPER:
            try:
                # Attempt to load using CUDA if available
                print(f"[Whisper] Loading faster-whisper '{model_size}' on CUDA GPU...", flush=True)
                self.model = WhisperModel(model_size, device="cuda", compute_type="float16")
                print(f"[Whisper] faster-whisper '{model_size}' loaded successfully on GPU.", flush=True)
            except Exception as e_cuda:
                print(f"[Whisper] CUDA loading failed: {e_cuda}. Falling back to CPU...", flush=True)
                try:
                    # Fallback to CPU with int8 optimization (extremely fast and light)
                    self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
                    print(f"[Whisper] faster-whisper '{model_size}' loaded successfully on CPU.", flush=True)
                except Exception as e_cpu:
                    print(f"[Whisper] CPU loading failed: {e_cpu}. Transcription will fallback to mock.", flush=True)
                    self.model = None
        else:
            print("[Whisper] faster-whisper library is not installed. Using mock fallback.", flush=True)

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes a WAV file using faster-whisper, falling back to a dummy action if model is offline.
        """
        if self.model is not None:
            try:
                print(f"[Whisper] Transcribing {audio_file_path} using faster-whisper...", flush=True)
                segments, info = self.model.transcribe(audio_file_path, language="es", beam_size=5)
                
                # Combine segments text
                transcript = "".join([segment.text for segment in segments]).strip()
                print(f"[Whisper] Transcription result: '{transcript}'", flush=True)
                return transcript
            except Exception as e:
                print(f"[Whisper] faster-whisper transcription error: {e}.", flush=True)

        # Fallback
        print("[Whisper] No transcription engine active. Returning mock action.", flush=True)
        return "Miro a mi alrededor buscando una salida."
