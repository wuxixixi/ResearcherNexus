# 设置输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Build script with code checking
Write-Host "Starting build with code checks..." -ForegroundColor Green

# Clean Next.js cache
Write-Host "Cleaning Next.js cache..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue

# Run TypeScript type check
Write-Host "Running TypeScript type check..." -ForegroundColor Cyan
pnpm typecheck
if ($LASTEXITCODE -ne 0) {
    Write-Host "TypeScript type check failed!" -ForegroundColor Red
    exit 1
}

# Run ESLint check
Write-Host "Running ESLint check..." -ForegroundColor Cyan
pnpm lint
if ($LASTEXITCODE -ne 0) {
    Write-Host "ESLint check failed!" -ForegroundColor Red
    Write-Host "Tip: Run 'pnpm lint:fix' to auto-fix some issues" -ForegroundColor Yellow
    exit 1
}

# Execute build
Write-Host "Building..." -ForegroundColor Cyan
pnpm build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
} 