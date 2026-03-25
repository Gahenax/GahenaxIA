from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gahenax_app.api.gahenax_api import router
from gahenax_app.api.bridge_api import bridge_router
import uvicorn

app = FastAPI(
    title="Gahenax Core + Antigravity Bridge",
    version="1.2.0",
    description="Gahenax inference engine + bidirectional Claude ↔ Antigravity message bus",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "http://localhost", "http://127.0.0.1"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router)
app.include_router(bridge_router)


@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "system": "Gahenax Core v1.2.0",
        "bridge": "Antigravity Bridge v1.2",
        "endpoints": {
            "gahenax_infer": "POST /api/gahenax/infer",
            "heartbeat":     "GET  /heartbeat",
            "telemetry_in":  "POST /telemetry",
            "send":          "POST /send",
            "poll_claude":   "GET  /messages/claude/pending",
            "poll_antigrav": "GET  /messages/antigravity/pending",
            "state":         "GET  /state/{session_id}",
            "sessions":      "GET  /sessions",
        },
    }


BANNER = """
==================================================
 GAHENAX CLAUDE BRIDGE — Port 8080
 POST /telemetry               — recibir mensajes (userscript)
 POST /send                    — Antigravity → Claude
 GET  /messages/{agent}/pending — poll mensajes pendientes
 GET  /state/<id>              — leer sesion
 GET  /heartbeat               — ping
 GET  /sessions                — listar sesiones activas
==================================================
"""

if __name__ == "__main__":
    print(BANNER)
    uvicorn.run(app, host="0.0.0.0", port=8080)
