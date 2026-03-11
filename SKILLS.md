# SKILLS — Gahenax Execution Contract Taxonomy

> **Sistema**: Gahenax Core v1.1.1
> **Gateway**: CFT v1 (Contract-First Execution)
> **Paradigma**: No evidence, no execution. Fail-closed by default.
> **Versión del documento**: 1.0.0

---

## 1. Qué es un Skill

Un **Skill** es la unidad ejecutable mínima del sistema Gahenax. No es una función libre —
es un **contrato declarado** que expone sus intenciones, costos y consecuencias antes de
correr una sola instrucción.

Todo skill existe dentro del `SkillRegistry` y solo puede ejecutarse a través del
`ExecutionGateway`. No hay atajos. No hay bypass. No hay narrativa.

```
Input Text / API Call
       │
       ▼
  [ ExecutionRequest ]  ← idempotency key obligatoria
       │
       ▼
  [ ExecutionGateway ]
       │
       ├─ Resolve skill in registry
       ├─ Circuit Breaker check
       ├─ Idempotency replay check
       ├─ Risk / Mode gate
       ├─ UA Budget gate
       ├─ CMR availability gate
       │
       ▼
  [ ToolRunner.run() ]  ← implementación real
       │
       ▼
  [ ExecutionResult ]   ← evidencia hash-sellada
       │
       ▼
  [ CMR Ledger ]        ← registro inmutable, append-only
```

---

## 2. Taxonomía de Riesgo (Risk Levels)

Cada skill declara su nivel de riesgo. El gateway lo hace cumplir sin excepción.

| Nivel     | Constante         | Ejecución          | Requisito de modo | Side effects    |
|-----------|-------------------|--------------------|-------------------|-----------------|
| Seguro    | `AUTO`            | Automática         | Cualquiera        | Ninguno         |
| Productivo| `CONFIRM`         | Requiere confirmación| Cualquiera      | Escritura local |
| Sistémico | `LOCKED`          | Solo en modo AUDIT | `AUDIT` + `risk_override=True` | DB schema / irreversible |

### Regla de oro

```
AUTO    → lee, nunca escribe
CONFIRM → escribe, pero es idempotente y reversible con best-effort
LOCKED  → altera estado global; rollback REQUIRED antes de aprobar
```

---

## 3. Anatomía de un SkillSpec

Cada skill se define mediante un `SkillSpec`. Todos los campos son contractuales —
no hay valores implícitos tolerados en producción.

```python
SkillSpec(
    skill_id          = "gahenax.<dominio>.<accion>",  # estable, never rename
    intent_tags       = ["tag1", "tag2"],               # para routing semántico
    description       = "Una oración. Sujeto + verbo + consecuencia.",
    risk_level        = RiskLevel.AUTO | CONFIRM | LOCKED,
    required_inputs   = ["campo1", "campo2"],           # validados pre-ejecución
    output_schema     = "NombreDelModeloPydantic",      # contrato de salida
    ua_cost_estimate  = 1.0,                            # Athena Units estimadas
    timeout_ms        = 5000,                           # hard timeout
    idempotent        = True,                           # mismo input → mismo output
    side_effects      = ["file:write", "db:write"],     # declarar todo
    rollback          = RollbackPolicy.NONE | BEST_EFFORT | REQUIRED,
    enabled           = True,
    dry_run_default   = False,                          # True = siempre simular primero
)
```

### Guía de `ua_cost_estimate`

| Rango UA | Tipo de operación típica                        |
|----------|-------------------------------------------------|
| 0.1–0.5  | Lectura de ledger, consulta de estado           |
| 0.5–2.0  | Generación de snapshot, escritura de archivo    |
| 2.0–5.0  | Llamada LLM, reducción lattice completa         |
| 5.0+     | Migración de schema, operaciones sistémicas     |

El budget por defecto en modo GEM (Everyday) es **6.0 UA**.
Si `ua_cost_estimate > ua_budget`, el gateway bloquea antes de ejecutar.

---

## 4. Catálogo Canónico de Skills (v1.1.1)

### SKILL-01 — `gahenax.query_ledger`

| Campo           | Valor                                                |
|-----------------|------------------------------------------------------|
| **Risk Level**  | `AUTO`                                               |
| **Intent Tags** | `audit`, `query`, `ledger`, `status`, `stats`        |
| **Description** | Read-only query of the CMR ledger. Returns stats and latest hash. |
| **Inputs**      | `window_n` (int) — número de registros a consultar   |
| **Output**      | `LedgerQueryResult`                                  |
| **UA Cost**     | 0.5                                                  |
| **Timeout**     | 2,000 ms                                             |
| **Side Effects**| Ninguno                                              |
| **Rollback**    | `NONE`                                               |
| **Idempotent**  | Sí                                                   |

**Cuándo usarlo**: Cuando necesitas verificar el estado del ledger CMR sin alterar ningún estado. Es el punto de entrada para auditorías livianas. No requiere confirmación del usuario.

**Flujo mínimo**:
```python
req = ExecutionRequest(
    request_id="audit-001",
    skill_id="gahenax.query_ledger",
    inputs={"window_n": 50},
    mode="GEM",
    ua_budget=6.0,
)
result = gateway.execute(req)
# result.status → OK
# result.outputs → {"records": [...], "latest_hash": "..."}
```

---

### SKILL-02 — `gahenax.generate_snapshot`

| Campo           | Valor                                                |
|-----------------|------------------------------------------------------|
| **Risk Level**  | `CONFIRM`                                            |
| **Intent Tags** | `snapshot`, `seal`, `export`, `record`, `sign`       |
| **Description** | Generates a signed CMR snapshot JSON and writes it to `snapshots/`. |
| **Inputs**      | `snapshot_label` (str) — etiqueta del snapshot       |
| **Output**      | `Snapshot`                                           |
| **UA Cost**     | 1.5                                                  |
| **Timeout**     | 5,000 ms                                             |
| **Side Effects**| `file:write`                                         |
| **Rollback**    | `BEST_EFFORT`                                        |
| **Idempotent**  | Sí (mismo label → mismo archivo determinista)        |

**Cuándo usarlo**: Para sellar el estado actual del ledger CMR con una firma hash. Idempotente: si el label ya existe, el resultado es el mismo archivo. Requiere confirmación explícita del usuario antes de escribir en disco.

**Flujo mínimo**:
```python
req = ExecutionRequest(
    request_id="seal-v1.2.0",
    skill_id="gahenax.generate_snapshot",
    inputs={"snapshot_label": "gahenax_core_v1.2.0_baseline"},
    mode="GEM",
    ua_budget=6.0,
    dry_run=True,           # SIEMPRE simular primero antes de confirmar
)
result = gateway.execute(req)
# result.status → DRY_RUN  (sin escritura real)
# Después de confirmación del usuario:
req.dry_run = False
result = gateway.execute(req)
# result.status → OK
# result.outputs → {"path": "snapshots/gahenax_core_v1.2.0_baseline.json", ...}
```

---

### SKILL-03 — `gahenax.migrate_ledger_schema`

| Campo           | Valor                                                              |
|-----------------|--------------------------------------------------------------------|
| **Risk Level**  | `LOCKED`                                                           |
| **Intent Tags** | `migration`, `schema`, `db`, `upgrade`, `alter`                    |
| **Description** | Applies a migration to the CMR SQLite schema. Irreversible without backup. |
| **Inputs**      | `migration_id` (str), `sql_patch` (str)                            |
| **Output**      | `MigrationResult`                                                  |
| **UA Cost**     | 4.0                                                                |
| **Timeout**     | 15,000 ms                                                          |
| **Side Effects**| `db:write`, `db:schema`                                            |
| **Rollback**    | `REQUIRED`                                                         |
| **Idempotent**  | Sí (`migration_id` previene doble aplicación)                      |
| **dry_run_default** | `True` — siempre inicia en modo simulado                       |

**Cuándo usarlo**: Solo cuando una alteración del schema SQLite del CMR es estrictamente necesaria. Requiere modo `AUDIT` + `risk_override=True`. El rollback es obligatorio — si no hay procedimiento de reversión definido, no se ejecuta.

**Restricciones de acceso**:
```
modo GEM         → BLOCKED  (SIDE_EFFECT_DENIED)
modo AUDIT       → BLOCKED si risk_override=False
modo AUDIT       → DRY_RUN primero (dry_run_default=True)
modo AUDIT + override + dry_run=False → EJECUTA
```

**Flujo mínimo**:
```python
req = ExecutionRequest(
    request_id="migration-0001",
    skill_id="gahenax.migrate_ledger_schema",
    inputs={
        "migration_id": "0001_add_session_column",
        "sql_patch": "ALTER TABLE cmr_runs ADD COLUMN session_tag TEXT DEFAULT NULL;",
    },
    mode="AUDIT",
    ua_budget=6.0,
    risk_override=True,
    dry_run=True,           # OBLIGATORIO en primera ejecución
)
result = gateway.execute(req)
# result.status → DRY_RUN
# Validar outputs y evidencia antes de ejecutar en producción
```

---

## 5. Circuit Breaker — Protección por Cuarentena

El `ExecutionGateway` mantiene un `CircuitBreaker` por cada `skill_id`.

```
Estado: CLOSED (normal)
    │
    ├─ N fallos consecutivos ≥ threshold (default: 3)
    │
    ▼
Estado: OPEN → QUARANTINED
    │  Todas las ejecuciones retornan BLOCKED (CIRCUIT_OPEN)
    │  Duración: quarantine_window_s (default: 300s)
    │
    ├─ Ventana expirada → estado HALF-OPEN
    │
    ▼
Estado: CLOSED (reset automático al primer éxito)
```

| Política         | threshold | quarantine | retries |
|------------------|-----------|------------|---------|
| `default()`      | 3         | 300 s      | 2       |
| `strict()`       | 1         | 600 s      | 0       |

Un skill en cuarentena no ejecuta aunque el request sea válido.
La cuarentena protege el CMR de rafagas de errores sistémicos.

---

## 6. Idempotencia

Todo skill marcado `idempotent=True` almacena su `ExecutionResult` en el
`IdempotencyStore` (in-memory, pluggable).

Si llega un request con el mismo `request_id`:
- El resultado es retornado inmediatamente desde caché.
- `error_class = IDEMPOTENCY_REPLAY` se agrega al resultado como trazabilidad.
- No se ejecuta ninguna lógica, no se cobra UA, no se toca el CMR.

```
request_id "seal-v1.2.0" → ejecutado → almacenado en cache
request_id "seal-v1.2.0" → reintento → retorna resultado cacheado (IDEMPOTENCY_REPLAY)
```

**Regla**: El `request_id` debe ser único por operación lógica.
Usar UUIDs o identificadores semánticos deterministas (hash del input).

---

## 7. Registro CMR (Canonical Measurement Recorder)

Cada ejecución exitosa es registrada en el CMR:

```
ExecutionResult
    ├── request_id
    ├── skill_id
    ├── status
    ├── outputs
    ├── evidence         ← SHA-256 hash del output
    ├── metrics          ← latency_ms, ua_spend
    └── timestamp (UTC)
        │
        ▼
   cmr.record_run()     ← append-only, encadenado criptográficamente
```

El CMR es el **ledger de falsificabilidad**. Sin él, un skill con `side_effects`
es bloqueado cuando `fail_closed=True` (default).

---

## 8. Añadir un Nuevo Skill — Protocolo

### Paso 1: Declarar el SkillSpec

```python
# En: backend/gahenax_app/core/skill_registry_bootstrap.py

registry.register(SkillSpec(
    skill_id          = "gahenax.<dominio>.<verbo>",
    intent_tags       = ["tag_semantico"],
    description       = "Qué hace. Una oración. Sin ambigüedad.",
    risk_level        = RiskLevel.AUTO,        # AUTO si no hay side effects
    required_inputs   = ["campo_requerido"],
    output_schema     = "NombreSchema",
    ua_cost_estimate  = 1.0,                   # ser conservador
    timeout_ms        = 5000,
    idempotent        = True,
    side_effects      = [],                    # vacío si AUTO
    rollback          = RollbackPolicy.NONE,
    enabled           = True,
    dry_run_default   = False,
))
```

### Paso 2: Implementar el Handler

```python
# El handler recibe (inputs: dict, dry_run: bool) y retorna dict

def my_skill_handler(inputs: dict, dry_run: bool = False) -> dict:
    if dry_run:
        return {"simulated": True, "would_do": "describir acción"}

    # lógica real aquí
    result = do_real_work(inputs["campo_requerido"])
    return {"output": result, "hash": sha256(result)}

# Registrar en el gateway:
gateway._tool_runner.register_handler("gahenax.<dominio>.<verbo>", my_skill_handler)
```

### Paso 3: Documentar en este archivo

Añadir una sección `SKILL-NN` en el [Catálogo Canónico](#4-catálogo-canónico-de-skills-v111)
con todos los campos de la tabla y ejemplos de flujo.

### Paso 4: Registrar en el CMR

La primera ejecución con `dry_run=True` debe correr y loguearse antes de promover
el skill a producción. El `result.evidence_hash()` es la firma de verificación.

### Lista de Verificación (Checklist de Admisión)

- [ ] `skill_id` sigue el patrón `gahenax.<dominio>.<verbo>`
- [ ] `description` no contiene verbos imperativos ni absolutos
- [ ] `risk_level` es el mínimo necesario (preferir AUTO)
- [ ] `side_effects` declara todos los recursos que escribe
- [ ] `rollback` es `REQUIRED` si el skill altera schema o estado global
- [ ] `ua_cost_estimate` ha sido medido (no estimado a ojo)
- [ ] Handler implementado y registrado en `_tool_runner`
- [ ] `dry_run=True` ejecutado y resultado verificado
- [ ] Documentación añadida a este archivo
- [ ] Entrada añadida al `CHANGELOG.md`

---

## 9. Errores del Gateway — Referencia

| `ErrorClass`          | Causa                                                      | Retryable |
|-----------------------|------------------------------------------------------------|-----------|
| `SCHEMA_VIOLATION`    | `skill_id` no existe en el registry                        | No        |
| `UA_CAP_EXCEEDED`     | Costo estimado del skill supera el budget del request      | Sí (aumentar budget) |
| `TIMEOUT`             | Ejecución superó `timeout_ms`                              | Sí        |
| `SIDE_EFFECT_DENIED`  | Skill LOCKED ejecutado sin modo AUDIT o sin `risk_override`| No        |
| `CIRCUIT_OPEN`        | Skill en cuarentena por fallos consecutivos                | Sí (esperar quarantine_window_s) |
| `IDEMPOTENCY_REPLAY`  | `request_id` ya fue ejecutado (resultado cacheado)         | N/A       |
| `TOOL_ERROR`          | Excepción dentro del handler                               | Sí        |
| `CMR_UNAVAILABLE`     | Skill con side effects sin CMR conectado (fail_closed=True)| No        |
| `UNKNOWN`             | Error no clasificado                                       | Sí        |

---

## 10. Invariantes del Sistema

Estas condiciones deben ser verdaderas en todo momento. Si alguna falla, el
sistema debe detenerse y registrar un `SEV-1` en el Antigravity Runbook.

```
1. Ningun skill ejecuta si su circuit breaker esta abierto.
2. Ningun skill con side_effects ejecuta sin CMR si fail_closed=True.
3. Ningun skill LOCKED ejecuta fuera de modo AUDIT.
4. Todo resultado de ejecucion tiene un evidence_hash sellado.
5. El CMR ledger es append-only. Ningun registro puede ser modificado.
6. ua_cost_estimate nunca es 0.0 para skills con side effects.
7. dry_run_default=True para todo skill LOCKED.
```

---

*Documento gobernado por el Gahenax Contract — Falsifiable Contractual Design (FCD)*
*Autor: Antigravity / Gahenax Team*
*Engine Version: GahenaxCore-v1.1.1*
