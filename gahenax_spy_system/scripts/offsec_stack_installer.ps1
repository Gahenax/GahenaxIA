# Gahenax OffSec Stack Installer
# Instala herramientas de ProjectDiscovery y OWASP para Bug Bounty

$tools = @(
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
)

Write-Host "🕵️ Instalando arsenal de seguridad Gahenax..." -ForegroundColor Cyan

foreach ($tool in $tools) {
    Write-Host "Instalando $tool..."
    go install $tool
}

# Amass tiene un repo diferente
Write-Host "Instalando OWASP Amass..."
go install github.com/owasp-amass/amass/v4/...@latest

Write-Host "✅ Instalación completada. Asegúrate de que `$HOME/go/bin` esté en tu PATH." -ForegroundColor Green
