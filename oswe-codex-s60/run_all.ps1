$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Running baseline (Project A)..."
bash "$root/Project_A_BaselineTicketUI/run_tests.sh"

Write-Host "Running enhanced (Project B)..."
bash "$root/Project_B_EnhancedTicketUI/run_tests.sh"

Write-Host "Aggregating results..."
python "$root/scripts/aggregate_results.py"

Write-Host "Done. See results/compare_report.md"
