# 清理 Next.js 和 pnpm 缓存脚本
Write-Host "开始清理缓存..." -ForegroundColor Yellow

# 清理 Next.js 缓存
Write-Host "清理 Next.js 缓存..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue

# 清理 TypeScript 缓存
Write-Host "清理 TypeScript 缓存..." -ForegroundColor Cyan
Remove-Item -Force *.tsbuildinfo -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force tsconfig.tsbuildinfo -ErrorAction SilentlyContinue

# 清理 node_modules（可选）
$response = Read-Host "是否要删除 node_modules? (y/n)"
if ($response -eq 'y') {
    Write-Host "删除 node_modules..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
    
    Write-Host "清理 pnpm 存储..." -ForegroundColor Cyan
    pnpm store prune
    
    Write-Host "重新安装依赖..." -ForegroundColor Cyan
    pnpm install
}

Write-Host "清理完成!" -ForegroundColor Green 