# Gahenax Spy Cleaner
# Cierra todos los procesos del sistema de espionaje

Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "🛑 Gahenax Spy detenido en todos los nodos local-host." -ForegroundColor Red
