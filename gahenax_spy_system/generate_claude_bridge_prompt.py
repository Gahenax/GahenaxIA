import json
import os
import glob
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATS_DIR = os.path.join(BASE_DIR, "..", "spy_data", "claude_chats")


def get_latest_chat():
    files = glob.glob(os.path.join(CHATS_DIR, "chat_*.json"))
    if not files:
        return None

    latest_file = max(files, key=os.path.getmtime)

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return {
            "error": f"Failed to load chat file: {e}",
            "messages": []
        }


def normalize_content(msg):
    raw_content = msg.get("text", msg.get("content", "..."))
    if isinstance(raw_content, str):
        return raw_content.strip()
    try:
        return json.dumps(raw_content, ensure_ascii=False)
    except Exception:
        return "..."


def generate_prompt():
    chat_data = get_latest_chat()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    has_messages = bool(chat_data and chat_data.get("messages"))

    prompt = f"""
# GAHENAX BRIDGE PROTOCOL — EIGHTH WAVE
Timestamp: {timestamp}
Status: Interconnected with Local Gahenax Environment (Port 8080)

## CONTEXT SYNC
Estás operando en una sesión sincronizada con el agente local de Gahenax.
He detectado el siguiente estado previo de nuestra conversación:
{"Last Messages Captured:" if has_messages else "--- NO CHAT HISTORY DETECTED ---"}
"""

    if chat_data and chat_data.get("error"):
        prompt += f"\n[WARNING] {chat_data['error']}\n"

    if has_messages:
        for msg in chat_data["messages"][-5:]:
            role = str(msg.get("role", "unknown")).upper()
            content = normalize_content(msg)
            safe_excerpt = content[:200].replace("\n", " ")
            prompt += f"- **{role}**: {safe_excerpt}...\n"

    prompt += """
## INSTRUCTIONS FOR CLAUDE
1. Always Sync: Si ves el widget "GAHENAX HUB", asume que tus respuestas están siendo monitoreadas por el orquestador local.
2. Collaborative Mode: Estás trabajando junto a Antigravity. Si Antigravity propone un cambio en el sistema de archivos, puedes referenciarlo aquí.
3. Signal Protocol: Si necesitas que el agente local ejecute algo pesado (JULES_ORDER), indícalo claramente con el tag [JULES_COMPUTE].

## CURRENT REPO CONTEXT
Estamos trabajando en el ecosistema GahenaxAI.
- Project: Claude Collaboration Bridge
- Local Bridge: gahenax_spy_system/claude_bridge.py
- Implant: gahenax_spy_system/claude_implant.user.js

¿Entendido? Confirma conexión con "SISTEMA GAHENAX INTERCONECTADO" para proceder.
"""
    return prompt.strip()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" GAHENAX PROMPT GENERATOR — BRIDGE STABILIZER ")
    print("=" * 60)
    print("\nCOPIA Y PEGA EL SIGUIENTE TEXTO EN TU CHAT DE CLAUDE:\n")
    print("-" * 60)
    print(generate_prompt())
    print("-" * 60)
