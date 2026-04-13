import os
import paramiko
from scp import SCPClient
import sys

# --- CONFIGURATION ---
HOST = "151.106.106.26"
PORT = 65002
USER = "u314799704"
KEY_PATH = r"c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax-nexus\.ssh\gahenax_nexus_id"
LOCAL_DIR = r"c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax-nexus\out"

def deploy(dry_run=True):
    print(f"--- Intentando conectar a {HOST}:{PORT} como {USER}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Authentication with Private Key
        k = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)
        ssh.connect(HOST, port=PORT, username=USER, pkey=k)
        print("OK: Autenticación con llave SSH exitosa.")
        
        # 1. Path Discovery & Safety Check
        stdin, stdout, stderr = ssh.exec_command("pwd && ls -F")
        current_path = stdout.read().decode().strip()
        print(f"--- Ruta actual en servidor: {current_path}")
        
        # Look for gahenaxaisolutions.com directory
        stdin, stdout, stderr = ssh.exec_command("find . -maxdepth 3 -name 'gahenaxaisolutions.com' -type d")
        found_path = stdout.read().decode().strip()
        
        if not found_path:
            # Maybe it's the primary domain in public_html
            target_path = "public_html"
            print(f"⚠️ No se encontró carpeta 'gahenaxaisolutions.com', asumiendo dominio principal en: {target_path}")
        else:
            target_path = os.path.join(found_path, "public_html").replace("\\", "/")
            print(f"--- Carpeta del dominio encontrada: {target_path}")

        # List target content for verification
        stdin, stdout, stderr = ssh.exec_command(f"ls -F {target_path}")
        remote_files = stdout.read().decode().strip()
        print(f"\n--- Contenido remoto actual en {target_path}:")
        print(remote_files if remote_files else "(vacio)")

        if dry_run:
            print("\n--- MODO DRY RUN: No se han realizado cambios.")
            print("Verifica si la lista de arriba corresponde a Gahenax y no a otro proyecto.")
            return

        # 2. Deployment logic
        if "--purge" in sys.argv:
            print(f"\n--- PURGA NUCLEAR: Borrando contenido en {target_path}...")
            # We don't delete the public_html itself, just its content
            ssh.exec_command(f"find {target_path} -mindepth 1 -delete")
            print("--- Servidor purgado (Zero-Debt).")

        print(f"\n--- Iniciando despliegue en {target_path}...")
        
        with SCPClient(ssh.get_transport()) as scp:
            # Upload directory contents
            for item in os.listdir(LOCAL_DIR):
                full_path = os.path.join(LOCAL_DIR, item)
                print(f"  UP: Subiendo: {item}")
                scp.put(full_path, recursive=True, remote_path=target_path)

        print("\n[OK] DESPLIEGUE SSH COMPLETADO [OK]")

    except Exception as e:
        print(f"ERR: Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    is_dry = "--confirm" not in sys.argv
    deploy(dry_run=is_dry)
