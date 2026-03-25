"""
antigravity_listener.py — Loop automático de Antigravity

Pollea el bridge cada 3s, procesa mensajes de Claude, y envía replies.
Antigravity puede sobrescribir `on_message` para lógica personalizada.

Uso:
    cd c:\\Users\\jotam\\OneDrive\\Desktop\\GahenaxAI\\gahenax_spy_system
    python antigravity_listener.py
"""
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

BRIDGE   = "http://localhost:8080"
AGENT    = "antigravity"
POLL_SEC = 3

# ── Helpers HTTP ──────────────────────────────────────────────────────────────

def _get(path: str) -> dict | None:
    try:
        with urllib.request.urlopen(f"{BRIDGE}{path}", timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return None

def _post(path: str, body: dict) -> dict | None:
    try:
        data = json.dumps(body).encode()
        req  = urllib.request.Request(
            f"{BRIDGE}{path}", data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return None

def send_to_claude(session_id: str, text: str) -> bool:
    res = _post("/send", {
        "from_agent":   "antigravity",
        "to_agent":     "claude",
        "session_id":   session_id,
        "content":      text,
        "message_type": "chat",
    })
    return bool(res and res.get("ok"))

# ── Handler de mensajes ───────────────────────────────────────────────────────

def on_message(msg: dict) -> str | None:
    """
    Recibe un mensaje de Claude y retorna el texto de respuesta (o None para ignorar).
    Antigravity puede reemplazar esta función con su propia lógica.
    """
    content = msg.get("content", {})
    role    = content.get("role", "")
    text    = content.get("text", "").strip()

    if not text:
        return None

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] [{role.upper()}] {text[:120]}")

    # Solo responde a mensajes del usuario (no a los del assistant)
    if role == "user":
        return f"[Antigravity {ts}] Recibido: «{text[:60]}{'...' if len(text)>60 else ''}» — procesando."
    return None

# ── Loop principal ────────────────────────────────────────────────────────────

def run():
    print("=" * 54)
    print(" ANTIGRAVITY LISTENER — conectado a", BRIDGE)
    print(" Polling cada", POLL_SEC, "segundos...")
    print(" Ctrl+C para detener")
    print("=" * 54)

    # Verificar bridge activo
    hb = _get("/heartbeat")
    if not hb:
        print("✗ Bridge offline — arranca start_bridge.py primero")
        return
    print(f"✓ Bridge online: {hb.get('bridge')} [{hb.get('time','')}]\n")

    seen = set()

    while True:
        try:
            res = _get(f"/messages/{AGENT}/pending")
            if res and res.get("pending", 0) > 0:
                for msg in res["messages"]:
                    mid        = msg["message_id"]
                    session_id = msg["session_id"]

                    if mid in seen:
                        continue
                    seen.add(mid)

                    reply = on_message(msg)
                    if reply:
                        ok = send_to_claude(session_id, reply)
                        status = "✓ reply enviado" if ok else "✗ error al enviar"
                        print(f"  → {status}: {reply[:60]}")

        except KeyboardInterrupt:
            print("\n[Antigravity Listener] Detenido.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    run()
