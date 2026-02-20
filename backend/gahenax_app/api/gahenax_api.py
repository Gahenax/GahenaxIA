from fastapi import APIRouter, HTTPException
from gahenax_app.schemas.gahenax_contract import GahenaxRequest, GahenaxOutputSchema
from gahenax_app.core.gahenax_engine import GahenaxGovernor, RenderProfile
from typing import Dict, Any

router = APIRouter(prefix="/api/gahenax", tags=["Gahenax Core"])

# Persistent Governors (Mock Session Store)
GOVERNORS: Dict[str, GahenaxGovernor] = {}

@router.post("/infer", response_model=GahenaxOutputSchema)
async def infer(request: GahenaxRequest):
    """
    Main inference cycle for Gahenax Core.
    Uses LLL Lattice Reduction and P over NP (UA) Physics.
    """
    session_id = request.session_id
    
    if request.turn_index == 1:
        # Create a new governed instance
        gov = GahenaxGovernor(budget_ua=request.ua_budget)
        session_id = gov.session_id
        GOVERNORS[session_id] = gov
    else:
        if not session_id or session_id not in GOVERNORS:
            raise HTTPException(status_code=400, detail="SESSION_STALL: Inactive or expired UA context.")
        gov = GOVERNORS[session_id]
        gov.turn = request.turn_index

    # Run the cycle
    try:
        profile = RenderProfile(request.render_profile)
    except ValueError:
        profile = RenderProfile.DAILY

    output = gov.run_inference_cycle(request.text, request.context_answers)
    
    # In a real implementation, we'd convert the dataclass to the schema
    # Here we return the dictionary representation
    return output.to_dict()

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
