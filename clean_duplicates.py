import os
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        return None

def main():
    base_dir = Path(r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\Repos_Auditoria")
    mersenne_dir = base_dir / "Mersenne-Gahen"
    riemann_dir = base_dir / "Riemman-Zero"

    print(f"[*] Escaneando fuente de la verdad: {mersenne_dir.name}")
    mersenne_hashes = {}
    for root, dirs, files in os.walk(mersenne_dir):
        if 'venv' in root or 'node_modules' in root or '.git' in root or '.agent' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                file_hash = get_file_hash(filepath)
                if file_hash:
                    mersenne_hashes[file_hash] = filepath

    print(f"[+] Archivos de Python indexados en Mersenne-Gahen: {len(mersenne_hashes)}")
    
    print(f"\n[*] Escaneando y purgando duplicados en: {riemann_dir.name}")
    deleted_count = 0
    for root, dirs, files in os.walk(riemann_dir, topdown=False):
        if 'venv' in root or 'node_modules' in root or '.git' in root or '.agent' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                file_hash = get_file_hash(filepath)
                
                if file_hash and file_hash in mersenne_hashes:
                    # Duplicate found
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"  [-] Eliminado (Clon exacto): {filepath.relative_to(riemann_dir)}")
                    except Exception as e:
                        print(f"  [!] Error eliminando {filepath}: {e}")
        
        # Clean up empty directories
        try:
            if not os.listdir(root): # if empty
                os.rmdir(root)
                print(f"  [-] Carpeta vacia eliminada: {Path(root).relative_to(riemann_dir)}")
        except Exception:
            pass

    print(f"\n[*] Limpieza completada. Total de scripts duplicados eliminados: {deleted_count}")

if __name__ == "__main__":
    main()
