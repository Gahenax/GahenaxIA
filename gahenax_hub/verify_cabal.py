import sys
import os

# Ensure the hub directory is in the path
sys.path.append(os.path.join(os.getcwd(), "gahenax_hub"))

from cabal_engine import build_default_engine, NodeName, DecisionStatus

def test_engine():
    print("Testing Cabalistic Engine...")
    engine = build_default_engine()
    state = engine.run(
        raw_input="Test high-level architecture integration.",
        objective="verify_operational_v1",
        constraints=["fast", "reliable"]
    )
    
    assert state.intent is not None
    assert state.intent.objective == "verify_operational_v1"
    assert state.validation is not None
    assert state.validation.status == DecisionStatus.PASSED
    assert state.response is not None
    assert "Objective: verify_operational_v1" in state.response.text
    
    print("Engine Test: PASSED")
    print(f"Run ID: {state.run_id}")
    print(f"Trace events: {len(state.trace)}")

def test_api_import():
    print("\nTesting API Imports...")
    try:
        from api import app
        print("API Import: PASSED")
    except ImportError as e:
        print(f"API Import: FAILED -> {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_engine()
    test_api_import()
