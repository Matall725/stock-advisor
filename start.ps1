param([switch]$NoBrowser)

$Host.UI.RawUI.WindowTitle = "Stock Advisor"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stock Advisor - One-Click Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Back   = Join-Path $Root "backend"
$Front  = Join-Path $Root "frontend"

# 1. Backend deps
Write-Host "[1/3] Backend dependencies..." -ForegroundColor Yellow
$venv = Join-Path $Back "venv"
if (-not (Test-Path $venv)) {
    python -m venv $venv | Out-Null
}
$pip = Join-Path $venv "Scripts\pip.exe"
& $pip install -q -r (Join-Path $Back "requirements.txt") 2>$null
Write-Host "  [OK] Backend ready" -ForegroundColor Green

# 2. Frontend deps
Write-Host "[2/3] Frontend dependencies..." -ForegroundColor Yellow
$nm = Join-Path $Front "node_modules"
if (-not (Test-Path $nm)) {
    Push-Location $Front
    npm install --silent 2>$null
    Pop-Location
}
Write-Host "  [OK] Frontend ready" -ForegroundColor Green

# 3. Start services
Write-Host "[3/3] Starting services..." -ForegroundColor Yellow

$py = Join-Path $venv "Scripts\python.exe"
$beLog = Join-Path $Root "backend.log"
$feLog = Join-Path $Root "frontend.log"

# kill leftovers
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "main.py" } | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "vite" } | Stop-Process -Force

# backend process
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $py
$psi.Arguments = "main.py"
$psi.WorkingDirectory = $Back
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true
$be = [System.Diagnostics.Process]::Start($psi)

# frontend process
$psi2 = New-Object System.Diagnostics.ProcessStartInfo
$psi2.FileName = "cmd.exe"
$psi2.Arguments = "/c npx vite --host"
$psi2.WorkingDirectory = $Front
$psi2.UseShellExecute = $false
$psi2.RedirectStandardOutput = $true
$psi2.RedirectStandardError = $true
$psi2.CreateNoWindow = $true
$fe = [System.Diagnostics.Process]::Start($psi2)

Start-Sleep 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services running!" -ForegroundColor Cyan
Write-Host "  Backend : http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop all services..." -ForegroundColor Yellow

if (-not $NoBrowser) {
    Start-Sleep 1
    Start-Process "http://localhost:5173"
}

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "Stopping..." -ForegroundColor Gray
if (!$be.HasExited) { $be.Kill() }
if (!$fe.HasExited) { $fe.Kill() }
Write-Host "Done." -ForegroundColor Green
