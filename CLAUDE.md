# GahenaxAI — Claude Code Configuration

> **GahenaxAI v1.2** — Gahenax Core + Antigravity Bridge + Ruflo-adapted Swarm
> Stack: Python / FastAPI / Flask / SQLite / Gemini API
> Bridge: Claude.ai ↔ Antigravity (Gemini CLI) bidireccional en puerto 8080

---

## Behavioral Rules (Always Enforced)

- Do what has been asked; nothing more, nothing less
- ALWAYS read a file before editing it
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing an existing file to creating a new one
- NEVER commit secrets, credentials, or .env files
- NEVER push to main/master — always use feature branches
- Active branch: `claude/gahenax-claude-bridge-AEO6l`

---

## Project Structure

```
GahenaxAI/
├── backend/                  # FastAPI — Gahenax Core API (port 8080)
│   ├── main.py               # Entry point
│   ├── requirements.txt
│   └── gahenax_app/
│       ├── api/
│       │   ├── gahenax_api.py    # /api/gahenax/infer
│       │   └── bridge_api.py     # bidirectional bridge endpoints
│       ├── core/
│       │   ├── gahenax_engine.py # GahenaxGovernor, UA budget
│       │   ├── gahenax_llm_bridge.py  # Gemini API
│       │   └── cmr.py            # Canonical Measurement Recorder
│       └── schemas/
│           └── gahenax_contract.py
├── gahenax_spy_system/       # Bridge layer
│   ├── claude_bridge.py      # Flask v2.0 — canonical bridge server
│   ├── start_bridge.py       # Launcher
│   ├── antigravity_listener.py  # Auto-poll loop for Antigravity
│   └── userscripts/
│       └── gahenax_claude_bridge.user.js  # Tampermonkey v1.2
├── agents/                   # Agent definitions (Ruflo-adapted)
│   ├── orchestrator.yaml
│   ├── coder.yaml
│   ├── architect.yaml
│   ├── tester.yaml
│   └── reviewer.yaml
├── orchestrator/             # Multi-worker job system
├── benchmarks/               # FCD benchmarks
├── snapshots/                # Immutable state snapshots
├── spy_data/claude_chats/    # Synced Claude.ai sessions
├── Dockerfile
├── docker-compose.yml
└── CLAUDE.md                 # This file
```

---

## Bridge API (port 8080)

| Endpoint | Dirección | Quién lo usa |
|---|---|---|
| `POST /telemetry` | Claude.ai → Bridge | Userscript |
| `GET /messages/antigravity/pending` | Bridge → Antigravity | antigravity_listener.py |
| `POST /send` | Antigravity → Bridge → Claude | Antigravity |
| `GET /messages/claude/pending` | Bridge → Claude.ai | Userscript (poll 4s) |
| `GET /state/<session_id>` | Snapshot completo | Cualquier agente |
| `GET /heartbeat` | Ping | Cualquier agente |

---

## Agent Swarm (Ruflo-adapted)

Topología jerárquica:
```
Antigravity (Gemini CLI) — Orquestador principal
    └── orchestrator agent
            ├── architect   (system design, UA budget: 12)
            ├── coder        (code generation, UA budget: 8)
            ├── tester       (test + validation, UA budget: 6)
            └── reviewer     (audit + h-rigidity, UA budget: 10)
```

Routing de tiers:
- **Tier 1**: Tasks simples → sin LLM (mock determinístico)
- **Tier 2**: Complejidad < 30% → Gemini Flash (Haiku-equivalent)
- **Tier 3**: Complejidad > 30% → Gemini Pro (Sonnet-equivalent)

Arrancar swarm:
```bash
python gahenax_swarm.py --task "descripción" --agents coder,tester
```

---

## Comandos clave

```bash
# Bridge (Flask v2.0)
cd gahenax_spy_system && python start_bridge.py

# Bridge (Docker)
docker-compose up --build

# Antigravity listener
python gahenax_spy_system/antigravity_listener.py

# Swarm
python gahenax_swarm.py --task "..." --agents all

# Benchmark
python gahenax_ops.py bench

# Audit console
streamlit run rigor_console.py
```

---

## Contratos y métricas

- **UA (Athena Units)**: presupuesto de esfuerzo computacional por agente
- **H-Rigidity**: estabilidad estructural (verde < 1e-12, rojo = 1.0)
- **CMR Ledger**: `ua_ledger.sqlite` — registro inmutable con hash chaining
- **FCD Gates A1–A4**: entropy reduction, schema adherence, rigidity, UA budget

---

## Concurrencia

- Batch ALL file reads en UN solo mensaje
- Batch ALL tool calls independientes en UN solo mensaje
- Usar `asyncio` en FastAPI para operaciones I/O
- El swarm ejecuta agentes en paralelo via `multiprocessing`
