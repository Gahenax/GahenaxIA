import time
import os
import random
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from gahenax_hub.math_lobe.system_hodge_mapper import hodge_mapper

console = Console()

def get_spectral_status():
    """Simula lectura de métricas de rigidez del sistema."""
    # En producción esto leería de gahenax_hub/sessions/cabal_memory.db
    rigidity = random.uniform(0.92, 0.99)
    ghosts = random.randint(0, 5)
    return rigidity, ghosts

def generate_table() -> Table:
    table = Table(title="💎 GAHENAX SPECTRAL RIGIDITY DASHBOARD")
    table.add_column("Módulo", justify="left", style="cyan")
    table.add_column("Rigidez (Hodge)", justify="center", style="green")
    table.add_column("Status", justify="right")

    # Obtener datos reales del mapper
    audit = hodge_mapper.scan_project()
    summary = audit["summary"]
    
    # Mostrar top 5 módulos más pesados o relevantes
    topology = sorted(audit["topology"], key=lambda x: x["rigidity"], reverse=True)[:8]
    
    for item in topology:
        style = "bold green" if item["class"] == "STRUCTURAL" else "bold red"
        table.add_row(
            item["file"], 
            f"{item['rigidity']:.4f}", 
            item["class"],
            style=style
        )
    
    return table

def main():
    with Live(generate_table(), refresh_per_second=1) as live:
        try:
            while True:
                time.sleep(2)
                live.update(generate_table())
        except KeyboardInterrupt:
            console.print("[bold red]Dashboard cerrado.")

if __name__ == "__main__":
    main()
