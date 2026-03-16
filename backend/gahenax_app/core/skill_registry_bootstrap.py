"""
skill_registry_bootstrap.py
============================
Canonical SkillRegistry — 3 example skills, graduated by risk.

  INFORMATIONAL  → AUTO     (no side effects, safe)
  PRODUCTIVE     → CONFIRM  (writes to filesystem)
  SYSTEMIC       → LOCKED   (modifies CMR ledger schema)

All skills start enabled but can be quarantined by the circuit breaker.
Side-effecting skills start with dry_run_default=False (production ready)
but callers can override with dry_run=True.
"""

from __future__ import annotations

from gahenax_app.core.gahenax_gateway import (
    SkillSpec, SkillRegistry, RiskLevel, RollbackPolicy
)


def build_registry() -> SkillRegistry:
    registry = SkillRegistry()

    # ── SKILL 1: INFORMATIONAL (AUTO) ────────────────────────────────────
    # Safe to auto-execute. Read-only. No side effects.
    # Example: answer a governance question from the CMR ledger.
    registry.register(SkillSpec(
        skill_id="gahenax.query_ledger",
        intent_tags=["audit", "query", "ledger", "status", "stats"],
        description="Read-only query of the CMR ledger. Returns stats and latest hash.",
        risk_level=RiskLevel.AUTO,
        required_inputs=["window_n"],
        output_schema="LedgerQueryResult",
        ua_cost_estimate=0.5,
        timeout_ms=2000,
        idempotent=True,
        side_effects=[],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # ── SKILL 2: PRODUCTIVE (CONFIRM) ────────────────────────────────────
    # Writes a snapshot JSON to disk. Requires user confirmation.
    # Idempotent: same inputs → same file (deterministic hash).
    registry.register(SkillSpec(
        skill_id="gahenax.generate_snapshot",
        intent_tags=["snapshot", "seal", "export", "record", "sign"],
        description="Generates a signed CMR snapshot JSON and writes it to snapshots/.",
        risk_level=RiskLevel.CONFIRM,
        required_inputs=["snapshot_label"],
        output_schema="Snapshot",
        ua_cost_estimate=1.5,
        timeout_ms=5000,
        idempotent=True,
        side_effects=["file:write"],
        rollback=RollbackPolicy.BEST_EFFORT,
        enabled=True,
        dry_run_default=False,
    ))

    # ── SKILL 3: SYSTEMIC / READ-ONLY START (LOCKED) ─────────────────────
    # Alters the CMR database schema (e.g. adds columns).
    # Starts LOCKED. Only executable in AUDIT mode + risk_override=True.
    # Rollback REQUIRED — the system must be able to undo.
    registry.register(SkillSpec(
        skill_id="gahenax.migrate_ledger_schema",
        intent_tags=["migration", "schema", "db", "upgrade", "alter"],
        description="Applies a migration to the CMR SQLite schema. Irreversible without backup.",
        risk_level=RiskLevel.LOCKED,
        required_inputs=["migration_id", "sql_patch"],
        output_schema="MigrationResult",
        ua_cost_estimate=4.0,
        timeout_ms=15000,
        idempotent=True,  # migration_id prevents double-application
        side_effects=["db:write", "db:schema"],
        rollback=RollbackPolicy.REQUIRED,
        enabled=True,
        dry_run_default=True,   # Always starts simulated
    ))

    # ── RUFLO INTEGRATION SKILLS ──────────────────────────────────────────
    # These skills delegate to Ruflo's multi-agent orchestration platform
    # via the RufloBridge (HTTP → ruflo MCP bridge at :3001).
    # Source: https://github.com/ruvnet/ruflo

    # RUFLO SKILL 1: Code generation / refactoring via Coder agent (AUTO)
    registry.register(SkillSpec(
        skill_id="ruflo.coder",
        intent_tags=["code", "implement", "refactor", "debug", "function", "module", "class"],
        description=(
            "Delegates code-generation, refactoring, or debugging tasks to Ruflo's "
            "specialized Coder agent (flash-attention + token-reduction optimized)."
        ),
        risk_level=RiskLevel.AUTO,
        required_inputs=["task"],
        output_schema="RufloCoderResult",
        ua_cost_estimate=2.0,
        timeout_ms=30000,
        idempotent=False,
        side_effects=["external:ruflo"],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 2: System design via Architect agent (CONFIRM)
    registry.register(SkillSpec(
        skill_id="ruflo.architect",
        intent_tags=["design", "architect", "api", "schema", "system", "structure", "ddd"],
        description=(
            "Delegates system-design and API-design tasks to Ruflo's Architect agent "
            "(context-caching + memory-persistence optimized)."
        ),
        risk_level=RiskLevel.CONFIRM,
        required_inputs=["task"],
        output_schema="RufloArchitectResult",
        ua_cost_estimate=3.0,
        timeout_ms=30000,
        idempotent=False,
        side_effects=["external:ruflo"],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 3: Code review via Reviewer agent (AUTO)
    registry.register(SkillSpec(
        skill_id="ruflo.reviewer",
        intent_tags=["review", "lint", "quality", "style", "convention", "best-practice", "pr"],
        description=(
            "Runs a code review via Ruflo's Reviewer agent — checks quality gates, "
            "best-practices, and style conventions."
        ),
        risk_level=RiskLevel.AUTO,
        required_inputs=["task"],
        output_schema="RufloReviewResult",
        ua_cost_estimate=1.5,
        timeout_ms=20000,
        idempotent=True,
        side_effects=["external:ruflo"],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 4: Test generation via Tester agent (AUTO)
    registry.register(SkillSpec(
        skill_id="ruflo.tester",
        intent_tags=["test", "coverage", "assert", "unit", "integration", "spec", "tdd"],
        description=(
            "Generates tests and coverage analysis via Ruflo's Tester agent."
        ),
        risk_level=RiskLevel.AUTO,
        required_inputs=["task"],
        output_schema="RufloTesterResult",
        ua_cost_estimate=2.0,
        timeout_ms=20000,
        idempotent=False,
        side_effects=["external:ruflo"],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 5: Security scan via Security-Architect agent (CONFIRM)
    registry.register(SkillSpec(
        skill_id="ruflo.security",
        intent_tags=["security", "vuln", "cve", "pentest", "threat", "injection", "audit", "harden"],
        description=(
            "Runs vulnerability scanning and CVE remediation via Ruflo's "
            "Security-Architect agent."
        ),
        risk_level=RiskLevel.CONFIRM,
        required_inputs=["task"],
        output_schema="RufloSecurityResult",
        ua_cost_estimate=3.5,
        timeout_ms=45000,
        idempotent=True,
        side_effects=["external:ruflo"],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 6: Multi-agent swarm coordination (CONFIRM)
    registry.register(SkillSpec(
        skill_id="ruflo.swarm",
        intent_tags=["swarm", "multi-agent", "parallel", "coordinate", "orchestrate", "hive"],
        description=(
            "Launches a multi-agent Ruflo swarm (hierarchical / mesh / ring / star) "
            "to tackle complex tasks requiring concurrent agent cooperation."
        ),
        risk_level=RiskLevel.CONFIRM,
        required_inputs=["tasks", "topology"],
        output_schema="RufloSwarmResult",
        ua_cost_estimate=6.0,
        timeout_ms=120000,
        idempotent=False,
        side_effects=["external:ruflo", "network:spawn"],
        rollback=RollbackPolicy.BEST_EFFORT,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 7: Vector memory store (AUTO)
    registry.register(SkillSpec(
        skill_id="ruflo.memory_store",
        intent_tags=["memory", "store", "persist", "embed", "knowledge", "agentdb"],
        description=(
            "Persists content in Ruflo's HNSW vector memory (AgentDB) for semantic "
            "retrieval across agent sessions."
        ),
        risk_level=RiskLevel.AUTO,
        required_inputs=["key", "content", "agent_id"],
        output_schema="RufloMemoryStoreResult",
        ua_cost_estimate=0.8,
        timeout_ms=5000,
        idempotent=True,
        side_effects=["external:ruflo", "db:write"],
        rollback=RollbackPolicy.BEST_EFFORT,
        enabled=True,
        dry_run_default=False,
    ))

    # RUFLO SKILL 8: Vector memory retrieval (AUTO)
    registry.register(SkillSpec(
        skill_id="ruflo.memory_retrieve",
        intent_tags=["memory", "retrieve", "search", "semantic", "recall", "lookup"],
        description=(
            "Semantic search over Ruflo's HNSW vector memory (~61µs per query)."
        ),
        risk_level=RiskLevel.AUTO,
        required_inputs=["query", "agent_id"],
        output_schema="RufloMemoryRetrieveResult",
        ua_cost_estimate=0.5,
        timeout_ms=3000,
        idempotent=True,
        side_effects=[],
        rollback=RollbackPolicy.NONE,
        enabled=True,
        dry_run_default=False,
    ))

    return registry


if __name__ == "__main__":
    reg = build_registry()
    print("=== SKILL REGISTRY (v1.1.1) ===\n")
    print(reg.summary())

    print("\n=== SPEC HASHES (tamper-evident) ===")
    for s in reg.all():
        print(f"  {s.skill_id:<40} {s.spec_hash()}")
