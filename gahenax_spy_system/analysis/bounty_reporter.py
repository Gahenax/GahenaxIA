import json
from datetime import datetime
from pathlib import Path

class BountyReporter:
    """
    Genera reportes profesionales de vulnerabilidades en Markdown.
    Alineado con el curso 'White Hat Security Foundations' (Unidad 8).
    """
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, finding: dict, target_domain: str):
        """
        Crea un archivo .md con la estructura profesional.
        finding: {
            "type": "...",
            "severity": "...",
            "url": "...",
            "evidence": "...",
            "impact": "...",
            "mitigation": "..."
        }
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_type = finding["type"].replace(" ", "_").lower()
        filename = f"report_{target_domain}_{safe_type}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        report_content = f"""# REPORT: {finding['type']} in {target_domain}

## [RESUMEN EJECUTIVO]
Se ha identificado una posible vulnerabilidad de nivel **{finding['severity']}** en el activo `{finding['url']}` durante una auditoría web automatizada bajo el ecosistema Gahenax.

- **Tipo**: {finding['type']}
- **Severidad**: {finding['severity']}
- **Estado**: Por verificar manualmente

---

## [ENTORNO Y ALCANCE]
- **Target**: {target_domain}
- **URL Específica**: {finding['url']}
- **Contexto**: Auditoría ética autorizada (Modo White Hat).

---

## [DESCRIPCIÓN TÉCNICA]
{finding.get('description', 'Fallo detectado mediante análisis de patrones de tráfico/plantillas Nuclei.')}

## [EVIDENCIA]
```text
{finding['evidence']}
```

---

## [IMPACTO ESTIMADO]
{finding.get('impact', 'El impacto depende de la sensibilidad de los datos asociados al recurso. Podría derivar en acceso no autorizado o manipulación de estado.')}

---

## [RECOMENDACIÓN DE MITIGACIÓN]
{finding.get('mitigation', 'Implementar validación del lado servidor y controles de integridad consistentes con el principio de mínimo privilegio.')}

---
*Generado por Gahenax OffSec Engine | White Hat Security Foundations Framework*
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f" Reporte generado: {filepath}")
        return str(filepath)

if __name__ == "__main__":
    # Prueba rápida
    reporter = BountyReporter()
    sample_finding = {
        "type": "Insecure Direct Object Reference (IDOR)",
        "severity": "High",
        "url": "https://api.example.com/v1/orders/99827",
        "evidence": "GET /v1/orders/99827 HTTP/1.1 -> Devuelve datos de otro usuario.",
        "impact": "Acceso total a la información de pedidos de cualquier cliente.",
        "mitigation": "Verificar en el backend que el order_id pertenece al account_id del token JWT."
    }
    reporter.generate_report(sample_finding, "example.com")
