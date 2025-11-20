Write-Host "Running all project tests and aggregating results"

Write-Host '-> Running Project A (baseline)'
Push-Location -Path .\Project_A_BaselineTicketUI
./run_tests.sh
Pop-Location

Write-Host '-> Running Project B (enhanced)'
Push-Location -Path .\Project_B_EnhancedTicketUI
./run_tests.sh
Pop-Location

New-Item -ItemType Directory -Force -Path .\results | Out-Null

Write-Host 'Collecting results into root results/'
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_A_BaselineTicketUI\results\results_pre.json -Destination .\results\results_pre.json
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_A_BaselineTicketUI\results\log_pre.txt -Destination .\results\log_pre.txt
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_A_BaselineTicketUI\results\summary_pre.json -Destination .\results\summary_pre.json

Copy-Item -ErrorAction SilentlyContinue -Path .\Project_B_EnhancedTicketUI\results\results_post.json -Destination .\results\results_post.json
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_B_EnhancedTicketUI\results\log_post.txt -Destination .\results\log_post.txt
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_B_EnhancedTicketUI\results\summary_post.json -Destination .\results\summary_post.json

Copy-Item -ErrorAction SilentlyContinue -Path .\Project_A_BaselineTicketUI\results\baseline_preview.html -Destination .\results\baseline_preview.html
Copy-Item -ErrorAction SilentlyContinue -Path .\Project_B_EnhancedTicketUI\results\enhanced_preview.html -Destination .\results\enhanced_preview.html

Write-Host 'Generating compare report'
python compare_results.py

Write-Host 'Aggregation complete. See results\ and compare_report.md'
