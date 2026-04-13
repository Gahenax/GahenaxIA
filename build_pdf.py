import os
import subprocess
import glob

# Rutas
base_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/antigravity_rules"
output_md = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/GahenaxAI_Architectural_Standards.md"
output_pdf = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/GahenaxAI_Architectural_Standards.pdf"
css_file = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/pdf_style.css"

# Lista de archivos en un orden lógico para lectura del cliente
sections = [
    ("web_frameworks.md", "1. Arquitectura Web y Frameworks"),
    ("html_css_core.md", "2. Fundamentos de Web Core (HTML/CSS)"),
    ("javascript_core.md", "3. JavaScript y Motores (V8)"),
    ("styling_systems.md", "4. Sistemas de Estilos (Tailwind/Bootstrap)"),
    ("ui_ux_tooling.md", "5. Integración UX/UI (Figma/Storybook)"),
    ("backend_languages.md", "6. Lenguajes de Backend"),
    ("backend_apis.md", "7. APIs y Protocolos"),
    ("backend_middleware.md", "8. Middleware y Mensajería"),
    ("databases_relational.md", "9. Bases de Datos Relacionales"),
    ("databases_nosql.md", "10. Bases de Datos NoSQL"),
    ("cloud_providers.md", "11. Infraestructura Cloud"),
    ("containers_orchestration.md", "12. Contenedores y Orquestación"),
    ("mobile_native.md", "13. Desarrollo Móvil Nativo"),
    ("mobile_cross_platform.md", "14. Desarrollo Móvil Multiplataforma"),
    ("payment_integrations.md", "15. Arquitectura de Pagos Seguros"),
    ("advanced_architecture_cqrs.md", "16. Patrones Avanzados (CQRS y Event-Driven)"),
    ("advanced_architecture_edge_obs.md", "17. Edge Computing y Observabilidad")
]

# Crear un CSS corporativo y limpio para el PDF
css_content = """
body { font-family: 'Inter', 'Segoe UI', sans-serif; color: #2d3748; line-height: 1.6; padding: 20px; }
h1.title { font-size: 2.5em; text-align: center; color: #1a202c; border-bottom: 3px solid #3182ce; padding-bottom: 20px; margin-top: 100px; }
h1.subtitle { text-align: center; color: #4a5568; font-weight: normal; margin-bottom: 150px; }
h1, h2, h3 { color: #2b6cb0; }
pre, code { background-color: #f7fafc; border-radius: 5px; padding: 2px 5px; }
pre { padding: 10px; border-left: 4px solid #3182ce; }
blockquote { border-left: 4px solid #e2e8f0; padding-left: 15px; color: #4a5568; font-style: italic; }
.page-break { page-break-before: always; }
"""

with open(css_file, "w", encoding="utf-8") as f:
    f.write(css_content)

# Construir el Markdown unificado
print("[+] Combinando Markdowns...")
with open(output_md, "w", encoding="utf-8") as out:
    # Portada oficial
    out.write("<h1 class='title'>GahenaxAI Solutions</h1>\n")
    out.write("<h1 class='subtitle'>Manual de Arquitectura, Heurísticas y Estándares de Ingeniería</h1>\n")
    out.write("<div class='page-break'></div>\n\n")
    
    # Índice o Intro
    out.write("# Introducción\n\n")
    out.write("Este documento empresarial compila todas las heurísticas (`[HEURISTICA-...]`), patrones, anti-patrones y reglas inquebrantables descubiertas e indexadas para asegurar la excelencia en los futuros proyectos tecnológicos de Gahenax. Diseñado para garantizar escalabilidad extrema y prevenir _over-engineering_.\n\n")
    out.write("<div class='page-break'></div>\n\n")

    for filename, section_title in sections:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as sf:
                content = sf.read()
                # Remover primer header si es H1 para no pisar la estética, o simplemente inyectarlo
                out.write(f"<div class='page-break'></div>\n\n")
                out.write(content + "\n\n")
        else:
            print(f"[!] Warning: no se encontró {filename}")

# Ejecutar conversión con Node.js globalmente a través de npx
print("[+] Ejecutando npx md-to-pdf...")
cmd = f'npx --yes md-to-pdf "{output_md}" --stylesheet "{css_file}"'
print(f"Comando: {cmd}")

old_cwd = os.getcwd()
os.chdir(os.path.dirname(output_md))
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
os.chdir(old_cwd)

if result.returncode == 0:
    print(f"\n[+] ÉXITO. PDF generado en: {output_pdf}")
else:
    print("\n[-] Error al generar el PDF.")
    print(result.stdout)
    print(result.stderr)
