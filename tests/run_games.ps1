# Create output directory
New-Item -ItemType Directory -Force -Path output | Out-Null

Write-Host "Running 10 games..."

# Run 10 games sequentially
1..10 | ForEach-Object {
    $i = $_
    Write-Host "Running game $i..."
    python __main__.py 2>&1 | Out-File "output/result_$i.txt" -Encoding utf8
}

Write-Host "Done! Results saved to output/"
