# PowerShell test runner for Project A - Baseline Ticket UI

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Running Tests - Baseline Ticket UI" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Run tests using Python
Write-Host "Executing test runner..." -ForegroundColor Yellow
python tests\test_runner.py

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Test execution complete!" -ForegroundColor Green
Write-Host "Results saved to: results/" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
