param (
    [switch]$Proxy,
    [switch]$Clean,
    [int]$ProxyPort = 8080
)

$caPath = "C:\Users\jotam\AppData\Roaming\Requestly\.tmp\certs\ca.pem"
$vars = @("SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS", "REQUESTS_CA_BUNDLE", "PERL_LWP_SSL_CA_FILE", "GIT_SSL_CAINFO", "CARGO_HTTP_CAINFO", "CURL_CA_BUNDLE")

if ($Clean) {
    Write-Host "Limpiando variables de Requestly de la sesión actual..." -ForegroundColor Yellow
    foreach ($v in $vars) { Remove-Item "Env:\$v" -ErrorAction SilentlyContinue }
    Remove-Item Env:\HTTP_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:\HTTPS_PROXY -ErrorAction SilentlyContinue
    exit
}

if (Test-Path $caPath) {
    Write-Host "--- Gahenax Proxy Linker (Requestly) ---" -ForegroundColor Cyan
    
    # Aplicar certificados
    foreach ($v in $vars) { Set-Item "Env:\$v" -Value $caPath }
    Write-Host "[OK] Trusting Certificate: $caPath" -ForegroundColor Gray

    if ($Proxy) {
        $proxyUrl = "http://127.0.0.1:$ProxyPort"
        $env:HTTP_PROXY = $proxyUrl
        $env:HTTPS_PROXY = $proxyUrl
        Write-Host "[ON] Proxy Interception enabled on $proxyUrl" -ForegroundColor Green
    } else {
        Write-Host "[OFF] Proxy Interception (only manual config or implicit certs used)" -ForegroundColor Yellow
    }
    
    Write-Host "Sesión vinculada correctamente." -ForegroundColor Cyan
} else {
    Write-Error "Requestly CA certificate not found at $caPath. Ensure Requestly Desktop is installed and setup."
}
