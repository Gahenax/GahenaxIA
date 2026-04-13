import os
import markdown

base_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/antigravity_rules"
output_html = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/GahenaxAI_Architectural_Standards.html"

sections = [
    ("web_frameworks.md", "1. Arquitectura Web y Frameworks"),
    ("html_css_core.md", "2. Fundamentos de Web Core (HTML/CSS)"),
    ("javascript_core.md", "3. JavaScript y Motores (V8)"),
    ("styling_systems.md", "4. Sistemas de Estilos (Tailwind/Bootstrap)"),
    ("ui_ux_tooling.md", "5. Integración UX/UI (Figma/Storybook)"),
    ("backend_languages.md", "6. Lenguciones de Backend"),
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

css_styles = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; color: #1a202c; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; background: #fff;}
    .cover { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90vh; text-align: center; }
    h1.title { font-size: 3.5em; color: #000; border-bottom: 4px solid #3182ce; padding-bottom: 20px; font-weight: 700; }
    h2.subtitle { font-size: 1.5em; color: #4a5568; font-weight: 300; margin-top: 20px;}
    .company { margin-top: auto; font-size: 1.2em; color: #a0aec0; letter-spacing: 2px; }
    
    h1 { color: #2b6cb0; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-top: 40px;}
    h2 { color: #2c5282; margin-top: 30px;}
    h3 { color: #2a4365; }
    p { margin-bottom: 15px; }
    
    pre { background-color: #f7fafc; padding: 15px; border-radius: 8px; overflow-x: auto; border-left: 4px solid #3182ce; font-family: "Consolas", monospace; font-size: 0.9em; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    code { background-color: #edf2f7; padding: 2px 5px; border-radius: 4px; font-family: "Consolas", monospace; font-size: 0.9em; color: #c53030;}
    pre code { background-color: transparent; color: inherit; padding: 0;}
    
    blockquote { border-left: 5px solid #cbd5e0; margin: 1.5em 10px; padding: 0.5em 10px; color: #4a5568; background: #fdfdfd; font-style: italic;}
    ul, ol { margin-left: 20px; margin-bottom: 15px; }
    li { margin-bottom: 5px; }
    
    /* Print optimizations */
    @media print {
        body { margin: 0; padding: 0; max-width: 100%; border: none; }
        .page-break { page-break-before: always; }
        .cover { height: 100vh; }
        h1, h2 { page-break-after: avoid; }
        pre, blockquote { page-break-inside: avoid; border: 1px solid #e2e8f0; border-left: 4px solid #3182ce;}
        a { text-decoration: none; color: #000; }
    }
</style>
"""

# Gather raw Markdown
raw_md = ""
for filename, section_title in sections:
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_md += f.read() + "\n\n<div class='page-break'></div>\n\n"

# Convert Markdown to HTML fragments
md_parser = markdown.Markdown(extensions=['fenced_code', 'tables'])
html_content = md_parser.convert(raw_md)

# Build Corporate HTML Container
final_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Manual de Arquitectura - GahenaxAI</title>
    {css_styles}
</head>
<body>
    <div class="cover page-break">
        <h1 class="title">Bases de Datos de Arquitectura GahenaxAI</h1>
        <h2 class="subtitle">Directrices, Heurísticas y Estándares de Ingeniería (Aprobado para Clientes)</h2>
        <div class="company">PROPIEDAD INTELECTUAL DE GAHENAX AI SOLUTIONS</div>
    </div>
    
    <div class="page-break">
        <h1>Introducción Ejecutiva</h1>
        <p>Este documento es la compilación oficial de ingeniería y arquitectura que dictan los cimientos tecnológicos de <b>GahenaxAI</b>. Contiene el análisis de ecosistemas, patrones <i>anti-patterns</i> y nuestra colección de heurísticas (Leyes Áureas) que nos garantizan la máxima escalabilidad y la evasión de sobre-ingeniería en entornos empresariales.</p>
        <p><i>Nota: Puede presionar (Ctrl+P) o (Cmd+P) en su navegador web para imprimir este documento como una versión PDF corporativa inmaculada.</i></p>
    </div>
    
    <div class="page-break"></div>
    {html_content}
</body>
</html>
"""

print("[+] Generando reporte final en HTML...")
with open(output_html, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"[+] ÉXITO: {output_html} compilado exitosamente.")
