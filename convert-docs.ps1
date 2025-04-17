# Convert Markdown docs to ADF
# This script converts all Markdown files in the docs directory to ADF format

# Configuration
$docsDir = "./docs"
$adfDocsDir = "./docs/adf"
$toolsDir = "./tools/adf"

# Convert Markdown files to ADF
Write-Host "Converting Markdown files to ADF..." -ForegroundColor Cyan

$markdownFiles = Get-ChildItem -Path $docsDir -Filter "*.md" -Recurse | Where-Object { $_.FullName -notlike "*$adfDocsDir*" }
foreach ($file in $markdownFiles) {
    $relativePath = $file.FullName.Substring((Resolve-Path $docsDir).Path.Length + 1)
    $outputPath = Join-Path -Path $adfDocsDir -ChildPath ($relativePath -replace "\.md$", ".adf.json")
    
    # Create directory if it doesn't exist
    $outputDir = Split-Path -Path $outputPath -Parent
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Convert Markdown to ADF
    Write-Host "Converting $($file.FullName) to $outputPath" -ForegroundColor Green
    node "$toolsDir/markdown-to-adf.js" $file.FullName $outputPath
}

Write-Host "Conversion complete!" -ForegroundColor Cyan
