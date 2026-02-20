from fastapi import APIRouter, HTTPException
from gahenax_app.schemas.gahenax_contract import GahenaxRequest, GahenaxOutputSchema
from gahenax_app.core.gahenax_engine import GahenaxGovernor, RenderProfile
from gahenax_app.core.telemetry import UALedgerDB, LedgerRecord, compute_evidence_hash
from typing import Dict, Any
import time
from datetime import datetime, timezone
import os

router = APIRouter(prefix="/api/gahenax", tags=["Gahenax Core"])

# CRM Persistence Layer
LEDGER = UALedgerDB(os.path.join(os.getcwd(), "ua_ledger.sqlite"))

# Persistent Governors (Mock Session Store)
GOVERNORS: Dict[str, GahenaxGovernor] = {}

@router.post("/infer", response_model=GahenaxOutputSchema)
async def infer(request: GahenaxRequest):
    """
    Main inference cycle for Gahenax Core.
    Logs every interaction to the Rigor Console CRM.
    """
    start_time = time.perf_counter()
    session_id = request.session_id
    
    if request.turn_index == 1 or not session_id:
        # Create a new governed instance
        gov = GahenaxGovernor(budget_ua=request.ua_budget)
        session_id = gov.session_id
        GOVERNORS[session_id] = gov
    else:
        if session_id not in GOVERNORS:
            # Fallback or strict error
            gov = GahenaxGovernor(budget_ua=request.ua_budget)
            GOVERNORS[session_id] = gov
        else:
            gov = GOVERNORS[session_id]
            gov.turn = request.turn_index

    # Run the cycle
    try:
        profile = RenderProfile(request.render_profile)
    except ValueError:
        profile = RenderProfile.DAILY

    output_obj = gov.run_inference_cycle(request.text, request.context_answers)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # --- CRM LOGGING (FCD-1.0) ---
    payload = {
        "case_id": f"REQ_{int(time.time())}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine_version": "GahenaxCore-v1.0",
        "contract_version": "GahenaxOutput-v1.0",
        "seed": 0,
        "latency_ms": latency_ms,
        "contract_valid": True, # Pydantic response_model ensures this
        "ua_spend": int(gov.ua.spent),
        "delta_s": float(gov.ua.efficiency * gov.ua.spent),
        "delta_s_per_ua": float(gov.ua.efficiency),
        "h_rigidity": 1e-15,
        "work_units": int(gov.ua.spent * 2),
        "evidence_hash": ""
    }
    payload["evidence_hash"] = compute_evidence_hash(payload)
    LEDGER.append(
        user_id="default_user",
        session_id=session_id,
        request_id=payload["case_id"],
        rec=LedgerRecord(**payload)
    )
    # -----------------------------

    return output_obj.to_dict()

@router.get("/status/{session_id}")
async def get_status(session_id: str):
    if session_id not in GOVERNORS:
        raise HTTPException(status_code=404, detail="Session not found.")
    gov = GOVERNORS[session_id]
    return {
        "session_id": gov.session_id,
        "turn": gov.turn,
        "ua_status": {
            "spent": gov.ua.spent,
            "budget": gov.ua.budget,
            "efficiency": gov.ua.efficiency
        }
    }
