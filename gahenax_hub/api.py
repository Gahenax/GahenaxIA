from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import uuid
import json
import os

from cabal_engine import build_default_engine, CognitiveState, Intent, DecisionStatus, NodeName, YesodNode

app = FastAPI(title="Gahenax Cabal AI v1 Operativa")

# --- Models ---
class InferRequest(BaseModel):
    query: str
    objective: Optional[str] = "general_reasoning"
    constraints: Optional[List[str]] = []

class InferResponse(BaseModel):
    run_id: str
    text: str
    decision_status: str
    trace_summary: List[Dict[str, Any]]

# --- Persistent Memory (Episode) ---
MEMORY_FILE = "gahenax_hub/sessions/episode_memory.json"

def save_episode(state: CognitiveState):
    os.makedirs("gahenax_hub/sessions", exist_ok=True)
    history = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Simple serialization of trace
    serialized_trace = [
        {"ts": e.ts, "node": e.node, "action": e.action, "detail": str(e.detail)}
        for e in state.trace
    ]
    
    history.append({
        "run_id": state.run_id,
        "objective": state.intent.objective if state.intent else "unknown",
        "result": state.response.text if state.response else "no_response",
        "trace": serialized_trace
    })
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# --- Endpoints ---
@app.post("/infer", response_model=InferResponse)
async def infer(request: InferRequest):
    engine = build_default_engine()
    
    # Run the engine
    try:
        state = engine.run(
            raw_input=request.query,
            objective=request.objective or "general_reasoning",
            constraints=request.constraints
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not state.response:
        raise HTTPException(status_code=500, detail="Engine failed to generate a response.")
    
    # Save to history (JSON for summary, SQLite is handled by YesodNode)
    save_episode(state)
    
    return InferResponse(
        run_id=state.run_id,
        text=state.response.text,
        decision_status=state.validation.status.value if state.validation else "unknown",
        trace_summary=[
            {
                "ts": e.ts, 
                "node": e.node, 
                "action": e.action, 
                "spectral_echo": state.spectral_echo_detected if e.node == "gevurah" else False
            }
            for e in state.trace
        ]
    )

@app.get("/health")
async def health():
    return {"status": "alive", "engine": "Cabal-v1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
