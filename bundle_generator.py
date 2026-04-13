import os
import shutil
import zipfile

# Directorios Origen
pdf_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/OEDA_Proyectos_PDF"  # Example source of Tier 1
pdf_all_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/OEDA_All_Research_PDF"
code_dir = r"c:/Users/jotam/OneDrive/Desktop/Wellness/Workspace1/OEDA_Riemann_Atlas" # Target Project to bundle

# Directorio Salida (La "tienda" local)
bundle_dir = r"c:/Users/jotam/OneDrive/Desktop/GahenaxAI/Products/Riemann_Atlas_Product"
os.makedirs(bundle_dir, exist_ok=True)

# 1. Definir los Textos de las Licencias Universales OEDA / Gahenax
license_tier1_text = """
GAHENAX AI SOLUTIONS - RESEARCH NOTE (TIER 1)
---------------------------------------------
Este documento (Paper/PDF) se provee estrictamente con fines informativos, académicos y de pre-venta.
Propiedad Intelectual de GahenaxAI. Queda prohibida la reventa, reproducción, alteración
o distribución masiva sin permiso escrito explícito.
"""

license_tier2_text = """
GAHENAX AI SOLUTIONS - EXPERIMENTAL ENGINE DEMO (TIER 2)
--------------------------------------------------------
LIMITED NON-COMMERCIAL LICENSE (CC BY-NC-ND)

Esta versión limitada del 'Gahenax Experimental Engine' se entrega a usted para fines de auditoría 
técnica, educación y experimentación personal.

USTED NO PUEDE:
- Utilizar este motor en un entorno de producción B2B comercial.
- Monetizar APIs generadas en base a este código.
- Revender o hacer *fork* del código base de Gahenax.

Contiene datasets truncados intencionalmente y funciones de concurrencia limitadas como demostración.
"""

license_tier3_text = """
GAHENAX AI SOLUTIONS - FULL PREMIUM ENGINE (TIER 3)
---------------------------------------------------
COMMERCIAL USE LICENSE & ARCHITECTURE PORT

Con la adquisición de este nivel 'Full Expert', se le otorga una licencia B2B perpetua, 
no exclusiva e intransferible para implementar este motor en su propia infraestructura 
privada o comercial.

USTED PUEDE:
- Modificar el código fuente interno sin restricciones para adaptar su aplicación de usuario final.
- Desplegar el sistema en servidores en Producción (AWS, Cloudflare, etc.).
- Procesar volumen de datos real con fines comerciales.

USTED NO PUEDE:
- Vender el código crudo de GahenaxAI a otras agencias de forma directa ("reselling the engine").
- Reclamar propiedad intelectual del Algoritmo Original.
"""

def create_zip_tier(zip_name, file_list, license_text):
    zip_path = os.path.join(bundle_dir, zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Añadir todos los archivos
        for item in file_list:
            if os.path.exists(item):
                if os.path.isfile(item):
                    zipf.write(item, os.path.basename(item))
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        # Filter out heavy git nodes or caches
                        if '.git' in root or '__pycache__' in root:
                            continue
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(item))
                            zipf.write(file_path, arcname)
        # Añadir la licencia on-the-fly
        zipf.writestr("LICENSE.txt", license_text)
    print(f"[+] Generado Bundle: {zip_path}")


print("[*] Empaquetando Producto Digital: Riemann Atlas Experimental Engine")

# TIER 1: The Paper
tier1_files = [
    os.path.join(pdf_dir, "OEDA_Riemann_Atlas_Client_Report.pdf")
]
create_zip_tier("Tier1_Riemann_Paper_Authority.zip", tier1_files, license_tier1_text)

# TIER 2: The Demo Limited
# Includes the PDF + A limited view of the code (Only the execution scripts, not the datasets or specific deep logic folders if possible, or we just ship a 'demo' markdown script instead of the full thing)
tier2_files = tier1_files + [
    os.path.join(code_dir, "README_FIRST.md"),
    os.path.join(code_dir, "methodology") # the methodology is public proof
]
create_zip_tier("Tier2_Riemann_Engine_Demo.zip", tier2_files, license_tier2_text)

# TIER 3: The Full Premium Engine
# Includes everything + full code + huge datasets
huge_dataset = os.path.join(pdf_all_dir, "OEDA_CalculoIA_ALL_ZEROS_FINAL.pdf") # Demo large dataset integration
tier3_files = tier1_files + [
    code_dir, # Todo el código crudo fuente de OEDA_Riemann_Atlas
    huge_dataset # El dataset gigante de millones de ceros que no entra en la demo
]
create_zip_tier("Tier3_Riemann_Engine_Premium_B2B.zip", tier3_files, license_tier3_text)

print("[*] Todos los tiers y licencias han sido empaquetados exitosamente.")
