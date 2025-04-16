# RooFlow Scripts

This directory contains PowerShell scripts to help you apply RooFlow custom modes to your projects.

## Available Scripts

### 1. `apply-to-existing-project.ps1`

This script automates the process of applying RooFlow custom modes to an existing project.

#### Usage

```powershell
.\apply-to-existing-project.ps1 -ProjectPath "C:\path\to\your\project"
```

#### Parameters

- `-ProjectPath` (Required): The full path to your existing project directory

#### What it does

1. Creates a `.roomodes` file with a Test mode configuration
2. Creates a `.rooignore` file with common patterns to ignore
3. Creates a `memory-bank` directory with the following files:
   - `productContext.md`
   - `activeContext.md`
   - `systemPatterns.md`
   - `decisionLog.md`
   - `progress.md`

### 2. `setup-new-project.ps1`

This script automates the process of creating a new project with RooFlow custom modes.

#### Usage

```powershell
.\setup-new-project.ps1 -ProjectName "YourProjectName" -ProjectPath "C:\path\to\parent\directory"
```

#### Parameters

- `-ProjectName` (Required): The name of your new project
- `-ProjectPath` (Optional): The parent directory where the project will be created (defaults to current directory)

#### What it does

1. Creates a new project directory with the specified name
2. Initializes a Git repository
3. Creates a `.roomodes` file with a Test mode configuration
4. Creates a `.rooignore` file with common patterns to ignore
5. Creates a `.gitignore` file with common patterns to ignore
6. Creates a `memory-bank` directory with the following files:
   - `productContext.md`
   - `activeContext.md`
   - `systemPatterns.md`
   - `decisionLog.md`
   - `progress.md`
7. Creates a basic `README.md` file
8. Creates a basic project structure with `src`, `docs`, and `tests` directories

### 3. `Initialize-RooMemorySystem.ps1`

This script sets up the memory bank optimization and archiving system in a project directory.

#### Usage

```powershell
.\Initialize-RooMemorySystem.ps1 -ProjectPath "C:\path\to\your\project"
```

#### Parameters

- `-ProjectPath` (Required): The full path to your project directory

#### What it does

1. Creates necessary directories for the memory system:
   - `memory-bank`
   - `memory-bank/archives`
   - `memory-archives`
   - `.roo`
2. Creates configuration files:
   - `memory-config.json` with default settings
   - `mcp-config.json` with default server configurations
3. Creates empty archive files for different memory types

### 4. `setup-adf-workflow.ps1`

This script sets up a basic ADF (Atlassian Document Format) documentation workflow in your project.

#### Usage

```powershell
.\setup-adf-workflow.ps1
```

#### What it does

1. Creates necessary directories:
   - `docs`
   - `docs/adf`
   - `tools/adf`
2. Copies ADF tools to the project
3. Creates a README for the ADF docs
4. Creates a conversion script (`convert-docs.ps1`)
5. Creates a sample documentation file if the docs directory is empty
6. Updates `.gitignore` to include ADF documentation directories

### 5. `Configure-McpServers.ps1`

This script interactively configures MCP servers defined in `.roo/mcp-config.json`.

#### Usage

```powershell
.\Configure-McpServers.ps1
```

#### What it does

1. Reads the MCP configuration file
2. Iterates through each defined server
3. Prompts the user to enable/disable the server
4. For enabled servers, prompts the user to select allowed tools
5. Updates the configuration file with the user's choices
6. Checks for necessary environment variables and provides reminders

## Prerequisites

- PowerShell 5.1 or later
- Git installed and available in your PATH

## Next Steps After Running Scripts

1. Open the project in VS Code
2. Start a new Roo Code task in Architect mode
3. Roo will detect the memory bank and activate it
4. Begin with a project planning session
5. Use the "Update Memory Bank" or "UMB" command at key milestones

## Troubleshooting

If you encounter any issues:

1. Make sure you have the necessary permissions to create files and directories
2. Check that Git is installed and available in your PATH
3. Verify that the paths you provide exist and are accessible