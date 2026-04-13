#!/usr/bin/env python3
"""
CSP Hasher - Post-build hashing pipeline para gahenaxaisolutions.com
Genera SHA-256 hashes de scripts/styles inline y actualiza .htaccess
Protocolo: Gahenax AI - La honestidad técnica no se negocia
"""

import hashlib
import base64
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

class InlineHashParser(HTMLParser):
    """Extrae scripts y styles inline del HTML renderizado"""
    
    def __init__(self):
        super().__init__()
        self.script_hashes = []
        self.style_hashes = []
        self.in_script = False
        self.in_style = False
        self.script_content = ""
        self.style_content = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            # Ignorar scripts remotos, solo procesar inline
            has_src = any(k == "src" for k, v in attrs)
            if not has_src:
                self.in_script = True
                self.script_content = ""
        elif tag == "style":
            self.in_style = True
            self.style_content = ""
    
    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.in_script = False
            if self.script_content.strip():
                hash_b64 = self._calculate_hash(self.script_content)
                self.script_hashes.append(hash_b64)
        elif tag == "style" and self.in_style:
            self.in_style = False
            if self.style_content.strip():
                hash_b64 = self._calculate_hash(self.style_content)
                self.style_hashes.append(hash_b64)
    
    def handle_data(self, data):
        if self.in_script:
            self.script_content += data
        elif self.in_style:
            self.style_content += data
    
    @staticmethod
    def _calculate_hash(content):
        """Calcula SHA-256 en formato base64 (requerido por CSP spec)"""
        # Normalizar: remover espacios en blanco excesivos pero preservar estructura
        content_bytes = content.encode('utf-8')
        sha256_hash = hashlib.sha256(content_bytes).digest()
        return base64.b64encode(sha256_hash).decode('utf-8')
    
    def get_hashes(self):
        return {
            'scripts': self.script_hashes,
            'styles': self.style_hashes
        }


def generate_csp_header(script_hashes, style_hashes):
    """Genera un CSP segura sin unsafe-inline/unsafe-eval"""
    
    script_src = "'self'"
    if script_hashes:
        script_src += " " + " ".join(f"'sha256-{h}'" for h in script_hashes)
    
    style_src = "'self'"
    if style_hashes:
        style_src += " " + " ".join(f"'sha256-{h}'" for h in style_hashes)
    
    csp = (
        f"default-src 'self'; "
        f"script-src {script_src}; "
        f"style-src {style_src}; "
        f"img-src 'self' data: https:; "
        f"font-src 'self' data: https:; "
        f"connect-src 'self'; "
        f"frame-ancestors 'none'; "
        f"object-src 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self';"
    )
    
    return csp


def update_htaccess(htaccess_path, csp_header):
    """Actualiza el archivo .htaccess con la CSP nueva"""
    
    if not htaccess_path.exists():
        print(f"ERROR: {htaccess_path} no existe")
        return False
    
    try:
        with open(htaccess_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para reemplazar la línea CSP existente (sin importar unsafe-inline o previas configuraciones largas)
        csp_pattern = r'Header set Content-Security-Policy "[^"]*"'
        csp_line = f'Header set Content-Security-Policy "{csp_header}"'
        
        if re.search(csp_pattern, content):
            new_content = re.sub(csp_pattern, csp_line, content)
        else:
            # Si no existe, insertarla después de X-Content-Type-Options
            new_content = re.sub(
                r'(Header set X-Content-Type-Options "nosniff")',
                f'\\1\n  Header set Content-Security-Policy "{csp_header}"',
                content
            )
        
        with open(htaccess_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"ok .htaccess actualizado con CSP segura")
        return True
    
    except Exception as e:
        print(f"ERROR al actualizar .htaccess: {e}")
        return False


def main():
    """Pipeline principal"""
    
    # Configuración de rutas (Ajustado para modificar sobre out/.htaccess directamente)
    html_path = Path("out/index.html")
    htaccess_path = Path("out/.htaccess")
    
    # Verificar que index.html existe (generado por Next.js static export)
    if not html_path.exists():
        print(f"❌ ERROR: {html_path} no existe")
        print("   Ejecutar: npm run build")
        sys.exit(1)
    
    print("Analizando HTML renderizado...")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extraer hashes
        parser = InlineHashParser()
        parser.feed(html_content)
        hashes = parser.get_hashes()
        
        script_count = len(hashes['scripts'])
        style_count = len(hashes['styles'])
        
        print(f"   - Scripts inline encontrados: {script_count}")
        print(f"   - Styles inline encontrados: {style_count}")
        
        if script_count == 0 and style_count == 0:
            print("ADVERTENCIA: No se encontraron scripts/styles inline")
            print("   (Esto es normal si Next.js externaliza todo a archivos)")
        
        # Generar CSP
        print("Generando CSP segura...")
        csp_header = generate_csp_header(hashes['scripts'], hashes['styles'])
        
        # Mostrar preview
        print(f"\nCSP generada (primeros 150 chars):")
        print(f"   {csp_header[:150]}...")
        
        # Actualizar .htaccess de "out" para deploy
        print(f"\nActualizando {htaccess_path}...")
        if update_htaccess(htaccess_path, csp_header):
            # También actualizamos public/.htaccess para que quede perpetuo
            update_htaccess(Path("public/.htaccess"), csp_header)
            
            print(f"\nEXITO: Pipeline completado")
            print(f"   - CSP sin unsafe-inline/unsafe-eval [OK]")
            print(f"   - .htaccess actualizado [OK]")
            print(f"\nProximos pasos:")
            print(f"   1. Hacer git commit de los cambios")
            print(f"   2. Hacer deploy a Hostinger")
            print(f"   3. Verificar CSP en browser: DevTools -> Network -> Response Headers")
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        print(f"ERROR durante el pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
