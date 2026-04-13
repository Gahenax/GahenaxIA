#!/usr/bin/env python3
"""

           GAHENAX AI — ANTIGRAVITY INSTALLER                                 
           Instala las 54 Skills + CLAUDE.md en:                              
             • ~/.claude/              (Claude Code / Cursor / Windsurf)      
             • AppData\Roaming\Claude\ (Claude Desktop app)                  

  USO:                                                                        
    python install_antigravity.py           # Instalación completa            
    python install_antigravity.py --check   # Solo verifica estado            
    python install_antigravity.py --remove  # Desinstala todo                

"""

from __future__ import annotations

import sys
import json
import os
import shutil
import argparse
from pathlib import Path


# 
#  RUTAS
# 

# Fuente: este repositorio GahenaxAI
REPO_ROOT     = Path(__file__).parent.resolve()
SRC_SKILLS    = REPO_ROOT / ".agent" / "skills"
SRC_WORKFLOWS = REPO_ROOT / ".agent" / "workflows"
SRC_CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

# Destino A: carpeta global de Claude Code (aplica a TODOS los proyectos)
CLAUDE_HOME   = Path.home() / ".claude"
DST_SKILLS    = CLAUDE_HOME / "skills"
DST_WORKFLOWS = CLAUDE_HOME / "workflows"
DST_CLAUDE_MD = CLAUDE_HOME / "CLAUDE.md"

# Destino B: Claude Desktop app (GUI)
# Windows: %APPDATA%\Claude\claude_desktop_config.json
_appdata       = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
CLAUDE_DESKTOP = _appdata / "Claude"
DESKTOP_CONFIG = CLAUDE_DESKTOP / "claude_desktop_config.json"


# 
#  COLORES ANSI (para terminal bonita)
# 

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

def ok(msg: str)   -> None: print(f"  {C.GREEN} {msg}{C.RESET}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}  {msg}{C.RESET}")
def err(msg: str)  -> None: print(f"  {C.RED} {msg}{C.RESET}")
def info(msg: str) -> None: print(f"  {C.CYAN}ℹ  {msg}{C.RESET}")
def dim(msg: str)  -> None: print(f"  {C.DIM}{msg}{C.RESET}")


# 
#  INSTALACIÓN
# 

def install_skills() -> tuple[int, int]:
    """
    Copia cada SKILL.md de .agent/skills/<nombre>/SKILL.md
    a ~/.claude/skills/<nombre>/SKILL.md

    Retorna (instaladas, omitidas)
    """
    if not SRC_SKILLS.exists():
        err(f"No se encontró la carpeta de skills: {SRC_SKILLS}")
        return 0, 0

    DST_SKILLS.mkdir(parents=True, exist_ok=True)
    installed: int = 0
    skipped: int = 0

    skill_dirs = sorted(SRC_SKILLS.iterdir())

    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            continue

        src_md = skill_dir / "SKILL.md"
        if not src_md.exists():
            warn(f"Sin SKILL.md: {skill_dir.name}/")
            continue

        dst_dir = DST_SKILLS / skill_dir.name
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_md = dst_dir / "SKILL.md"

        # Copia también subcarpetas: scripts/, references/, assets/
        for sub in skill_dir.iterdir():
            if sub.is_dir():
                dst_sub = dst_dir / sub.name
                if dst_sub.exists():
                    shutil.rmtree(dst_sub)
                shutil.copytree(sub, dst_sub)

        shutil.copy2(src_md, dst_md)
        dim(f"  skill: {skill_dir.name}")
        installed += 1

    return installed, skipped


def install_workflows() -> int:
    """
    Copia los 6 workflows de .agent/workflows/*.md
    a ~/.claude/workflows/
    """
    if not SRC_WORKFLOWS.exists():
        warn(f"No se encontró carpeta de workflows: {SRC_WORKFLOWS}")
        return 0

    DST_WORKFLOWS.mkdir(parents=True, exist_ok=True)
    count = 0

    for wf_file in sorted(SRC_WORKFLOWS.glob("*.md")):
        dst = DST_WORKFLOWS / wf_file.name
        shutil.copy2(wf_file, dst)
        dim(f"  workflow: {wf_file.name}")
        count += 1

    return count


def install_claude_md() -> bool:
    """Copia CLAUDE.md a ~/.claude/CLAUDE.md"""
    if not SRC_CLAUDE_MD.exists():
        err(f"CLAUDE.md no encontrado en: {SRC_CLAUDE_MD}")
        return False

    CLAUDE_HOME.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_CLAUDE_MD, DST_CLAUDE_MD)
    return True


def install_claude_desktop() -> bool:
    """
    Configura Claude Desktop app añadiendo un MCP filesystem server
    que expone el directorio de skills de Gahenax.

    Esto permite que Claude Desktop lea los SKILL.md bajo demanda
    sin necesidad de tenerlos en el contexto permanente.
    """
    # Leer config existente o empezar desde cero
    CLAUDE_DESKTOP.mkdir(parents=True, exist_ok=True)

    if DESKTOP_CONFIG.exists():
        try:
            config = json.loads(DESKTOP_CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn("claude_desktop_config.json existe pero tiene JSON inválido — se respaldará")
            shutil.copy2(DESKTOP_CONFIG, DESKTOP_CONFIG.with_suffix(".bak.json"))
            config = {}
    else:
        config = {}

    # Asegurar estructura base
    mcp_servers: dict = config.setdefault("mcpServers", {})

    # MCP server: filesystem sobre skills Gahenax
    # Usa el servidor oficial @modelcontextprotocol/server-filesystem
    mcp_servers["gahenax-skills"] = {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            str(DST_SKILLS),       # expone ~/.claude/skills/
            str(DST_WORKFLOWS),    # expone ~/.claude/workflows/
        ]
    }

    DESKTOP_CONFIG.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return True


def run_install(force: bool = False) -> None:
    print(f"\n{C.BOLD}{C.RESET}")
    print(f"{C.BOLD}    GAHENAX AI — ANTIGRAVITY INSTALLER        {C.RESET}")
    print(f"{C.BOLD}{C.RESET}\n")

    print(f"{C.BOLD} Origen:{C.RESET}   {REPO_ROOT}")
    print(f"{C.BOLD} Claude Code:{C.RESET} {CLAUDE_HOME}")
    print(f"{C.BOLD} Claude Desktop:{C.RESET} {CLAUDE_DESKTOP}\n")

    # 1. CLAUDE.md
    print(f"{C.BOLD} [1/4] CLAUDE.md (memoria persistente global)...{C.RESET}")
    if install_claude_md():
        ok(f"CLAUDE.md → {DST_CLAUDE_MD}")
    print()

    # 2. Skills
    print(f"{C.BOLD} [2/4] Skills (.agent/skills/ → ~/.claude/skills/)...{C.RESET}")
    skills_count, _ = install_skills()
    ok(f"{skills_count} skills instaladas → {DST_SKILLS}")
    print()

    # 3. Workflows
    print(f"{C.BOLD} [3/4] Workflows (.agent/workflows/ → ~/.claude/workflows/)...{C.RESET}")
    wf_count = install_workflows()
    ok(f"{wf_count} workflows instalados → {DST_WORKFLOWS}")
    print()

    # 4. Claude Desktop
    print(f"{C.BOLD} [4/4] Claude Desktop (claude_desktop_config.json)...{C.RESET}")
    if install_claude_desktop():
        ok(f"MCP server 'gahenax-skills' configurado → {DESKTOP_CONFIG}")
        info("Reinicia Claude Desktop para activar los cambios")
    print()

    # Resumen
    print(f"{C.BOLD}{'' * 54}{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}   INSTALACIÓN COMPLETADA{C.RESET}")
    print(f"{C.BOLD}{'' * 54}{C.RESET}")
    print(f"""
  {C.CYAN} Resumen:{C.RESET}
     • ~/.claude/CLAUDE.md       → memoria persistente
     • ~/.claude/skills/         → {skills_count} skills
     • ~/.claude/workflows/      → {wf_count} SOPs
     • AppData\\Roaming\\Claude\\ → MCP server gahenax-skills

  {C.CYAN} Próximos pasos:{C.RESET}
     1. Claude Code / Cursor / Windsurf — skills activas YA
     2. Claude Desktop — reinicia la app para activar el MCP server
     3. Usa /slash-commands para invocar los {wf_count} workflows

  {C.DIM}Para desinstalar: python install_antigravity.py --remove{C.RESET}
""")


# 
#  VERIFICACIÓN
# 

def run_check() -> None:
    print(f"\n{C.BOLD} Estado de Instalación Gahenax AI {C.RESET}\n")

    # CLAUDE.md
    if DST_CLAUDE_MD.exists():
        size_kb = DST_CLAUDE_MD.stat().st_size // 1024
        ok(f"CLAUDE.md ({size_kb} KB) → {DST_CLAUDE_MD}")
    else:
        err(f"CLAUDE.md no instalado")

    # Skills
    if DST_SKILLS.exists():
        skill_dirs = [d for d in DST_SKILLS.iterdir() if d.is_dir()]
        ok(f"{len(skill_dirs)} skills instaladas en {DST_SKILLS}")
        for d in sorted(skill_dirs):
            skill_md = d / "SKILL.md"
            status = "" if skill_md.exists() else " "
            print(f"     {status} {d.name}")
    else:
        err(f"~/.claude/skills/ no existe — ejecuta: python install_antigravity.py")

    # Workflows
    if DST_WORKFLOWS.exists():
        wf_files = list(DST_WORKFLOWS.glob("*.md"))
        ok(f"{len(wf_files)} workflows instalados en {DST_WORKFLOWS}")
    else:
        err("~/.claude/workflows/ no existe")

    # Claude Desktop
    print()
    if DESKTOP_CONFIG.exists():
        try:
            cfg = json.loads(DESKTOP_CONFIG.read_text(encoding="utf-8"))
            servers = cfg.get("mcpServers", {})
            if "gahenax-skills" in servers:
                ok(f"Claude Desktop MCP 'gahenax-skills' configurado → {DESKTOP_CONFIG}")
            else:
                warn(f"claude_desktop_config.json existe pero sin 'gahenax-skills' MCP server")
        except Exception as e:
            err(f"claude_desktop_config.json tiene error: {e}")
    else:
        err(f"Claude Desktop no configurado — {DESKTOP_CONFIG} no existe")

    # Comparación con fuente
    print(f"\n{C.BOLD} Comparación con Fuente {C.RESET}")
    src_skills = [d for d in SRC_SKILLS.iterdir() if d.is_dir()] if SRC_SKILLS.exists() else []
    dst_skills = [d for d in DST_SKILLS.iterdir() if d.is_dir()] if DST_SKILLS.exists() else []

    src_names = {d.name for d in src_skills}
    dst_names = {d.name for d in dst_skills}

    missing = src_names - dst_names
    if missing:
        warn(f"{len(missing)} skills en fuente pero NO instaladas:")
        for s in sorted(missing):
            print(f"       {s}")
    else:
        ok("Todas las skills están sincronizadas con la fuente")


# 
#  DESINSTALACIÓN
# 

def run_remove() -> None:
    print(f"\n{C.BOLD}{C.YELLOW} Desinstalando Gahenax AI de ~/.claude/ {C.RESET}\n")

    confirm = input("  ¿Estás seguro? Esto eliminará skills, workflows, CLAUDE.md y el MCP server. (s/N): ")
    if confirm.strip().lower() not in ("s", "si", "sí", "y", "yes"):
        print("  Cancelado.")
        return

    removed = []

    if DST_CLAUDE_MD.exists():
        DST_CLAUDE_MD.unlink()
        removed.append("~/.claude/CLAUDE.md")

    if DST_SKILLS.exists():
        shutil.rmtree(DST_SKILLS)
        removed.append("~/.claude/skills/")

    if DST_WORKFLOWS.exists():
        shutil.rmtree(DST_WORKFLOWS)
        removed.append("~/.claude/workflows/")

    # Limpia solo la entrada gahenax-skills del config de Claude Desktop
    if DESKTOP_CONFIG.exists():
        try:
            cfg = json.loads(DESKTOP_CONFIG.read_text(encoding="utf-8"))
            if "gahenax-skills" in cfg.get("mcpServers", {}):
                del cfg["mcpServers"]["gahenax-skills"]
                DESKTOP_CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
                removed.append("MCP 'gahenax-skills' de claude_desktop_config.json")
        except Exception as e:
            warn(f"No se pudo limpiar claude_desktop_config.json: {e}")

    if removed:
        ok(f"Eliminado: {', '.join(removed)}")
    else:
        info("No había nada instalado.")


# 
#  ENTRYPOINT
# 

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gahenax AI — Antigravity Installer para Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verifica el estado de instalación sin hacer cambios",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Desinstala Gahenax AI de ~/.claude/",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobreescribe sin preguntar si hay versiones existentes",
    )

    args = parser.parse_args()

    if args.check:
        run_check()
    elif args.remove:
        run_remove()
    else:
        run_install(force=args.force)


if __name__ == "__main__":
    main()
