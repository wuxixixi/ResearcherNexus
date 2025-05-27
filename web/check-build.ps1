# Check build output for tab labels
Write-Host "Checking build output for tab labels..." -ForegroundColor Cyan

# Search for TAB_LABELS in build output
Write-Host "`nSearching for TAB_LABELS mapping..." -ForegroundColor Yellow
$found = Get-ChildItem -Path ".next\static\chunks\app" -Filter "*.js" -Recurse | 
    Select-String -Pattern "TAB_LABELS|General.*通用|displayName.*GeneralTab" -List

if ($found) {
    Write-Host "Found tab label references in:" -ForegroundColor Green
    $found | ForEach-Object {
        Write-Host "  - $($_.Filename)" -ForegroundColor Gray
    }
} else {
    Write-Host "No tab label references found in build output!" -ForegroundColor Red
}

# Check for specific patterns
Write-Host "`nChecking for specific patterns..." -ForegroundColor Yellow
$patterns = @(
    "GeneralTab.*displayName",
    "MCPTab.*displayName", 
    "AboutTab.*displayName",
    "通用.*MCP.*关于"
)

foreach ($pattern in $patterns) {
    $matches = Get-ChildItem -Path ".next" -Filter "*.js" -Recurse | 
        Select-String -Pattern $pattern -List
    
    if ($matches) {
        Write-Host "Pattern '$pattern' found in $($matches.Count) file(s)" -ForegroundColor Green
    } else {
        Write-Host "Pattern '$pattern' NOT found" -ForegroundColor Red
    }
} 