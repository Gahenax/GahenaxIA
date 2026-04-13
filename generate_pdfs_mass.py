import os
import json
import markdown
import logging
from xhtml2pdf import pisa

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

search_dirs = [
    r"c:/Users/jotam/OneDrive/Desktop/Tesis",
    r"c:/Users/jotam/OneDrive/Desktop/Wellness/Workspace1"
]
output_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/OEDA_All_Research_PDF"
os.makedirs(output_dir, exist_ok=True)

skip_dirs = {'node_modules', '.git', '.agent', 'venv', '__pycache__', 'dist', 'build', 'artifacts', '.vscode'}

css_styles = """
<style>
    @page { size: A4; margin: 2cm; }
    body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #333; line-height: 1.5; word-wrap: break-word;}
    h1 { color: #2b6cb0; font-size: 16pt; border-bottom: 2px solid #3182ce; padding-bottom: 5px; margin-top: 15px; }
    h2 { color: #2c5282; font-size: 13pt; margin-top: 15px; }
    h3 { color: #2a4365; font-size: 11pt; margin-top: 10px; }
    pre { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #3182ce; font-family: "Courier New", monospace; font-size: 8pt; white-space: pre-wrap; word-wrap: break-word;}
    code { background-color: #f1f3f5; font-family: "Courier New", monospace; color: #c53030; font-size: 8pt; padding: 2px;}
    blockquote { border-left: 4px solid #cbd5e0; margin-left: 0; padding-left: 15px; color: #666; font-style: italic; background-color: #fdfdfd; padding: 10px; }
    .cover { margin-top: 30%; text-align: center;}
    .title { font-size: 20pt; color: #111; font-weight: bold; margin-bottom: 10px; word-wrap: break-word;}
    .subtitle { font-size: 12pt; color: #555; margin-bottom: 50px;}
    .company { font-size: 9pt; color: #999; letter-spacing: 2px; margin-top: 100px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    th { background-color: #f1f3f5; text-align: left; padding: 8px; border-bottom: 2px solid #dee2e6; color: #333; }
    td { padding: 8px; border-bottom: 1px solid #e9ecef; color: #555; }
    .sources { margin-top: 40px; border-top: 2px solid #e2e8f0; padding-top: 20px; }
    .sources h2 { color: #555; font-size: 12pt; }
    .sources ul { list-style-type: square; color: #666; font-size: 9pt; }
</style>
"""

md_parser = markdown.Markdown(extensions=['fenced_code', 'tables'])

def convert_to_pdf(content_md, title_text, pdf_filename):
    pdf_path = os.path.join(output_dir, pdf_filename)
    html_body = md_parser.convert(content_md)
    
    sources_html = "<div class='sources'><h2>Fuentes y Origen de Datos</h2><ul>"
    sources_html += "<li>Laboratorio OEDA (Observatory of Empirical Data & Algorithms)</li>"
    sources_html += "<li>Telemetría Empírica y Pipelines de Ejecución generados y curados por GahenaxAI</li>"
    sources_html += "<li>Registros Forenses Inmutables de Nodos de Cálculo Local y Serverless (Jules Protocol / Gahenax Core)</li>"
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
            <div class="subtitle">Investigación, Experimentos y Data Sets (OEDA)</div>
            <div class="company">PROPIEDAD DE GAHENAX AI SOLUTIONS</div>
        </div>
        <pdf:nextpage />
        {html_body}
        {sources_html}

        <pdf:nextpage />
        <div class="sources" style="border-top: none; margin-top: 50%; text-align: center;">
            <h2 style="color: #2b6cb0; border-bottom: 2px solid #3182ce; padding-bottom: 10px; display: inline-block;">Gated Access & B2B Integration</h2>
            <br><br>
            <p style="font-size: 11pt; color: #4a5568; line-height: 1.6;">
            <strong>El Dataset Completo Crudo (JSON/CSV), el Código del Rasterizador y los Modelos Matemáticos que generaron este snapshot son retenidos bajo secreto industrial de GahenaxAI.</strong><br><br>
            Las trazas, logs experimentales o código forense mostrados en este documento público sirven solo como prueba autoritaria de ejecución y resultados empíricos.<br><br>
            Para Agencias, Consultoras e Inversores que requieran poseer y operar el motor <strong>Gahenax OEDA Engine</strong> de primera mano en sus instalaciones comerciales:<br><br>
            <span style="font-size: 14pt; font-weight: bold; color: #c53030;">[ REQUEST CORE ACCESS ]</span><br><br>
            <i>Contactar formalmente a GahenaxAI Solutions para adquirir una licencia Premium Enterprise del Crawler y las Bases de Datos Maestras completas.</i>
            </p>
        </div>
    </body>
    </html>
    """
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(src=final_html, dest=pdf_file, encoding='utf-8')
    return pisa_status.err == 0

def process_file(filepath):
    filename = os.path.basename(filepath)
    parent_dir = os.path.basename(os.path.dirname(filepath))
    
    clean_name = f"{parent_dir}_{filename}".replace('.md', '').replace('.json', '').replace('.txt', '')
    pdf_filename = f"{clean_name}.pdf"

    try:
        if filename.endswith('.md'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            title = filename.replace('.md', '').replace('_', ' ').title()
            success = convert_to_pdf(content, title, pdf_filename)
            if success:
                logging.info(f"[+] Generado y referenciado: {pdf_filename}")
            else:
                logging.error(f"[-] Error en {pdf_filename}")
                
        elif filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pretty_json = json.dumps(data, indent=2)
            lines = pretty_json.split('\\n')
            if len(lines) > 2000:
                pretty_json = '\\n'.join(lines[:2000]) + "\\n... [DATASET TRUNCADO POR LONGITUD PARA PDF - REFERIRSE AL ORIGEN PARA COMPLETITUD] ..."
            
            content_md = f"# Dataset: {filename}\\n\\n```json\\n{pretty_json}\\n```\\n"
            title = filename.replace('.json', '').replace('_', ' ').title() + " Dataset"
            success = convert_to_pdf(content_md, title, pdf_filename)
            if success:
                logging.info(f"[+] Generado y referenciado (Dataset): {pdf_filename}")
            else:
                logging.error(f"[-] Error en dataset {pdf_filename}")
                
    except Exception as e:
        pass

logging.info(f"[*] Iniciando RE-rastreo y conversión masiva OEDA (con Fuentes Inyectadas) -> PDF en: {output_dir}")

for sdir in search_dirs:
    for root, dirs, files in os.walk(sdir):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith('.md') or file.endswith('.json'):
                if file in ['package.json', 'tsconfig.json', 'search_results.json', 'repo_health_report.json']:
                    continue
                filepath = os.path.join(root, file)
                process_file(filepath)

logging.info("[*] Conversión masiva y citación completada.")
