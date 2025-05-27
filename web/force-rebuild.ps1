# Force rebuild script - clean ALL caches
Write-Host "Starting force rebuild..." -ForegroundColor Green

# Stop any running processes
Write-Host "Stopping any running processes..." -ForegroundColor Cyan
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Clean Next.js cache
Write-Host "Cleaning Next.js cache..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue

# Clean node_modules cache
Write-Host "Cleaning node_modules cache..." -ForegroundColor Cyan
Remove-Item -Recurse -Force node_modules/.cache -ErrorAction SilentlyContinue

# Clean TypeScript cache
Write-Host "Cleaning TypeScript cache..." -ForegroundColor Cyan
Remove-Item -Force *.tsbuildinfo -ErrorAction SilentlyContinue
Remove-Item -Force tsconfig.tsbuildinfo -ErrorAction SilentlyContinue

# Clean pnpm cache
Write-Host "Cleaning pnpm store..." -ForegroundColor Cyan
pnpm store prune

# Wait a moment
Start-Sleep -Seconds 2

# Build
Write-Host "Building..." -ForegroundColor Cyan
pnpm build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "You can now restart using bootstrap.bat" -ForegroundColor Yellow
} else {
    Write-Host "Build failed!" -ForegroundColor Red
} 