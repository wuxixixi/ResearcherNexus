# 设置输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Quick build script - clean only necessary cache
Write-Host "Starting quick build..." -ForegroundColor Green

# Clean Next.js cache
Write-Host "Cleaning Next.js cache..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue

# Execute build
Write-Host "Building..." -ForegroundColor Cyan
& pnpm build
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit $buildExitCode
} 