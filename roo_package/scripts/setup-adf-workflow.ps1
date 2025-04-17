# Setup ADF Documentation Workflow
# This script sets up a basic ADF documentation workflow in your project

# Configuration
$docsDir = "./docs"
$adfDocsDir = "./docs/adf"
$toolsDir = "./tools/adf"

# Create directories if they don't exist
Write-Host "Creating directories..." -ForegroundColor Cyan

if (-not (Test-Path $docsDir)) {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
    Write-Host "Created $docsDir" -ForegroundColor Green
}

if (-not (Test-Path $adfDocsDir)) {
    New-Item -ItemType Directory -Path $adfDocsDir -Force | Out-Null
    Write-Host "Created $adfDocsDir" -ForegroundColor Green
}

if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    Write-Host "Created $toolsDir" -ForegroundColor Green
}

# Copy ADF tools to project
Write-Host "Copying ADF tools to project..." -ForegroundColor Cyan

$toolFiles = @(
    "adf-viewer.html",
    "markdown-to-adf.html",
    "markdown-to-adf.js",
    "adf-documentation.json",
    "example-adf.json"
)

foreach ($file in $toolFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "$toolsDir/" -Force
        Write-Host "Copied $file to $toolsDir/" -ForegroundColor Green
    } else {
        Write-Host "Warning: $file not found in current directory" -ForegroundColor Yellow
    }
}

# Create a README for the ADF docs
$readmePath = "$adfDocsDir/README.md"
$readmeContent = @"
# ADF Documentation

This directory contains documentation in Atlassian Document Format (ADF).

## Viewing Documentation

To view these documents:

1. Open `../tools/adf/adf-viewer.html` in a web browser
2. Click "Load from File" and select an ADF JSON file from this directory

## Updating Documentation

When updating documentation:

1. Edit the original Markdown files in the parent directory
2. Run the conversion script to regenerate the ADF files:
   ```powershell
   .\convert-docs.ps1
   ```
3. Commit both the Markdown and ADF versions to version control
"@

Set-Content -Path $readmePath -Value $readmeContent
Write-Host "Created $readmePath" -ForegroundColor Green

# Create a conversion script
$conversionScriptPath = "./convert-docs.ps1"
$conversionScriptContent = @"
# Convert Markdown docs to ADF
# This script converts all Markdown files in the docs directory to ADF format

# Configuration
`$docsDir = "./docs"
`$adfDocsDir = "./docs/adf"
`$toolsDir = "./tools/adf"

# Convert Markdown files to ADF
Write-Host "Converting Markdown files to ADF..." -ForegroundColor Cyan

`$markdownFiles = Get-ChildItem -Path `$docsDir -Filter "*.md" -Recurse | Where-Object { `$_.FullName -notlike "*`$adfDocsDir*" }
foreach (`$file in `$markdownFiles) {
    `$relativePath = `$file.FullName.Substring((Resolve-Path `$docsDir).Path.Length + 1)
    `$outputPath = Join-Path -Path `$adfDocsDir -ChildPath (`$relativePath -replace "\.md`$", ".adf.json")
    
    # Create directory if it doesn't exist
    `$outputDir = Split-Path -Path `$outputPath -Parent
    if (-not (Test-Path `$outputDir)) {
        New-Item -ItemType Directory -Path `$outputDir -Force | Out-Null
    }
    
    # Convert Markdown to ADF
    Write-Host "Converting `$(`$file.FullName) to `$outputPath" -ForegroundColor Green
    node "`$toolsDir/markdown-to-adf.js" `$file.FullName `$outputPath
}

Write-Host "Conversion complete!" -ForegroundColor Cyan
"@

Set-Content -Path $conversionScriptPath -Value $conversionScriptContent
Write-Host "Created $conversionScriptPath" -ForegroundColor Green

# Create a sample documentation file if docs directory is empty
$sampleDocPath = "$docsDir/getting-started.md"
if ((Get-ChildItem -Path $docsDir -Filter "*.md").Count -eq 0) {
    $sampleDocContent = @"
# Getting Started

This is a sample documentation file that can be converted to ADF format.

## Introduction

This project uses a documentation-as-code approach with support for Atlassian Document Format (ADF).

## Features

- **Markdown Support**: Write documentation in Markdown format
- **ADF Conversion**: Convert Markdown to ADF for use with Atlassian products
- **Version Control**: Store documentation alongside code in the repository
- **Automated Conversion**: Use scripts to automate the conversion process

## How to Use

1. Write documentation in Markdown format in the `docs` directory
2. Run the conversion script to generate ADF files:
   ```powershell
   .\convert-docs.ps1
   ```
3. View the ADF files using the ADF Viewer:
   ```
   .\tools\adf\adf-viewer.html
   ```
4. Commit both Markdown and ADF files to version control
"@

    Set-Content -Path $sampleDocPath -Value $sampleDocContent
    Write-Host "Created sample documentation file: $sampleDocPath" -ForegroundColor Green
}

# Add documentation to .gitignore exceptions if .gitignore exists
$gitignorePath = "./.gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath
    $modified = $false
    
    if (-not ($gitignoreContent -contains "!$toolsDir/")) {
        Add-Content -Path $gitignorePath -Value "!$toolsDir/"
        $modified = $true
    }
    
    if (-not ($gitignoreContent -contains "!$adfDocsDir/")) {
        Add-Content -Path $gitignorePath -Value "!$adfDocsDir/"
        $modified = $true
    }
    
    if ($modified) {
        Write-Host "Updated .gitignore to include ADF documentation directories" -ForegroundColor Green
    }
}

# Final instructions
Write-Host "`nADF Documentation Workflow Setup Complete!" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Write your documentation in Markdown format in the $docsDir directory" -ForegroundColor White
Write-Host "2. Run .\convert-docs.ps1 to convert Markdown to ADF" -ForegroundColor White
Write-Host "3. View ADF files using $toolsDir/adf-viewer.html" -ForegroundColor White
Write-Host "4. Commit both Markdown and ADF files to version control" -ForegroundColor White
Write-Host "`nFor more information, see adf-integration-guide.md" -ForegroundColor White