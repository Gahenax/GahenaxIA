import sys
import os

# Ensure UTF-8 stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

def load_groq_key():
    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sidecar", "python"),
        os.getcwd()
    ]
    for d in search_dirs:
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == "GROQ_API_KEY":
                                return v.strip()
            except Exception:
                pass
    return os.environ.get("GROQ_API_KEY")

def transcribe_groq(audio_path, api_key):
    try:
        import requests
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        with open(audio_path, "rb") as f:
            files = {
                "file": (os.path.basename(audio_path), f.read(), "audio/wav")
            }
        data = {
            "model": "whisper-large-v3-turbo",
            "temperature": "0",
            "response_format": "verbose_json"
        }
        res = requests.post(url, headers=headers, files=files, data=data, timeout=30.0)
        if res.status_code == 200:
            return res.json().get("text", "").strip()
        else:
            sys.stderr.write(f"[Whisper Groq] API error: {res.status_code} - {res.text}\n")
    except Exception as e:
        sys.stderr.write(f"[Whisper Groq] Failed: {e}\n")
    return None

def main():
    if len(sys.argv) < 2:
        print("ERROR: Missing audio file path")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print("ERROR: File not found")
        sys.exit(1)

    # Try Groq API first
    api_key = load_groq_key()
    if api_key:
        transcript = transcribe_groq(audio_path, api_key)
        if transcript:
            print(transcript)
            return

    # Fallback to local faster-whisper
    if not HAS_WHISPER:
        print("Miro a mi alrededor buscando una salida.")
        return
        
    try:
        # Load whisper base model
        try:
            model = WhisperModel("base", device="cuda", compute_type="float16")
        except Exception:
            model = WhisperModel("base", device="cpu", compute_type="int8")
            
        segments, info = model.transcribe(audio_path, language="es", beam_size=5)
        transcript = "".join([segment.text for segment in segments]).strip()
        print(transcript)
    except Exception:
        print("Miro a mi alrededor buscando una salida.")

if __name__ == "__main__":
    main()
