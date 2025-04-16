# Apply RooFlow Custom Modes to Existing Project
# This script automates the process of applying RooFlow custom modes, memory system, and ADF integration to the current project
# Usage: .\apply-to-existing-project.ps1
# Note: This script assumes it's being run from the root directory of the project you want to modify

param()

# Use the current directory as the project path
$ProjectPath = Get-Location

try {
    Write-Host "Applying RooFlow custom modes to the current project" -ForegroundColor Green

    # Step 1: Check for .roomodes file
    if (-not (Test-Path -Path ".roomodes")) {
        # Check if there's a .roomodes file in the package directory
        $packageDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
        $packageRoomodesPath = Join-Path -Path $packageDir -ChildPath ".roomodes"
        
        if (Test-Path -Path $packageRoomodesPath) {
            Write-Host "Copying .roomodes file from package..." -ForegroundColor Yellow
            Copy-Item -Path $packageRoomodesPath -Destination ".roomodes" -Force
            Write-Host "Copied .roomodes file from package" -ForegroundColor Green
        } else {
            # Create a default .roomodes file if one wasn't found in the package
            Write-Host "Creating default .roomodes file..." -ForegroundColor Yellow
            $roomodesContent = @'
{
  "customModes": [
    {
      "slug": "test",
      "name": "Test",
      "roleDefinition": "You are Roo's Test mode for this specific project",
      "groups": [
        "read",
        "browser",
        "command",
        "edit",
        "mcp"
      ],
      "source": "project",
      "customInstructions": "Always check to make sure memory bank is active. Explicitly prompt Emily when she needs to do a manual action. terminal commands must be PowerShell. Explicitly prompt Emily when she needs to do a manual action. Save to memory and prompt user to start a new task when token cost nears $0.5"
    }
  ]
}
'@
            Set-Content -Path ".roomodes" -Value $roomodesContent
            Write-Host "Created default .roomodes file" -ForegroundColor Green
        }
    } else {
        Write-Host ".roomodes file already exists" -ForegroundColor Yellow
    }

    # Step 2: Create .rooignore file if it doesn't exist
    if (-not (Test-Path -Path ".rooignore")) {
        Write-Host "Creating .rooignore file..." -ForegroundColor Yellow
        $rooignoreContent = @'
node_modules/
dist/
build/
.git/
*.log
'@
        Set-Content -Path ".rooignore" -Value $rooignoreContent
        Write-Host "Created .rooignore file" -ForegroundColor Green
    } else {
        Write-Host ".rooignore file already exists" -ForegroundColor Yellow
    }

    # Step 3: Create memory-bank directory and related directories if they don't exist
    if (-not (Test-Path -Path "memory-bank")) {
        Write-Host "Creating memory-bank directory..." -ForegroundColor Yellow
        New-Item -Path "memory-bank" -ItemType Directory | Out-Null
        Write-Host "Created memory-bank directory" -ForegroundColor Green
    } else {
        Write-Host "memory-bank directory already exists" -ForegroundColor Yellow
    }
    
    # Create memory-bank/archives directory if it doesn't exist
    $archivesSubPath = "memory-bank/archives"
    if (-not (Test-Path -Path $archivesSubPath)) {
        Write-Host "Creating memory-bank archives subdirectory..." -ForegroundColor Yellow
        New-Item -Path $archivesSubPath -ItemType Directory | Out-Null
        Write-Host "Created memory-bank archives subdirectory" -ForegroundColor Green
    } else {
        Write-Host "Memory-bank archives subdirectory already exists" -ForegroundColor Yellow
    }
    
    # Create memory-archives directory if it doesn't exist
    if (-not (Test-Path -Path "memory-archives")) {
        Write-Host "Creating memory-archives directory..." -ForegroundColor Yellow
        New-Item -Path "memory-archives" -ItemType Directory | Out-Null
        Write-Host "Created memory-archives directory" -ForegroundColor Green
    } else {
        Write-Host "Memory-archives directory already exists" -ForegroundColor Yellow
    }
    
    # Create .roo directory if it doesn't exist
    if (-not (Test-Path -Path ".roo")) {
        Write-Host "Creating .roo directory..." -ForegroundColor Yellow
        New-Item -Path ".roo" -ItemType Directory | Out-Null
        Write-Host "Created .roo directory" -ForegroundColor Green
    } else {
        Write-Host ".roo directory already exists" -ForegroundColor Yellow
    }

    # Get current timestamp
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Get project name from directory
    $projectName = Split-Path -Path $ProjectPath.Path -Leaf

    # Step 4: Create memory bank files if they don't exist
    $memoryBankFiles = @{
        "productContext.md" = @"
# Product Context

## Project Overview
[Brief description of $projectName]

## Goals
- [Goal 1]
- [Goal 2]

## Features
- [Feature 1]
- [Feature 2]

## Architecture
[High-level architecture description]
"@
        "activeContext.md" = @"
# Active Context

## Current Focus
[Current focus of development]

## Recent Changes
RooFlow memory bank initialized on $timestamp

## Open Questions/Issues
[Open questions or issues]
"@
        "systemPatterns.md" = @"
# System Patterns

## Design Patterns
[Design patterns used in the project]

## Architectural Patterns
[Architectural patterns used in the project]

## Coding Standards
[Coding standards followed in the project]
"@
        "decisionLog.md" = @"
# Decision Log

[$timestamp] - RooFlow memory bank initialized
"@
        "progress.md" = @"
# Progress

[$timestamp] - RooFlow memory bank initialized
"@
    }

    foreach ($file in $memoryBankFiles.Keys) {
        $filePath = "memory-bank/$file"
        if (-not (Test-Path -Path $filePath)) {
            Write-Host "Creating $filePath..." -ForegroundColor Yellow
            Set-Content -Path $filePath -Value $memoryBankFiles[$file]
            Write-Host "Created $filePath" -ForegroundColor Green
        } else {
            Write-Host "$filePath already exists" -ForegroundColor Yellow
        }
    }
    
    # Create memory-config.json with default content if it doesn't exist
    $configFilePath = "memory-bank/memory-config.json"
    if (-not (Test-Path -Path $configFilePath)) {
        Write-Host "Creating memory-config.json..." -ForegroundColor Yellow
        $defaultConfig = @{
            activeProjects = @()
            completedProjects = @()
            archiveSettings = @{
                autoArchiveCompleted = $true
                keepCompletedDays = 14
                archiveOnUMB = $true
            }
            loadSettings = @{
                prioritizeActive = $true
                maxEntriesPerFile = 50
                loadCompletedProjects = $false
            }
            projectMetadata = @{}
        } | ConvertTo-Json -Depth 5
        Set-Content -Path $configFilePath -Value $defaultConfig
        Write-Host "Created memory-config.json" -ForegroundColor Green
    } else {
        Write-Host "memory-config.json already exists" -ForegroundColor Yellow
    }
    
    # Create empty archive files if they don't exist
    $archiveFiles = @(
        "activeContext-archive.md",
        "decisionLog-archive.md",
        "productContext-archive.md",
        "progress-archive.md",
        "systemPatterns-archive.md"
    )
    
    foreach ($file in $archiveFiles) {
        $filePath = Join-Path -Path $archivesSubPath -ChildPath $file
        if (-not (Test-Path -Path $filePath)) {
            Write-Host "Creating empty archive file: $filePath" -ForegroundColor Yellow
            New-Item -Path $filePath -ItemType File | Out-Null
            Write-Host "Created empty archive file: $filePath" -ForegroundColor Green
        } else {
            Write-Host "Archive file already exists: $filePath" -ForegroundColor Yellow
        }
    }
    
    # Create empty archive-index.md if it doesn't exist
    $archiveIndexFilePath = Join-Path -Path $archivesSubPath -ChildPath "archive-index.md"
    if (-not (Test-Path -Path $archiveIndexFilePath)) {
        Write-Host "Creating empty archive index: $archiveIndexFilePath" -ForegroundColor Yellow
        New-Item -Path $archiveIndexFilePath -ItemType File | Out-Null
        Write-Host "Created empty archive index" -ForegroundColor Green
    } else {
        Write-Host "Archive index already exists: $archiveIndexFilePath" -ForegroundColor Yellow
    }
    
    # Create mcp-config.json with default server configurations if it doesn't exist
    $mcpConfigPath = ".roo/mcp-config.json"
    if (-not (Test-Path -Path $mcpConfigPath)) {
        Write-Host "Creating default mcp-config.json..." -ForegroundColor Yellow
        $defaultMcpConfig = @{
            mcpServers = @{
                filesystem = @{
                    enabled = $false
                    description = "Provides access to the local filesystem."
                    basePath = "<Specify base path if needed, e.g., project root or specific data folder>"
                }
                git = @{
                    enabled = $false
                    description = "Provides Git repository operations."
                    repoPath = "<Specify path to the Git repository, defaults to project root if empty>"
                    credentialsEnvVar = "<Optional: Environment variable name for Git credentials>"
                }
                braveSearch = @{
                    enabled = $false
                    description = "Provides web search capabilities via Brave Search API."
                    apiKeyEnvVar = "BRAVE_SEARCH_API_KEY" # Placeholder - User must set this environment variable
                }
            }
        } | ConvertTo-Json -Depth 5
        Set-Content -Path $mcpConfigPath -Value $defaultMcpConfig -Encoding UTF8
        Write-Host "Created default mcp-config.json" -ForegroundColor Green
    } else {
        Write-Host "mcp-config.json already exists: $mcpConfigPath" -ForegroundColor Yellow
    }
    
    # Setup ADF Documentation Workflow
    Write-Host "Setting up ADF Documentation Workflow..." -ForegroundColor Yellow
    
    # Create ADF directories if they don't exist
    $docsDir = "docs"
    $adfDocsDir = "docs/adf"
    $toolsDir = "tools/adf"
    
    if (-not (Test-Path -Path $docsDir)) {
        Write-Host "Creating $docsDir directory..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
        Write-Host "Created $docsDir" -ForegroundColor Green
    } else {
        Write-Host "$docsDir directory already exists" -ForegroundColor Yellow
    }
    
    if (-not (Test-Path -Path $adfDocsDir)) {
        Write-Host "Creating $adfDocsDir directory..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $adfDocsDir -Force | Out-Null
        Write-Host "Created $adfDocsDir" -ForegroundColor Green
    } else {
        Write-Host "$adfDocsDir directory already exists" -ForegroundColor Yellow
    }
    
    if (-not (Test-Path -Path $toolsDir)) {
        Write-Host "Creating $toolsDir directory..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
        Write-Host "Created $toolsDir" -ForegroundColor Green
    } else {
        Write-Host "$toolsDir directory already exists" -ForegroundColor Yellow
    }
    
    # Copy ADF tools to project
    Write-Host "Copying ADF tools to project..." -ForegroundColor Cyan
    
    # Get the path to the repository root (where the script is located)
    # Get the path to the package's tools directory (relative to this script)
    $packageToolsDir = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath "../tools/adf"
    $packageToolsDir = Resolve-Path -Path $packageToolsDir # Ensure it's an absolute path
    
    $toolFiles = @(
        "adf-viewer.html",
        "markdown-to-adf.html",
        "markdown-to-adf.js",
        "adf-documentation.json",
        "example-adf.json"
    )
    
    foreach ($file in $toolFiles) {
        $sourcePath = Join-Path -Path $packageToolsDir -ChildPath $file
        $destPath = Join-Path -Path $toolsDir -ChildPath $file
        if (Test-Path $sourcePath) {
            if (-not (Test-Path $destPath)) {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
                Write-Host "Copied $file to $toolsDir/" -ForegroundColor Green
            } else {
                Write-Host "$file already exists in $toolsDir/" -ForegroundColor Yellow
            }
        } else {
            Write-Host "Warning: $file not found in repository root" -ForegroundColor Yellow
        }
    }
    
    # Create a README for the ADF docs if it doesn't exist
    $readmePath = "$adfDocsDir/README.md"
    if (-not (Test-Path -Path $readmePath)) {
        Write-Host "Creating ADF README..." -ForegroundColor Yellow
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
    } else {
        Write-Host "ADF README already exists: $readmePath" -ForegroundColor Yellow
    }
    
    # Create a conversion script if it doesn't exist
    $conversionScriptPath = "convert-docs.ps1"
    if (-not (Test-Path -Path $conversionScriptPath)) {
        Write-Host "Creating conversion script..." -ForegroundColor Yellow
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
    } else {
        Write-Host "Conversion script already exists: $conversionScriptPath" -ForegroundColor Yellow
    }
    
    # Create a sample documentation file if docs directory is empty
    $sampleDocPath = "docs/getting-started.md"
    if ((Get-ChildItem -Path $docsDir -Filter "*.md").Count -eq 0) {
        Write-Host "Creating sample documentation file..." -ForegroundColor Yellow
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
    } else {
        Write-Host "Documentation files already exist in $docsDir" -ForegroundColor Yellow
    }
    
    # Update .gitignore to include ADF documentation directories if .gitignore exists
    if (Test-Path -Path ".gitignore") {
        $gitignoreContent = Get-Content ".gitignore"
        $modified = $false
        
        # Add ADF documentation directories exceptions
        if (-not ($gitignoreContent -contains "!$toolsDir/")) {
            Add-Content -Path ".gitignore" -Value "!$toolsDir/"
            $modified = $true
        }
        
        if (-not ($gitignoreContent -contains "!$adfDocsDir/")) {
            Add-Content -Path ".gitignore" -Value "!$adfDocsDir/"
            $modified = $true
        }
        
        # Add Roo-related files and directories
        $rooEntries = @(
            ".roo/",
            ".roomodes",
            ".rooignore",
            "memory-bank/",
            "memory-archives/"
        )
        
        $rooModified = $false
        foreach ($entry in $rooEntries) {
            if (-not ($gitignoreContent -contains $entry)) {
                Add-Content -Path ".gitignore" -Value $entry
                $rooModified = $true
            }
        }
        
        if ($modified) {
            Write-Host "Updated .gitignore to include ADF documentation directories" -ForegroundColor Green
        } else {
            Write-Host ".gitignore already includes ADF documentation directories" -ForegroundColor Yellow
        }
        
        if ($rooModified) {
            Write-Host "Updated .gitignore to include Roo-related files and directories" -ForegroundColor Green
        } else {
            Write-Host ".gitignore already includes Roo-related files and directories" -ForegroundColor Yellow
        }
    }

    Write-Host "`nRooFlow custom modes, memory system, and ADF integration have been successfully applied to the project!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Open the project in VS Code" -ForegroundColor Cyan
    Write-Host "2. Configure MCP servers (optional): .\scripts\Configure-McpServers.ps1" -ForegroundColor Cyan
    Write-Host "3. Start a new Roo Code task in Architect mode" -ForegroundColor Cyan
    Write-Host "4. Roo will detect the memory bank and activate it" -ForegroundColor Cyan
    Write-Host "5. Begin with a project planning session to populate the memory bank" -ForegroundColor Cyan
    Write-Host "6. Use 'Update Memory Bank' or 'UMB' command at key milestones" -ForegroundColor Cyan
    Write-Host "7. For ADF documentation conversion, ensure Node.js is installed and run: .\convert-docs.ps1" -ForegroundColor Cyan

    # Prompt user to switch to Architect mode
    Write-Host "`nRooFlow setup complete! Please switch to Architect mode and ask a question to initialize the memory bank." -ForegroundColor Green

} catch {
    Write-Error "An error occurred: $_"
}