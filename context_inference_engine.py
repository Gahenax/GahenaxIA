"""

       GAHENAX CIE v2.0 — Context Inference Engine                          
       Motor: Ouroboros-v2-Sigil | OEDA Protocol | BM25 Heuristic Router    


El CIE es el cerebro analítico de Gahenax AI. Recibe un snapshot del estado
de un repositorio o proyecto, clasifica su contexto mediante el sistema de
Sigilos de Ouroboros-v2, activa las heurísticas relevantes desde los archivos
de reglas, y emite un dictamen gobernado con acciones priorizadas.

CICLO INTERNO: Observe → Evaluate → Decide → Act  (OEDA)

Uso básico:
    from context_inference_engine import CIE
    engine = CIE()
    result = engine.infer(snapshot)
    print(result.to_json())

Uso con escaneo de repositorio real:
    result = engine.scan_repo("./mi_proyecto")
    print(result.to_report())
"""

from __future__ import annotations

import json
import math
import os
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# 
#  MÓDULO 1 — TAXONOMÍA DE SIGILOS (Ouroboros-v2)
#  Cada componente del sistema pertenece a exactamente un Sigilo.
# 

class Sigil:
    """Constantes canónicas del sistema de Sigilos Ouroboros-v2."""
    GATE   = "GATE"    # Validación, autenticación, rate limiting, firewalls
    SWORD  = "SWORD"   # Lógica destructiva, mutación de estado, compute pesado
    ALTAR  = "ALTAR"   # Almacenamiento, ORMs, persistencia inmutable
    MIRROR = "MIRROR"  # Observabilidad, logs, telemetría, métricas
    CHAIN  = "CHAIN"   # Flujos asíncronos, mensajería, pipelines, eventos
    MAP    = "MAP"     # Esquemas relacionales, mapas de entidades, ERDs
    KEY    = "KEY"     # Secretos, credenciales, vault, API keys (idempotentes)
    SEAL   = "SEAL"    # Contratos sellados, interfaces inmutables publicadas
    SCALE  = "SCALE"   # Configuración de escalado, SLAs, métricas de carga
    CIRCLE = "CIRCLE"  # Bucles de feedback, auto-mejora, evaluación continua

# Invariantes ontológicas del Engine Manifest (engine_manifest.json)
INVARIANTS = {
    "strict_idempotency": [Sigil.KEY, Sigil.ALTAR],
    "require_gates":      [Sigil.CHAIN, Sigil.SCALE, Sigil.SWORD],
    "require_seals":      [Sigil.MIRROR, Sigil.CHAIN],
}

# Mapa: tecnología detectada → Sigil primario
TECH_SIGIL_MAP: dict[str, str] = {
    # GATE — Seguridad y validación
    "next-auth":   Sigil.GATE, "passport":    Sigil.GATE,
    "jwt":         Sigil.GATE, "oauth":       Sigil.GATE,
    "keycloak":    Sigil.GATE, "auth0":       Sigil.GATE,
    "zod":         Sigil.GATE, "pydantic":    Sigil.GATE,
    "kong":        Sigil.GATE, "nginx":       Sigil.GATE,
    "traefik":     Sigil.GATE, "rate-limit":  Sigil.GATE,
    # SWORD — Lógica crítica
    "stripe":      Sigil.SWORD, "paypal":     Sigil.SWORD,
    "omnipay":     Sigil.SWORD, "celery":     Sigil.SWORD,
    "fastapi":     Sigil.SWORD, "django":     Sigil.SWORD,
    "spring":      Sigil.SWORD, "axum":       Sigil.SWORD,
    "rayon":       Sigil.SWORD, "tokio":      Sigil.SWORD,
    # ALTAR — Persistencia
    "prisma":      Sigil.ALTAR, "sequelize":  Sigil.ALTAR,
    "typeorm":     Sigil.ALTAR, "mongoose":   Sigil.ALTAR,
    "sqlalchemy":  Sigil.ALTAR, "eloquent":   Sigil.ALTAR,
    "drizzle":     Sigil.ALTAR, "hibernate":  Sigil.ALTAR,
    "mysql":       Sigil.ALTAR, "postgresql": Sigil.ALTAR,
    "mongodb":     Sigil.ALTAR, "redis":      Sigil.ALTAR,
    "milvus":      Sigil.ALTAR, "sqlite":     Sigil.ALTAR,
    # MIRROR — Observabilidad
    "opentelemetry": Sigil.MIRROR, "otel":     Sigil.MIRROR,
    "grafana":     Sigil.MIRROR, "prometheus": Sigil.MIRROR,
    "sentry":      Sigil.MIRROR, "datadog":   Sigil.MIRROR,
    "loki":        Sigil.MIRROR, "tempo":     Sigil.MIRROR,
    "winston":     Sigil.MIRROR, "pino":      Sigil.MIRROR,
    # CHAIN — Mensajería y flujos
    "kafka":       Sigil.CHAIN, "rabbitmq":  Sigil.CHAIN,
    "celery":      Sigil.CHAIN, "bull":      Sigil.CHAIN,
    "redis-queue": Sigil.CHAIN, "temporal":  Sigil.CHAIN,
    "zeebe":       Sigil.CHAIN, "nats":      Sigil.CHAIN,
    "sqs":         Sigil.CHAIN, "pubsub":    Sigil.CHAIN,
    # KEY — Secretos
    "vault":       Sigil.KEY,  "doppler":   Sigil.KEY,
    "vaultwarden": Sigil.KEY,  "dotenv":    Sigil.KEY,
    "aws-secrets": Sigil.KEY,
    # SCALE — Infraestructura y escalado
    "kubernetes":  Sigil.SCALE, "docker":    Sigil.SCALE,
    "helm":        Sigil.SCALE, "terraform": Sigil.SCALE,
    "cloudflare":  Sigil.SCALE, "vercel":    Sigil.SCALE,
    "aws":         Sigil.SCALE, "gcp":       Sigil.SCALE,
}

# Mapa de blueprints (tipo de proyecto)
FRAMEWORK_BLUEPRINTS: dict[str, str] = {
    "react":      "frontend:spa",
    "nextjs":     "frontend:ssr",
    "nuxt":       "frontend:ssr",
    "vue":        "frontend:spa",
    "angular":    "frontend:spa",
    "svelte":     "frontend:compiler",
    "sveltekit":  "frontend:ssr",
    "fastapi":    "backend:asgi",
    "django":     "backend:wsgi",
    "flask":      "backend:wsgi",
    "spring":     "backend:jvm",
    "axum":       "backend:rust",
    "express":    "backend:node",
    "nestjs":     "backend:node",
    "tauri":      "desktop:hybrid",
    "electron":   "desktop:hybrid",
    "react-native": "mobile:cross",
    "flutter":    "mobile:cross",
    "swift":      "mobile:native-ios",
    "kotlin":     "mobile:native-android",
}


# 
#  MÓDULO 2 — BM25 HEURISTIC ROUTER
#  Routing determinista de heurísticas sin llamar a un LLM.
# 

class HeuristicBM25:
    """
    Motor BM25 Okapi para routing de heurísticas de antigravity_rules/.
    Indexa el contenido de los .md files y retorna las heurísticas más
    relevantes dado el stack tecnológico detectado.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self._docs:       list[dict]             = []
        self._index:      dict[str, dict[int, int]] = defaultdict(dict)
        self._doc_lengths: dict[int, int]        = {}
        self._idf:        dict[str, float]       = {}
        self._avg_dl:     float                  = 1.0
        # Índice de heurísticas: código → objeto
        self._heuristic_map: dict[str, dict]     = {}

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return [w for w in text.split() if len(w) >= 3]

    def load_rules_directory(self, rules_dir: str) -> int:
        """
        Carga y parsea todos los archivos .md del directorio de reglas.
        Extrae heurísticas con patrón [HEURISTICA-*] de su contenido.
        Retorna el número de documentos cargados.
        """
        rules_path = Path(rules_dir)
        if not rules_path.exists():
            return 0

        docs = []
        heuristics = []

        for md_file in sorted(rules_path.glob("*.md")):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            domain  = md_file.stem  # ej: "web_frameworks"

            # Extrae bloques de heurísticas individuales con regex
            pattern = r'\[(?P<code>HEURISTICA-[A-Z0-9\-]+)[^\]]*\].*?\"(?P<desc>[^\"]+)\"'
            for match in re.finditer(pattern, content, re.DOTALL):
                h_code  = match.group("code")
                h_desc  = match.group("desc")
                h_obj   = {
                    "code":    h_code,
                    "desc":    h_desc,
                    "domain":  domain,
                    "source":  md_file.name,
                    "content": content,  # corpus completo del file para BM25
                }
                self._heuristic_map[h_code] = h_obj
                heuristics.append(h_obj)

            # También indexa el documento completo por keyword domain
            docs.append({
                "domain":  domain,
                "source":  md_file.name,
                "content": content,
                "heuristics": [h["code"] for h in heuristics
                               if h["domain"] == domain],
            })

        self._fit(docs, "content")
        self._docs = docs
        return len(docs)

    def _fit(self, docs: list[dict], field: str) -> None:
        corpus = [self._tokenize(d[field]) for d in docs]
        N = len(corpus)
        if N == 0:
            return
        total = 0
        for i, tokens in enumerate(corpus):
            self._doc_lengths[i] = len(tokens)
            total += len(tokens)
            freq: dict[str, int] = defaultdict(int)
            for t in tokens:
                freq[t] += 1
            for t, f in freq.items():
                self._index[t][i] = f
        self._avg_dl = total / N
        for term, postings in self._index.items():
            df = len(postings)
            self._idf[term] = math.log((N - df + 0.5) / (df + 0.5) + 1)

    def query(self, query: str, top_k: int = 5) -> list[tuple[float, dict]]:
        """Retorna los top_k documentos más relevantes con sus scores."""
        tokens       = self._tokenize(query)
        scores: dict[int, float] = defaultdict(float)
        for term in tokens:
            if term not in self._index:
                continue
            for doc_id, freq in self._index[term].items():
                dl = self._doc_lengths[doc_id]
                tf = (freq * (self.k1 + 1)) / (
                    freq + self.k1 * (1 - self.b + self.b * dl / self._avg_dl)
                )
                scores[doc_id] += self._idf.get(term, 0) * tf
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(score, self._docs[doc_id]) for doc_id, score in ranked[:top_k]]

    def get_heuristics_for_stack(self, frameworks: list[str],
                                  language: str) -> list[dict]:
        """
        Dado el stack detectado, retorna todas las heurísticas relevantes
        usando BM25 sobre el corpus de antigravity_rules.
        """
        query = " ".join(frameworks + [language])
        ranked = self.query(query, top_k=5)

        triggered: dict[str, dict] = {}
        for score, doc in ranked:
            if score < 0.1:
                continue
            for h_code in doc.get("heuristics", []):
                if h_code in self._heuristic_map:
                    triggered[h_code] = self._heuristic_map[h_code]

        return list(triggered.values())

    def all_heuristics(self) -> dict[str, dict]:
        return self._heuristic_map


# 
#  MÓDULO 3 — SNAPSHOT (Contrato de Entrada)
# 

@dataclass
class CIESnapshot:
    """
    El payload que el CIE espera recibir.
    Puede construirse manualmente o auto-completarse via scan_repo().
    """
    # Identificación
    request_id:        str  = field(default_factory=lambda: str(uuid.uuid4()))
    phase:             str  = "analysis"  # analysis | debugging | refactor | greenfield

    # Stack tecnológico
    primary_language:  str  = "unknown"
    frameworks:        list = field(default_factory=list)
    orm:               str  = ""
    database:          str  = ""
    auth_provider:     str  = ""
    messaging:         list = field(default_factory=list)
    observability:     list = field(default_factory=list)
    infra:             list = field(default_factory=list)

    # Señales de madurez
    file_count:        int   = 0
    test_density:      float = 0.0   # 0.0 a 1.0 (ratio test files / total files)
    has_cicd:          bool  = False
    has_docker:        bool  = False
    has_dist_tracing:  bool  = False
    has_type_safety:   bool  = False  # TypeScript, typed Python, Java

    # Señales de seguridad / pagos
    has_payments:           bool = False
    uses_sandbox_keys:      bool = True
    authenticates_webhooks: bool = True
    has_rate_limiting:      bool = False
    has_input_validation:   bool = False

    # Contexto libre
    raw_context:       str  = ""

    @classmethod
    def from_json(cls, raw: str) -> "CIESnapshot":
        data = json.loads(raw)
        # Normaliza el JSON plano al dataclass
        target  = data.get("target", data)
        signals = data.get("signals", data)
        return cls(
            request_id        = data.get("request_id", str(uuid.uuid4())),
            phase             = data.get("phase", "analysis"),
            primary_language  = target.get("primary_language", "unknown").lower(),
            frameworks        = [f.lower() for f in target.get("frameworks", [])],
            orm               = signals.get("database_orm", ""),
            database          = signals.get("database", ""),
            auth_provider     = signals.get("auth_provider", ""),
            messaging         = signals.get("messaging", []),
            observability     = signals.get("observability", []),
            infra             = signals.get("infra", []),
            file_count        = signals.get("file_count", 0),
            test_density      = float(signals.get("test_density", 0.0)),
            has_cicd          = bool(signals.get("has_cicd", False)),
            has_docker        = bool(signals.get("has_docker", False)),
            has_dist_tracing  = bool(signals.get("has_distributed_tracing", False)),
            has_type_safety   = bool(signals.get("has_type_safety", False)),
            has_payments      = bool(signals.get("has_payments", False)),
            uses_sandbox_keys = bool(signals.get("uses_sandbox_keys", True)),
            authenticates_webhooks = bool(signals.get("authenticates_webhooks", True)),
            has_rate_limiting = bool(signals.get("has_rate_limiting", False)),
            has_input_validation = bool(signals.get("has_input_validation", False)),
            raw_context       = data.get("raw_context", ""),
        )


# 
#  MÓDULO 4 — RESULTADO (Contrato de Salida)
# 

@dataclass
class SigilAssignment:
    """Una tecnología asignada a su Sigilo correspondiente."""
    tech:   str
    sigil:  str
    reason: str

@dataclass
class InvariantViolation:
    """Una violación de las invariantes ontológicas de Ouroboros-v2."""
    rule:        str
    description: str
    severity:    str  # "warning" | "critical"

@dataclass
class HeuristicTrigger:
    """Una heurística activada con su código canónico y descripción."""
    code:    str
    domain:  str
    desc:    str
    source:  str

@dataclass
class CIEResult:
    """El dictamen gobernado del CIE."""
    request_id:          str
    timestamp:           str
    # Fase 1: Inferencia
    context_blueprint:   str               # ej: "frontend:ssr"
    project_maturity:    str               # "greenfield" | "growing" | "mature" | "legacy"
    intent:              str               # "feature-addition" | "heavy-refactoring" | "bug-hunting"
    # Fase 2: Catalogación Sigil
    sigil_assignments:   list[SigilAssignment]
    sigil_summary:       dict[str, list[str]]   # sigil → [techs]
    # Fase 3: Invariantes
    invariant_violations: list[InvariantViolation]
    risk_level:          str               # "low" | "medium" | "critical"
    # Fase 4: Heurísticas
    heuristics_triggered: list[HeuristicTrigger]
    # Fase 5: Acciones OEDA
    suggested_actions:   list[dict]        # [{priority, action, sigil}]
    # Metadatos
    confidence_score:    float
    cie_alert:           Optional[str] = None

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    def to_report(self) -> str:
        """Genera un reporte Markdown legible para humanos."""
        lines = [
            f"#  CIE Report — {self.timestamp}",
            f"**Request ID:** `{self.request_id}`",
            f"**Blueprint:** `{self.context_blueprint}`  |  "
            f"**Madurez:** `{self.project_maturity}`  |  "
            f"**Intent:** `{self.intent}`",
            "",
            f"##  Nivel de Riesgo: `{self.risk_level.upper()}`",
        ]

        if self.cie_alert:
            lines += [f"\n> **CIE Alert:** {self.cie_alert}", ""]

        # Sigil Summary
        lines += ["", "##  Mapa de Sigilos"]
        for sigil, techs in sorted(self.sigil_summary.items()):
            if techs:
                lines.append(f"  - **{sigil}** → {', '.join(f'`{t}`' for t in techs)}")

        # Invariant Violations
        if self.invariant_violations:
            lines += ["", "##  Violaciones de Invariantes Ontológicas"]
            for v in self.invariant_violations:
                icon = "" if v.severity == "critical" else ""
                lines.append(f"  {icon} **[{v.rule}]** {v.description}")

        # Heuristics
        if self.heuristics_triggered:
            lines += ["", "##  Heurísticas Activadas"]
            for h in self.heuristics_triggered:
                lines.append(f"  - **[{h.code}]** _{h.domain}_ — {h.desc[:100]}...")

        # Actions
        if self.suggested_actions:
            lines += ["", "##  Acciones OEDA"]
            for i, action in enumerate(self.suggested_actions, 1):
                prio = action.get("priority", "MED")
                sigil = action.get("sigil", "")
                msg   = action.get("action", "")
                lines.append(f"  {i}. `[{prio}]` [{sigil}] {msg}")

        lines += [
            "",
            f"---",
            f"**Confidence Score:** `{self.confidence_score:.0%}`",
        ]
        return "\n".join(lines)


# 
#  MÓDULO 5 — CIE CORE ENGINE (Ouroboros-v2-Sigil)
#  El bucle OEDA completo.
# 

class CIE:
    """
    Context Inference Engine v2.0 — Motor Gahenax.

    Implementa el ciclo OEDA sobre el snapshot recibido:
      O → Observe:  Extrae framework, tecnologías, señales de madurez
      E → Evaluate: Clasifica con Sigilos, valida invariantes
      D → Decide:   Prioriza acciones, activa heurísticas
      A → Act:      Emite el CIEResult gobernado
    """

    def __init__(self, rules_dir: str = "./antigravity_rules"):
        self._router = HeuristicBM25()
        loaded = self._router.load_rules_directory(rules_dir)
        self._rules_loaded = loaded
        self._rules_dir    = rules_dir

    #  PUNTO DE ENTRADA PRINCIPAL 

    def infer(self, snapshot: CIESnapshot | str | dict) -> CIEResult:
        """
        Recibe un CIESnapshot, dict o JSON string.
        Ejecuta el ciclo OEDA completo y retorna un CIEResult.
        """
        # Normaliza la entrada
        if isinstance(snapshot, str):
            snap = CIESnapshot.from_json(snapshot)
        elif isinstance(snapshot, dict):
            snap = CIESnapshot.from_json(json.dumps(snapshot))
        else:
            snap = snapshot

        #  OBSERVE 
        all_techs = self._gather_all_techs(snap)
        blueprint = self._detect_blueprint(snap)
        maturity  = self._assess_maturity(snap)
        intent    = self._classify_intent(snap)

        #  EVALUATE 
        assignments  = self._assign_sigils(all_techs)
        sigil_summary = self._build_sigil_summary(assignments)
        violations   = self._check_invariants(snap, sigil_summary)
        risk_level   = self._compute_risk(snap, violations)
        heuristics   = self._route_heuristics(snap)

        #  DECIDE 
        actions      = self._generate_actions(snap, violations, risk_level, sigil_summary)
        confidence   = self._compute_confidence(snap, assignments, heuristics)
        cie_alert    = self._build_cie_alert(violations) if violations else None

        #  ACT 
        return CIEResult(
            request_id           = snap.request_id,
            timestamp            = datetime.now(timezone.utc).isoformat(),
            context_blueprint    = blueprint,
            project_maturity     = maturity,
            intent               = intent,
            sigil_assignments    = assignments,
            sigil_summary        = sigil_summary,
            invariant_violations = violations,
            risk_level           = risk_level,
            heuristics_triggered = heuristics,
            suggested_actions    = actions,
            confidence_score     = confidence,
            cie_alert            = cie_alert,
        )

    def scan_repo(self, repo_path: str) -> CIEResult:
        """
        Escanea un repositorio local y construye un CIESnapshot automáticamente.
        Detecta: lenguaje, frameworks, ORM, tests, CI/CD, Docker, pagos, etc.
        """
        path = Path(repo_path)
        if not path.exists():
            raise FileNotFoundError(f"Repositorio no encontrado: {repo_path}")

        snap = self._auto_scan(path)
        return self.infer(snap)

    #  OBSERVE HELPERS 

    def _gather_all_techs(self, snap: CIESnapshot) -> list[str]:
        techs = list(snap.frameworks)
        if snap.orm:          techs.append(snap.orm)
        if snap.database:     techs.append(snap.database)
        if snap.auth_provider: techs.append(snap.auth_provider)
        techs.extend(snap.messaging)
        techs.extend(snap.observability)
        techs.extend(snap.infra)
        return [t.lower() for t in techs if t]

    def _detect_blueprint(self, snap: CIESnapshot) -> str:
        for fw in snap.frameworks:
            if fw in FRAMEWORK_BLUEPRINTS:
                return FRAMEWORK_BLUEPRINTS[fw]
        lang_map = {
            "typescript": "frontend:unknown",
            "javascript": "frontend:unknown",
            "python":     "backend:asgi",
            "java":       "backend:jvm",
            "rust":       "backend:rust",
            "go":         "backend:go",
            "kotlin":     "mobile:native-android",
            "swift":      "mobile:native-ios",
        }
        return lang_map.get(snap.primary_language, "unknown:unknown")

    def _assess_maturity(self, snap: CIESnapshot) -> str:
        score = 0
        if snap.has_cicd:          score += 2
        if snap.has_docker:        score += 1
        if snap.test_density > 0.3: score += 2
        if snap.test_density > 0.6: score += 1
        if snap.has_dist_tracing:  score += 2
        if snap.has_type_safety:   score += 1
        if snap.file_count > 200:  score += 1
        if score >= 8:  return "mature"
        if score >= 5:  return "growing"
        if score >= 2:  return "greenfield"
        return "legacy"

    def _classify_intent(self, snap: CIESnapshot) -> str:
        if snap.phase == "debugging":       return "bug-hunting"
        if snap.file_count > 100:           return "heavy-refactoring"
        if snap.phase == "greenfield":      return "greenfield-build"
        return "feature-addition"

    #  EVALUATE HELPERS 

    def _assign_sigils(self, techs: list[str]) -> list[SigilAssignment]:
        assignments = []
        for tech in techs:
            sigil = TECH_SIGIL_MAP.get(tech)
            if sigil:
                reason = self._sigil_reason(tech, sigil)
                assignments.append(SigilAssignment(tech=tech, sigil=sigil, reason=reason))
        return assignments

    def _sigil_reason(self, tech: str, sigil: str) -> str:
        reasons = {
            Sigil.GATE:   f"`{tech}` provee validación / autenticación / firewall",
            Sigil.SWORD:  f"`{tech}` ejecuta lógica de negocio crítica o mutación de estado",
            Sigil.ALTAR:  f"`{tech}` gestiona persistencia / almacenamiento",
            Sigil.MIRROR: f"`{tech}` emite observabilidad / logs / telemetría",
            Sigil.CHAIN:  f"`{tech}` opera sobre flujos asíncronos / mensajería",
            Sigil.KEY:    f"`{tech}` maneja secretos / credenciales",
            Sigil.SCALE:  f"`{tech}` gestiona infraestructura / escalado",
        }
        return reasons.get(sigil, f"`{tech}` asignado a {sigil}")

    def _build_sigil_summary(self, assignments: list[SigilAssignment]) -> dict[str, list[str]]:
        summary: dict[str, list[str]] = {s: [] for s in vars(Sigil).values()
                                          if isinstance(s, str) and s.isupper()}
        for a in assignments:
            if a.sigil in summary:
                summary[a.sigil].append(a.tech)
        return summary

    def _check_invariants(self, snap: CIESnapshot,
                           sigil_summary: dict[str, list[str]]) -> list[InvariantViolation]:
        violations: list[InvariantViolation] = []

        # Invariante 1: SWORD/ALTAR requieren GATE
        has_gate  = bool(sigil_summary.get(Sigil.GATE))
        has_sword = bool(sigil_summary.get(Sigil.SWORD))
        has_altar = bool(sigil_summary.get(Sigil.ALTAR))

        if (has_sword or has_altar) and not has_gate:
            violations.append(InvariantViolation(
                rule     = "GATE_REQUIRED_FOR_SWORD_ALTAR",
                description = (
                    f"Se detectaron componentes {'SWORD' if has_sword else ''} "
                    f"{'ALTAR' if has_altar else ''} sin ningún GATE (auth/validación). "
                    "Todo endpoint mutante debe pasar por un GATE primero."
                ),
                severity = "critical",
            ))

        # Invariante 2: CHAIN requiere MIRROR (sin trazabilidad = dead queues invisibles)
        has_chain  = bool(sigil_summary.get(Sigil.CHAIN))
        has_mirror = bool(sigil_summary.get(Sigil.MIRROR))
        if has_chain and not has_mirror:
            violations.append(InvariantViolation(
                rule     = "MIRROR_REQUIRED_FOR_CHAIN",
                description = (
                    "Mensajería asíncrona (CHAIN) detectada sin observabilidad (MIRROR). "
                    "Alto riesgo de dead queues y fallos silenciosos."
                ),
                severity = "critical",
            ))

        # Invariante 3: Pagos sin GATE
        if snap.has_payments and not snap.has_input_validation:
            violations.append(InvariantViolation(
                rule     = "PAYMENT_REQUIRES_GATE",
                description = "Integración de pagos sin validación de inputs. Riesgo de fulfillment spoofing.",
                severity = "critical",
            ))

        # Invariante 4: Pagos sin autenticación de webhooks
        if snap.has_payments and not snap.authenticates_webhooks:
            violations.append(InvariantViolation(
                rule     = "WEBHOOK_SIGNATURE_MISSING",
                description = "FATAL: Webhook sin validación de firma. Cualquier HTTP POST puede disparar fulfillment.",
                severity = "critical",
            ))

        # Invariante 5: Densidad de tests crítica
        if snap.test_density < 0.10:
            violations.append(InvariantViolation(
                rule     = "CRITICAL_LOW_TEST_DENSITY",
                description = f"Densidad de tests: {snap.test_density:.0%}. Por debajo del umbral crítico (10%). Mutaciones son peligrosas.",
                severity = "critical",
            ))
        elif snap.test_density < 0.20:
            violations.append(InvariantViolation(
                rule     = "LOW_TEST_DENSITY",
                description = f"Densidad de tests: {snap.test_density:.0%}. Baja (umbral recomendado: 30%+).",
                severity = "warning",
            ))

        # Invariante 6: UUIDv4 como PK (MySQL)
        if "mysql" in snap.database.lower() or "mysql" in snap.frameworks:
            if snap.orm and "uuid" in snap.raw_context.lower():
                if "v4" in snap.raw_context.lower() or "uuidv4" in snap.raw_context.lower():
                    violations.append(InvariantViolation(
                        rule     = "UUIDV4_PK_MYSQL_FORBIDDEN",
                        description = "UUIDv4 como Primary Key en MySQL destruye el Clustered B+ Tree. Usa ULIDv7 o INT auto-increment.",
                        severity = "critical",
                    ))

        # Invariante 7: ASGI bloqueando Event Loop
        if "fastapi" in snap.frameworks or "starlette" in snap.frameworks:
            if "asyncio.sleep" not in snap.raw_context and "await" not in snap.raw_context:
                if "time.sleep" in snap.raw_context or "requests." in snap.raw_context:
                    violations.append(InvariantViolation(
                        rule     = "ASGI_EVENT_LOOP_BLOCKED",
                        description = "FastAPI con llamadas síncronas bloqueantes detectadas. Usa `httpx` async o workers con BackgroundTasks.",
                        severity = "critical",
                    ))

        return violations

    def _compute_risk(self, snap: CIESnapshot,
                       violations: list[InvariantViolation]) -> str:
        critical_count = sum(1 for v in violations if v.severity == "critical")
        warning_count  = sum(1 for v in violations if v.severity == "warning")
        if critical_count > 0:    return "critical"
        if warning_count  > 0:    return "medium"
        if not snap.has_cicd:     return "medium"
        return "low"

    #  DECIDE HELPERS 

    def _route_heuristics(self, snap: CIESnapshot) -> list[HeuristicTrigger]:
        if self._rules_loaded == 0:
            return []
        raw = self._router.get_heuristics_for_stack(snap.frameworks, snap.primary_language)
        return [
            HeuristicTrigger(
                code   = h["code"],
                domain = h["domain"],
                desc   = h["desc"],
                source = h["source"],
            )
            for h in raw
        ]

    def _generate_actions(self, snap: CIESnapshot,
                           violations: list[InvariantViolation],
                           risk_level: str,
                           sigil_summary: dict) -> list[dict]:
        actions = []
        priority_map = {"critical": "P0", "warning": "P1"}

        # Acciones desde violaciones
        for v in violations:
            actions.append({
                "priority": priority_map.get(v.severity, "P2"),
                "sigil":    "GATE",
                "action":   f"[{v.rule}] {v.description}",
            })

        # Acciones de madurez
        if not snap.has_cicd:
            actions.append({
                "priority": "P1",
                "sigil":    "MIRROR",
                "action":   "Implementar CI/CD pipeline. Sin CI, los deploys son manuales y propensos a drift.",
            })
        if snap.test_density < 0.3 and risk_level != "critical":
            actions.append({
                "priority": "P2",
                "sigil":    "CIRCLE",
                "action":   f"Aumentar cobertura de tests al 30%+ (actual: {snap.test_density:.0%}).",
            })
        if snap.has_payments and not snap.uses_sandbox_keys:
            actions.append({
                "priority": "P0",
                "sigil":    "KEY",
                "action":   "FATAL: Claves de pago productivas en pipeline. Rotar a sandbox/test keys inmediatamente.",
            })

        # CHAIN sin MIRROR
        has_chain = bool(sigil_summary.get(Sigil.CHAIN))
        has_mirror = bool(sigil_summary.get(Sigil.MIRROR))
        if has_chain and not has_mirror:
            actions.append({
                "priority": "P1",
                "sigil":    "MIRROR",
                "action":   "Integrar distributed tracing (OpenTelemetry) en todos los consumers del message broker.",
            })

        # Deduplicar y ordenar por prioridad
        seen = set()
        deduped = []
        for a in actions:
            key = a["action"][:60]
            if key not in seen:
                seen.add(key)
                deduped.append(a)

        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        return sorted(deduped, key=lambda x: priority_order.get(x["priority"], 9))

    def _compute_confidence(self, snap: CIESnapshot,
                             assignments: list[SigilAssignment],
                             heuristics: list[HeuristicTrigger]) -> float:
        score = 0.3
        # Más señales = más confianza
        if snap.primary_language != "unknown": score += 0.10
        if snap.frameworks:                    score += 0.15
        if snap.file_count > 0:                score += 0.10
        if snap.test_density > 0:              score += 0.05
        if snap.orm:                           score += 0.05
        if assignments:                        score += 0.10
        if heuristics:                         score += 0.10
        if self._rules_loaded > 0:             score += 0.05
        return round(min(score, 0.98), 2)

    def _build_cie_alert(self, violations: list[InvariantViolation]) -> str:
        criticals = [v for v in violations if v.severity == "critical"]
        if not criticals:
            return ""
        codes = ", ".join(v.rule for v in criticals[:3])
        return (
            f" LINTER ONTOLÓGICO: {len(criticals)} violación(es) crítica(s) detectada(s). "
            f"Reglas: [{codes}]. Resolver antes de merge."
        )

    #  REPO SCANNER 

    def _auto_scan(self, path: Path) -> CIESnapshot:
        """
        Escanea el contenido de un repositorio y auto-construye un CIESnapshot.
        Detecta frameworks, ORM, tests, CI/CD, pagos y más.
        """
        snap = CIESnapshot(request_id=str(uuid.uuid4()), phase="analysis")

        # Recolecta todos los archivos (excluye node_modules, .git, __pycache__)
        excluded = {".git", "node_modules", "__pycache__", ".next",
                    "dist", "build", ".venv", "venv", ".mypy_cache"}
        all_files: list[Path] = []
        for f in path.rglob("*"):
            if f.is_file() and not any(p in f.parts for p in excluded):
                all_files.append(f)

        snap.file_count = len(all_files)

        # Detectar lenguaje dominante
        ext_count: dict[str, int] = defaultdict(int)
        test_files = 0
        for f in all_files:
            ext_count[f.suffix] += 1
            name = f.name.lower()
            if "test" in name or "spec" in name or name.startswith("test_"):
                test_files += 1

        snap.test_density = round(test_files / max(snap.file_count, 1), 3)

        lang_map = {
            ".ts": "typescript", ".tsx": "typescript",
            ".js": "javascript", ".jsx": "javascript",
            ".py": "python",     ".java": "java",
            ".rs": "rust",       ".go": "go",
            ".kt": "kotlin",     ".swift": "swift",
        }
        dominant = max(ext_count, key=ext_count.get) if ext_count else ""
        snap.primary_language = lang_map.get(dominant, "unknown")

        # Detecta CI/CD
        ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile",
                    ".circleci/config.yml", "woodpecker.yml"]
        snap.has_cicd = any((path / ci).exists() for ci in ci_files)

        # Detecta Docker
        snap.has_docker = (path / "Dockerfile").exists() or (path / "docker-compose.yml").exists()

        # Detectar type safety
        if snap.primary_language in ("typescript", "java", "kotlin", "rust", "swift"):
            snap.has_type_safety = True

        # Lee package.json / requirements.txt / pom.xml para frameworks
        self._scan_dependencies(path, snap)

        # Lee raw context (primeros 2KB del readme o main file)
        for candidate in ["README.md", "readme.md", "main.py", "src/index.ts", "src/app.py"]:
            candidate_path = path / candidate
            if candidate_path.exists():
                snap.raw_context = candidate_path.read_text(
                    encoding="utf-8", errors="ignore"
                )[:2048]
                break

        return snap

    def _scan_dependencies(self, path: Path, snap: CIESnapshot) -> None:
        """Lee archivos de dependencias para detectar frameworks y tecnologías."""
        # --- package.json (Node/TS) ---
        pkg_json = path / "package.json"
        if pkg_json.exists():
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
                all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                frameworks, orm, auth, messaging, obs = [], "", "", [], []

                for dep in all_deps:
                    dep_l = dep.lower()
                    if dep_l in ("next", "next.js"):       frameworks.append("nextjs")
                    elif dep_l == "react":                  frameworks.append("react")
                    elif dep_l == "vue":                    frameworks.append("vue")
                    elif dep_l == "svelte":                 frameworks.append("svelte")
                    elif dep_l == "@nestjs/core":           frameworks.append("nestjs")
                    elif dep_l == "express":                frameworks.append("express")
                    elif dep_l == "tauri-apps":             frameworks.append("tauri")
                    elif dep_l in ("prisma", "@prisma/client"): orm = "prisma"
                    elif dep_l == "typeorm":                 orm = "typeorm"
                    elif dep_l == "mongoose":               orm = "mongoose"
                    elif dep_l == "drizzle-orm":            orm = "drizzle"
                    elif "next-auth" in dep_l or dep_l == "auth.js": auth = "next-auth"
                    elif dep_l == "passport":               auth = "passport"
                    elif dep_l == "kafka":                  messaging.append("kafka")
                    elif dep_l == "amqplib":                messaging.append("rabbitmq")
                    elif dep_l == "bullmq":                 messaging.append("bull")
                    elif "@opentelemetry" in dep_l:         obs.append("opentelemetry")
                    elif dep_l == "@sentry/node":           obs.append("sentry")
                    elif dep_l == "stripe":
                        snap.has_payments = True; frameworks.append("stripe")
                    elif dep_l == "paypal":
                        snap.has_payments = True; frameworks.append("paypal")

                snap.frameworks    = list(set(snap.frameworks + frameworks))
                snap.orm           = orm or snap.orm
                snap.auth_provider = auth or snap.auth_provider
                snap.messaging     = list(set(snap.messaging + messaging))
                snap.observability = list(set(snap.observability + obs))
            except Exception:
                pass

        # --- requirements.txt (Python) ---
        req_txt = path / "requirements.txt"
        if req_txt.exists():
            content = req_txt.read_text(encoding="utf-8", errors="ignore").lower()
            mapping = {
                "fastapi": "fastapi", "django": "django", "flask": "flask",
                "sqlalchemy": "sqlalchemy", "pydantic": "pydantic",
                "celery": "celery", "opentelemetry": "opentelemetry",
                "kafka": "kafka", "stripe": "stripe",
            }
            for keyword, tech in mapping.items():
                if keyword in content:
                    if tech in ("fastapi", "django", "flask"):
                        snap.frameworks.append(tech)
                    elif tech in ("sqlalchemy",):
                        snap.orm = tech
                    elif tech in ("celery", "kafka"):
                        snap.messaging.append(tech)
                    elif tech in ("opentelemetry",):
                        snap.observability.append(tech)
                    elif tech == "stripe":
                        snap.has_payments = True

        # --- pom.xml (Java/Kotlin) ---
        pom = path / "pom.xml"
        if pom.exists():
            content = pom.read_text(encoding="utf-8", errors="ignore").lower()
            if "spring-boot" in content:   snap.frameworks.append("spring")
            if "kafka" in content:         snap.messaging.append("kafka")
            if "hibernate" in content:     snap.orm = "hibernate"
            if "micrometer" in content:    snap.observability.append("micrometer")


# 
#  MÓDULO 6 — CLI / DEMO
# 

if __name__ == "__main__":
    import sys

    RULES_DIR = os.path.join(os.path.dirname(__file__), "antigravity_rules")
    engine = CIE(rules_dir=RULES_DIR)

    print("=" * 70)
    print("  GAHENAX CIE v2.0 — Context Inference Engine")
    print(f"  Reglas cargadas: {engine._rules_loaded} archivos de antigravity_rules/")
    print(f"  Heurísticas indexadas: {len(engine._router.all_heuristics())}")
    print("=" * 70)

    # --- Demo 1: JSON payload (backward-compatible con v1) ---
    print("\n[DEMO 1] Payload JSON (Next.js + RabbitMQ sin MIRROR + Payment sin auth)")
    payload_v1 = """
    {
      "request_id": "cie-demo-001",
      "phase": "ingestion",
      "target": {
        "primary_language": "typescript",
        "frameworks": ["react", "nextjs", "rabbitmq", "stripe"]
      },
      "signals": {
        "file_count": 145,
        "test_density": 0.08,
        "has_cicd": false,
        "has_distributed_tracing": false,
        "database_orm": "prisma",
        "database": "mysql",
        "auth_provider": "next-auth",
        "authenticates_webhooks": false,
        "has_payments": true
      },
      "raw_context": "import UUIDv4 from 'uuid/v4';"
    }
    """
    result = engine.infer(payload_v1)
    print(result.to_report())

    # --- Demo 2: FastAPI sin GATE (Python backend limpio) ---
    print("\n\n" + "=" * 70)
    print("[DEMO 2] FastAPI mature stack (alta madurez)")
    snap2 = CIESnapshot(
        request_id       = "cie-demo-002",
        phase            = "feature-addition",
        primary_language = "python",
        frameworks       = ["fastapi"],
        orm              = "sqlalchemy",
        database         = "postgresql",
        observability    = ["opentelemetry"],
        has_cicd         = True,
        has_docker       = True,
        test_density     = 0.55,
        has_type_safety  = True,
        has_input_validation = True,
        has_rate_limiting    = True,
        auth_provider    = "jwt",
        file_count       = 280,
    )
    result2 = engine.infer(snap2)
    print(result2.to_report())

    # --- Demo 3: Scan de repositorio real (si se pasa como argumento) ---
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        print(f"\n\n{'='*70}")
        print(f"[DEMO 3] Auto-scan: {repo_path}")
        try:
            result3 = engine.scan_repo(repo_path)
            print(result3.to_report())
        except FileNotFoundError as e:
            print(f"    {e}")

    print("\n CIE v2.0 ejecutado correctamente.")
