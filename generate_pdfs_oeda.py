import os
import markdown
from xhtml2pdf import pisa

files_to_convert = [
    (r"c:/Users/jotam/OneDrive/Desktop/Wellness/Workspace1/Mersenne_Gap_Observatory/README_FIRST.md", "Reporte de Observatorio de Gaps de Mersenne"),
    (r"c:/Users/jotam/OneDrive/Desktop/Wellness/Workspace1/OEDA_HodgeRigidity/README.md", "Reporte de Rigidez de Hodge & Yang-Mills"),
    (r"c:/Users/jotam/OneDrive/Desktop/Wellness/Workspace1/OEDA_Riemann_Atlas/README_FIRST.md", "Atlas Topológico de Ceros de Riemann")
]

output_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/OEDA_Proyectos_PDF"
os.makedirs(output_dir, exist_ok=True)

oeda_sources = {
    "Mersenne_Gap_Observatory": ["Great Internet Mersenne Prime Search (GIMPS) Archives", "Distribuciones del Teorema de los Números Primos", "GahenaxAI OEDA Lab - Telemetría Empírica Ouroboros"],
    "OEDA_HodgeRigidity": ["Conjetura de Hodge - Clay Mathematics Institute", "Existencia de Yang-Mills y Brecha de Masa (Mass Gap) - CMI", "GahenaxAI OEDA - Simulaciones Topológicas de Rigidez"],
    "OEDA_Riemann_Atlas": ["Bernhard Riemann (1859): Sobre el número de primos menores que una magnitud dada", "Teoría de Matrices Aleatorias GUE (Gaussian Unitary Ensemble)", "GahenaxAI OEDA - Análisis Espectral de Ceros y Patrones de Interferencia"]
}

css_styles = """
<style>
    @page { size: A4; margin: 2cm; }
    body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #2d3748; line-height: 1.5; }
    h1 { color: #2b6cb0; font-size: 18pt; border-bottom: 2px solid #3182ce; padding-bottom: 5px; margin-top: 20px; }
    h2 { color: #2c5282; font-size: 14pt; margin-top: 15px; }
    h3 { color: #2a4365; font-size: 12pt; margin-top: 10px; }
    pre { background-color: #f7fafc; padding: 10px; border-left: 4px solid #3182ce; font-family: "Courier New", monospace; font-size: 8pt; white-space: pre-wrap; word-wrap: break-word;}
    code { background-color: #edf2f7; font-family: "Courier New", monospace; color: #c53030; font-size: 9pt; }
    blockquote { border-left: 4px solid #cbd5e0; margin-left: 0; padding-left: 15px; color: #4a5568; font-style: italic; background-color: #fdfdfd; padding: 10px; }
    .cover { margin-top: 30%; text-align: center;}
    .title { font-size: 24pt; color: #1a202c; font-weight: bold; margin-bottom: 10px;}
    .subtitle { font-size: 14pt; color: #4a5568; margin-bottom: 50px;}
    .company { font-size: 10pt; color: #a0aec0; letter-spacing: 2px; margin-top: 100px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    th { background-color: #edf2f7; text-align: left; padding: 8px; border-bottom: 2px solid #cbd5e0; color: #2d3748; }
    td { padding: 8px; border-bottom: 1px solid #e2e8f0; color: #4a5568; }
    .sources { margin-top: 40px; border-top: 2px solid #e2e8f0; padding-top: 20px; }
    .sources h2 { color: #4a5568; font-size: 14pt; }
    .sources ul { list-style-type: square; color: #4a5568; font-size: 10pt; }
</style>
"""

md_parser = markdown.Markdown(extensions=['fenced_code', 'tables'])

print(f"[*] Iniciando conversión Markdown -> PDF con Fuentes OEDA en: {output_dir}")

for filepath, title_text in files_to_convert:
    if not os.path.exists(filepath):
        print(f"[!] Archivo no encontrado: {filepath}")
        continue
        
    project_dir = os.path.basename(os.path.dirname(filepath))
    pdf_filename = project_dir + "_Client_Report.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        raw_md = f.read()
    
    html_body = md_parser.convert(raw_md)
    
    sources_html = ""
    if project_dir in oeda_sources:
        sources_html = "<div class='sources'><h2>Fuentes Matemáticas y Empíricas</h2><ul>"
        for src in oeda_sources[project_dir]:
            sources_html += f"<li>{src}</li>"
        sources_html += "</ul></div>"

    final_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        {css_styles}
    </head>
    <body>
        <div class="cover">
            <div class="title">{title_text}</div>
            <div class="subtitle">Investigación Matemática y Análisis de Datos (OEDA)</div>
            <div class="company">PROPIEDAD DE GAHENAX AI SOLUTIONS</div>
        </div>
        <pdf:nextpage />
        {html_body}
        {sources_html}

        <pdf:nextpage />
        <div class="sources" style="border-top: none; margin-top: 50%; text-align: center;">
            <h2 style="color: #2b6cb0; border-bottom: 2px solid #3182ce; padding-bottom: 10px; display: inline-block;">Gated Access & Commercial Licensing</h2>
            <br><br>
            <p style="font-size: 11pt; color: #4a5568; line-height: 1.6;">
            <strong>Los Algoritmos de Búsqueda de Espectros, Motores Computacionales y Telemetrías Completas de OEDA que respaldan este informe no son de dominio público.</strong><br><br>
            Para instituciones de investigación, fondos de inversión (HFT) o laboratorios privados que requieran ejecutar los simuladores cuánticos y/o el motor <strong>Gahenax OEDA Engine</strong>:<br><br>
            <span style="font-size: 14pt; font-weight: bold; color: #c53030;">[ REQUEST CORE ACCESS ]</span><br><br>
            <i>Por favor, contacte a GahenaxAI Solutions con la naturaleza de su investigación para agendar una consultoría B2B y acceder al licenciamiento técnico.</i>
            </p>
        </div>
    </body>
    </html>
    """
    
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(src=final_html, dest=pdf_file, encoding='utf-8')
        
    if pisa_status.err:
        print(f"[-] Error generando {pdf_filename}")
    else:
        print(f"[+] Generado con fuentes: {pdf_filename}")

print("[*] Proceso OEDA referenciado finalizado.")
