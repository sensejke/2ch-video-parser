# Test PowerShell syntax
Write-Host "==> Testing PowerShell syntax" -ForegroundColor Green

function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }

Write-Info "Testing functions..."
Write-Success "PowerShell syntax is correct"

Write-Host ""
Write-Host "If you see this message, PowerShell scripts should work!" -ForegroundColor Green
