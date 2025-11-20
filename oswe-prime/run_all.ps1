$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Running Project A Baseline Tests..."
Push-Location "$root/Project_A_BaselineTicketUI"
bash ./run_tests.sh
Pop-Location

Write-Host "Running Project B Enhanced Tests..."
Push-Location "$root/Project_B_EnhancedTicketUI"
bash ./run_tests.sh
Pop-Location

# aggregate
New-Item -ItemType Directory -Force -Path "$root/results" | Out-Null
Copy-Item -Path "$root/Project_A_BaselineTicketUI/results/results_pre.json" -Destination "$root/results/" -ErrorAction SilentlyContinue
Copy-Item -Path "$root/Project_A_BaselineTicketUI/results/log_pre.txt" -Destination "$root/results/" -ErrorAction SilentlyContinue
Copy-Item -Path "$root/Project_B_EnhancedTicketUI/results/results_post.json" -Destination "$root/results/" -ErrorAction SilentlyContinue
Copy-Item -Path "$root/Project_B_EnhancedTicketUI/results/log_post.txt" -Destination "$root/results/" -ErrorAction SilentlyContinue

# generate compare report
python "$root/compare_results.py" "$root/results/results_pre.json" "$root/results/results_post.json" "$root/results/compare_report.md"
Write-Host "All done. Reports are in $root/results"
