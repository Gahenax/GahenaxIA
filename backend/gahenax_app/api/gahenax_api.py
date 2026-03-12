from __future__ import annotations

import os
import time
import threading
from typing import Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from gahenax_app.schemas.gahenax_contract import GahenaxRequest, GahenaxOutputSchema
from gahenax_app.core.gahenax_engine import (
    GahenaxGovernor, RenderProfile, EngineMode,
    compute_cni_fingerprint, H_RIGIDITY_PERFECT,
)
from gahenax_app.core.cmr import CMR, CMRConfig, utc_now

# ─────────────────────────── versioning ────────────────────────────
PROMPT_VERSION   = "engine_v1.1.md#GEMv1"
ENGINE_VERSION   = "GahenaxCore-v1.1.1"
CONTRACT_VERSION = "GahenaxOutput-v1.0"

router = APIRouter(prefix="/api/gahenax", tags=["Gahenax Core"])

# ─────────────────────────── CMR setup ─────────────────────────────
_db_path = os.environ.get("GAHENAX_DB_PATH", os.path.join(os.getcwd(), "ua_ledger.sqlite"))
CMR_INST = CMR(CMRConfig(db_path=_db_path))

# ─────────────────────── rate limiter (simple) ─────────────────────
_RATE_LIMIT      = int(os.environ.get("GAHENAX_RATE_LIMIT", "60"))   # req/min per IP
_RATE_WINDOW_S   = 60
_rate_counts: Dict[str, list] = {}
_rate_lock = threading.Lock()

def _check_rate_limit(client_ip: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        ts_list = _rate_counts.setdefault(client_ip, [])
        _rate_counts[client_ip] = [t for t in ts_list if now - t < _RATE_WINDOW_S]
        if len(_rate_counts[client_ip]) >= _RATE_LIMIT:
            return False
        _rate_counts[client_ip].append(now)
        return True

# ─────────────────── session store with TTL cleanup ────────────────
_SESSION_TTL_S   = int(os.environ.get("GAHENAX_SESSION_TTL", "3600"))  # 1 h default
_governors: Dict[str, GahenaxGovernor] = {}
_session_ts: Dict[str, float] = {}
_session_lock = threading.Lock()

def _get_or_create_governor(
    session_id: str | None,
    turn_index: int,
    budget_ua: float | None,
    mode: EngineMode,
) -> tuple[GahenaxGovernor, str]:
    now = time.monotonic()
    with _session_lock:
        # Evict stale sessions
        stale = [sid for sid, ts in _session_ts.items() if now - ts > _SESSION_TTL_S]
        for sid in stale:
            _governors.pop(sid, None)
            _session_ts.pop(sid, None)

        if turn_index == 1 or not session_id or session_id not in _governors:
            gov = GahenaxGovernor(budget_ua=budget_ua, mode=mode)
            sid = gov.session_id
            _governors[sid] = gov
            _session_ts[sid] = now
            return gov, sid

        gov = _governors[session_id]
        gov.turn = turn_index
        _session_ts[session_id] = now
        return gov, session_id


# ────────────────────────── endpoints ──────────────────────────────

@router.post("/infer", response_model=GahenaxOutputSchema)
async def infer(request: GahenaxRequest, req: Request):
    """Main inference cycle, logged to the Canonical Measurement Recorder (CMR)."""
    client_ip = req.client.host if req.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    t0 = time.perf_counter()
    ts0 = utc_now()

    input_fingerprint = compute_cni_fingerprint(request.model_dump())

    try:
        mode = EngineMode(request.mode)
    except ValueError:
        mode = EngineMode.EVERYDAY

    gov, session_id = _get_or_create_governor(
        request.session_id, request.turn_index, request.ua_budget, mode
    )

    try:
        profile = RenderProfile(request.render_profile)
    except ValueError:
        profile = RenderProfile.DAILY

    output_obj = gov.run_inference_cycle(request.text, request.context_answers)

    ts1 = utc_now()
    latency_ms = (time.perf_counter() - t0) * 1000.0

    CMR_INST.record_run(
        user_id="default_user",
        session_id=session_id,
        request_id=f"REQ_{int(time.time() * 1000)}",
        engine_version=ENGINE_VERSION,
        contract_version=CONTRACT_VERSION,
        prompt_version=PROMPT_VERSION,
        input_fingerprint=input_fingerprint,
        seed=0,
        latency_ms=latency_ms,
        contract_valid=True,
        contract_fail_reason=None,
        ua_spend=int(gov.ua.spent),
        delta_s=float(gov.ua.efficiency * gov.ua.spent),
        delta_s_per_ua=float(gov.ua.efficiency),
        h_rigidity=H_RIGIDITY_PERFECT,
        work_units=int(gov.ua.spent * 2),
        timestamp_start=ts0,
        timestamp_end=ts1,
        git_commit=os.getenv("GIT_COMMIT"),
        host_id=os.getenv("HOSTNAME"),
    )

    return output_obj.to_dict()


@router.get("/status/{session_id}")
async def get_status(session_id: str):
    with _session_lock:
        gov = _governors.get(session_id)
    if gov is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "session_id": gov.session_id,
        "turn": gov.turn,
        "ua_status": {
            "spent": gov.ua.spent,
            "budget": gov.ua.budget,
            "efficiency": gov.ua.efficiency,
        },
    }
