# GAHENAX OFFSEC: MAPA TÁCTICO DE HACKING

Esta es la hoja de ruta estratégica para auditorías de precisión y pruebas de penetración.

---

### **FASE 1: FUNDAMENTOS Y RECONOCIMIENTO (The Cartography Phase)**
*   **OSINT (Pasivo):** `subfinder`, `amass`, `assetfinder` (Subdominios), `Shodan`, `Censys` (Infraestructura), `Wappalyzer` (Fingerprinting).
*   **Activo:** `nmap` (Escaneo de puertos), `ffuf`, `gobuster` (Enumeración), `Burp Suite` (Mapeo manual).

---

### **FASE 2: VULNERABILIDADES WEB (The Core Battlefield)**
*   **Inyecciones:** SQLi (`sqlmap`), XSS (Reflejado, Almacenado, DOM), Command Injection.
*   **Lógica de Negocio:** IDOR (Insecure Direct Object Reference), Race Conditions (Turbo Intruder), Broken Access Control.
*   **Críticas:** SSRF (Server-Side Request Forgery), SSTI (Template Injection), Insecure Deserialization (`ysoserial`).

---

### **FASE 3: VULNERABILIDADES DE RED Y SISTEMA**
*   **Explotación:** Servicios obsoletos (EternalBlue, BlueKeep), `searchsploit`.
*   **Contraseñas:** Fuerza bruta y diccionario (`Hydra`, `Medusa`, `rockyou.txt`).
*   **MitM:** ARP Spoofing (`Bettercap`, `Ettercap`).

---

### **FASE 4: TÉCNICAS AVANZADAS Y POST-EXPLOTACIÓN**
*   **PrivEsc:** `LinPEAS` / `WinPEAS`, SUID bits, `Mimikatz`.
*   **Persistencia:** Cronjobs, Scheduled Tasks, SSH keys, Backdoors.
*   **Evasión:** Bypass de AV/EDR/WAF.

---
*Referencia táctica para el mentor Gahenax AI.*
