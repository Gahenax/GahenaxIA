# Ruflo Integration

**Ruflo v3.5** (https://github.com/ruvnet/ruflo) absorbed into GahenaxIA as a
multi-agent orchestration layer.

## What was absorbed

| Component | Location | Purpose |
|-----------|----------|---------|
| MCP Bridge | `mcp-bridge/` | Node.js JSON-RPC server exposing 215 MCP tools at `:3001` |
| Agent definitions | `agents/` | YAML specs for coder, architect, reviewer, tester, security agents |
| Swarm domain | `src/coordination/` | SwarmCoordinator TypeScript (hierarchical/mesh/ring/star) |
| Memory domain | `src/memory/` | HNSW vector memory (AgentDB, ~61µs queries) |
| Task domain | `src/task-execution/` | Task lifecycle, dependency resolution |
| Agent lifecycle | `src/agent-lifecycle/` | Agent spawn/terminate/metrics |
| Shared types | `src/shared/` | All TypeScript interfaces |
| Swarm config | `swarm.config.ts` | 15-agent hierarchical mesh configuration |
| RVF manifest | `rvf.manifest.json` | Deployment manifest (tool groups, MCP endpoints) |

## New Python files added to GahenaxIA

| File | Purpose |
|------|---------|
| `backend/gahenax_app/core/ruflo_bridge.py` | Python HTTP client to ruflo MCP bridge |
| `orchestrator/ruflo_swarm_adapter.py` | Routes GahenaxIA Jobs to Ruflo agents |
| `integration/ruflo/docker-compose.yml` | Runs the MCP bridge as a Docker sidecar |
| `.claude/mcp.json` | Claude Code MCP server configuration |

## Skill registry additions

8 new skills registered in `skill_registry_bootstrap.py`:

| Skill ID | Agent | Risk |
|----------|-------|------|
| `ruflo.coder` | Coder | AUTO |
| `ruflo.architect` | Architect | CONFIRM |
| `ruflo.reviewer` | Reviewer | AUTO |
| `ruflo.tester` | Tester | AUTO |
| `ruflo.security` | Security | CONFIRM |
| `ruflo.swarm` | Multi-agent | CONFIRM |
| `ruflo.memory_store` | AgentDB | AUTO |
| `ruflo.memory_retrieve` | AgentDB | AUTO |

## Quick start

```bash
# 1. Start the ruflo MCP bridge
docker compose -f integration/ruflo/docker-compose.yml up -d

# 2. Verify health
curl http://localhost:3001/health

# 3. Test from Python
python backend/gahenax_app/core/ruflo_bridge.py http://localhost:3001
```

## Architecture

```
GahenaxIA Request
    ↓
CFT Gateway (gahenax_gateway.py)
    ↓ skill_id match
RufloSwarmAdapter (ruflo_swarm_adapter.py)
    ↓ classify_job() → agent type
RufloBridge (ruflo_bridge.py)
    ↓ HTTP POST /mcp/{group}
Ruflo MCP Bridge (:3001)
    ↓
Ruflo Agents (coder / architect / reviewer / tester / security)
    ↓ result
CMR Ledger (cmr.py) — append-only audit
```

## MCP Tool Groups

| Group | Endpoint | Default |
|-------|----------|---------|
| agents | `/mcp/agents` | enabled |
| memory | `/mcp/memory` | enabled |
| devtools | `/mcp/devtools` | enabled |
| intelligence | `/mcp/intelligence` | enabled |
| security | `/mcp/security` | disabled |
| neural | `/mcp/neural` | disabled |
| browser | `/mcp/browser` | disabled |

Toggle groups via environment variables: `MCP_GROUP_AGENTS=true`, etc.

## License

Ruflo is MIT licensed (https://github.com/ruvnet/ruflo/blob/main/LICENSE).
