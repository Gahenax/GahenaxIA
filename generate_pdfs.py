import os
import markdown
from xhtml2pdf import pisa

base_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/antigravity_rules"
output_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/Bases_de_Datos_PDF"
os.makedirs(output_dir, exist_ok=True)

sources_map = {
    "advanced_architecture_cqrs": ["Martin Fowler - CQRS Pattern", "Microsoft Azure Architecture Center - Event Sourcing", "Greg Young - CQRS Documents"],
    "advanced_architecture_edge_obs": ["OpenTelemetry.io Official Documentation", "Cloudflare Workers Docs", "Vercel Edge Network Architecture", "Prometheus & Grafana Labs"],
    "backend_apis": ["REST API Tutorial", "GraphQL.org Foundation", "gRPC Official Documentation (CNCF)", "OpenAPI Specification"],
    "backend_languages": ["Python.org / PEP 8", "Node.js Technical Steering Committee", "Go.dev Documentation", "Rust Lang Foundation"],
    "backend_middleware": ["Apache Kafka Documentation", "RabbitMQ Official Guides", "Redis.io Architecture"],
    "cloud_providers": ["AWS Well-Architected Framework", "Google Cloud Architecture Center", "Azure Architecture Center", "HashiCorp Terraform Docs"],
    "containers_orchestration": ["Kubernetes.io (CNCF)", "Docker Official Documentation", "Helm best practices"],
    "databases_nosql": ["MongoDB Architecture Guide", "Redis Documentation", "Cassandra Apache Foundation"],
    "databases_relational": ["PostgreSQL Global Development Group", "MySQL Reference Manual", "ACID Properties in RDBMS"],
    "html_css_core": ["MDN Web Docs (Mozilla)", "W3C HTML5/CSS3 Specifications", "WHATWG HTML Standard"],
    "javascript_core": ["MDN Web Docs - JavaScript", "ECMAScript Language Specification (TC39)", "V8 Engine Documentation"],
    "mobile_cross_platform": ["React Native Official Documentation (Meta)", "Flutter Architectural Overview", "Dart Language Tour"],
    "mobile_native": ["Apple Developer Documentation (Swift/iOS)", "Android Developers (Kotlin)", "Material Design Guidelines"],
    "payment_integrations": ["Stripe API Documentation", "PayPal Developer Portal", "PCI-DSS Compliance Standards"],
    "styling_systems": ["Tailwind CSS Documentation", "Bootstrap Core Concepts", "CSS Modules Specification"],
    "ui_ux_tooling": ["Figma Best Practices", "Storybook Documentation", "Nielsen Norman Group - UX Guidelines"],
    "web_frameworks": ["React.js Official Docs", "Next.js Architecture (Vercel)", "Vue.js Guide", "Svelte.dev documentation"]
}

css_styles = """
<style>
    @page { size: A4; margin: 2cm; }
    body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #2d3748; line-height: 1.5; }
    h1 { color: #2b6cb0; font-size: 18pt; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-top: 20px; }
    h2 { color: #2c5282; font-size: 14pt; margin-top: 15px; }
    pre { background-color: #f7fafc; padding: 10px; border-left: 4px solid #3182ce; font-family: "Courier New", monospace; font-size: 9pt; white-space: pre-wrap; word-wrap: break-word;}
    code { background-color: #edf2f7; font-family: "Courier New", monospace; color: #c53030; }
    blockquote { border-left: 4px solid #cbd5e0; margin-left: 0; padding-left: 15px; color: #4a5568; font-style: italic; }
    .cover { margin-top: 30%; text-align: center;}
    .title { font-size: 24pt; color: #1a202c; font-weight: bold; margin-bottom: 10px;}
    .subtitle { font-size: 14pt; color: #4a5568; margin-bottom: 50px;}
    .company { font-size: 10pt; color: #a0aec0; letter-spacing: 2px; margin-top: 100px; }
    .sources { margin-top: 40px; border-top: 2px solid #e2e8f0; padding-top: 20px; }
    .sources h2 { color: #4a5568; font-size: 14pt; }
    .sources ul { list-style-type: square; color: #4a5568; font-size: 10pt; }
</style>
"""

md_parser = markdown.Markdown(extensions=['fenced_code', 'tables'])

print(f"[*] Iniciando conversión Markdown -> PDF en el directorio: {output_dir}")

for filename in os.listdir(base_dir):
    if not filename.endswith('.md'):
        continue
    
    filepath = os.path.join(base_dir, filename)
    pdf_filename = filename.replace('.md', '.pdf')
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        raw_md = f.read()
    
    html_body = md_parser.convert(raw_md)
    
    # Title extraction for cover cleanly
    core_name = filename.replace('.md', '')
    title_text = core_name.replace('_', ' ').title()
    if 'Html Css' in title_text: title_text = title_text.replace('Html Css', 'HTML CSS')
    if 'Ui Ux' in title_text: title_text = title_text.replace('Ui Ux', 'UX/UI')
    
    sources_html = ""
    if core_name in sources_map:
        sources_html = "<div class='sources'><h2>Bibliografía y Referencias Oficiales</h2><ul>"
        for src in sources_map[core_name]:
            sources_html += f"<li>{src}</li>"
        sources_html += "<li>Manuales Arquitectónicos y Metadatos de Repositorios Oficiales (GitHub/GitLab)</li>"
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
            <div class="subtitle">Directrices y Estándares de Ingeniería</div>
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
            <strong>El Motor Experimental (Código Completo, Datasets Crudos y Arquitecturas Ejecutables) que respalda esta investigación no es de dominio público para evitar usos maliciosos o implementaciones no-reguladas.</strong><br><br>
            Para firmas analíticas, agencias, laboratorios privados o individuos que requieran replicar o integrar el <strong>Gahenax Engine</strong> en su propia infraestructura B2B:<br><br>
            <span style="font-size: 14pt; font-weight: bold; color: #c53030;">[ REQUEST CORE ACCESS ]</span><br><br>
            <i>Por favor, contacte a GahenaxAI Solutions con su caso de uso y le evaluaremos la viabilidad técnica para emitir una cotización personalizada de licenciamiento Full-Premium de esta tecnología.</i>
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
        print(f"[+] Generado y referenciado: {pdf_filename}")

print("[*] Proceso finalizado.")
