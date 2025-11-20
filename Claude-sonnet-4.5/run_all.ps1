# PowerShell master test execution script - runs both projects and generates comparison

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "SAAS TICKET DETAIL PAGE UI/UX IMPROVEMENT - EVALUATION SUITE" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Run Project A - Baseline
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host "PHASE 1: Running Baseline Ticket UI (Project A)" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Yellow
Push-Location Project_A_BaselineTicketUI
& .\run_tests.ps1
Pop-Location

# Run Project B - Enhanced
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host "PHASE 2: Running Enhanced Ticket UI (Project B)" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Yellow
Push-Location Project_B_EnhancedTicketUI
& .\run_tests.ps1
Pop-Location

# Copy results to central location
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host "PHASE 3: Aggregating Results" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Yellow

if (-not (Test-Path "results")) {
    New-Item -ItemType Directory -Path "results" | Out-Null
}

Copy-Item "Project_A_BaselineTicketUI\results\results_pre.json" "results\" -Force
Copy-Item "Project_A_BaselineTicketUI\results\log_pre.txt" "results\" -Force
Copy-Item "Project_B_EnhancedTicketUI\results\results_post.json" "results\" -Force
Copy-Item "Project_B_EnhancedTicketUI\results\log_post.txt" "results\" -Force

Write-Host "Results aggregated in: results/" -ForegroundColor Green

# Generate comparison report
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host "PHASE 4: Generating Comparison Report" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Yellow
python generate_comparison_report.py

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "ALL TESTS COMPLETE" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Review the following files:" -ForegroundColor Cyan
Write-Host "  - results\results_pre.json  (Baseline results)" -ForegroundColor White
Write-Host "  - results\results_post.json (Enhanced results)" -ForegroundColor White
Write-Host "  - results\compare_report.md (Comparison analysis)" -ForegroundColor White
Write-Host ""
