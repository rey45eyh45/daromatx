# Install all dependencies
Write-Host "📦 DAROMATX Bot dependencies o'rnatilmoqda..." -ForegroundColor Cyan

$rootPath = $PSScriptRoot

# Install Bot dependencies
Write-Host ""
Write-Host "🐍 Python dependencies o'rnatilmoqda..." -ForegroundColor Yellow
Set-Location "$rootPath\bot"

if (-not (Test-Path "venv")) {
    python -m venv venv
}

& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# Install API dependencies
Write-Host ""
Write-Host "🌐 API dependencies o'rnatilmoqda..." -ForegroundColor Yellow
Set-Location "$rootPath\api"
pip install -r requirements.txt

# Install Mini App dependencies
Write-Host ""
Write-Host "📱 Mini App dependencies o'rnatilmoqda..." -ForegroundColor Yellow
Set-Location "$rootPath\mini-app"
npm install

Set-Location $rootPath

Write-Host ""
Write-Host "✅ Barcha dependencies o'rnatildi!" -ForegroundColor Green
Write-Host ""
Write-Host "Ishga tushirish uchun: .\start.ps1" -ForegroundColor Cyan
