# Start all services
Write-Host "🚀 DAROMATX Bot ishga tushirilmoqda..." -ForegroundColor Cyan

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python o'rnatilmagan!" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js o'rnatilmagan!" -ForegroundColor Red
    exit 1
}

$rootPath = $PSScriptRoot

# Start Bot
Write-Host "🤖 Bot ishga tushirilmoqda..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\bot'; python main.py"

# Start API
Write-Host "🌐 API ishga tushirilmoqda..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\api'; python -m uvicorn main:app --reload --port 8000"

# Start Mini App
Write-Host "📱 Mini App ishga tushirilmoqda..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\mini-app'; npm run dev"

Write-Host ""
Write-Host "✅ Barcha servislar ishga tushirildi!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Bot: Telegram bot ishlayapti"
Write-Host "📍 API: http://localhost:8000"
Write-Host "📍 Mini App: http://localhost:3000"
Write-Host ""
