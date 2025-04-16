# RooFlow Setup Package

This package contains the necessary scripts and tools to perform a comprehensive setup of RooFlow features (including custom modes, Memory Bank, and ADF integration) in either a new or existing project.

## Purpose

The goal is to provide a self-contained distribution for initializing a project with:
- Roo custom modes (via `.roomodes`).
- The Roo Memory Bank system.
- Default MCP server configurations.
- An Atlassian Document Format (ADF) documentation workflow and tools.
- Necessary configuration files like `.rooignore` and `.gitignore`.

## Contents

- `scripts/`: Contains the setup scripts:
    - `unpack.ps1`: Use this to unpack the RooFlow package and run the setup script in one step.
    - `apply-to-existing-project.ps1`: Use this to add RooFlow features to the current project.
    - `setup-new-project.ps1`: Use this to initialize the current directory with RooFlow features.
    - `sync-roomodes.ps1`: Use this to find and synchronize all .roomodes files across repositories.
- `tools/adf/`: Contains the necessary tools for the ADF documentation workflow (viewer, converter, etc.).
- `config/`: Contains configuration files for RooFlow custom modes.

## How to Use with Roo

If you're using Roo to set up this package, follow these steps:

1. **Switch to Code Mode**: If you're not already in Code mode, use:
   ```
   <switch_mode>
   <mode_slug>code</mode_slug>
   <reason>To execute PowerShell commands for RooFlow setup</reason>
   </switch_mode>
   ```

2. **Run the Unpack Script**: Once in Code mode, execute:
   ```
   <execute_command>
   <command>path\to\roo_package\scripts\unpack.ps1</command>
   </execute_command>
   ```

   If you want to specify a custom project name:
   ```
   <execute_command>
   <command>path\to\roo_package\scripts\unpack.ps1 -ProjectName "CustomProjectName"</command>
   </execute_command>
   ```

## Manual Setup Instructions

### Option 1: Using the Unpack Script (Recommended)

1. **Copy the Package:** Copy the entire `roo_package` directory to your computer.

2. **Run the Unpack Script:** Open PowerShell, navigate to the directory where you want to set up your project, and run:

   ```powershell
   path\to\roo_package\scripts\unpack.ps1
   ```

   This will:
   - Copy all necessary files from the package to your current directory
   - Run the setup script automatically

   If you want to specify a custom project name:

   ```powershell
   path\to\roo_package\scripts\unpack.ps1 -ProjectName "CustomProjectName"
   ```

### Option 2: Manual Setup

1. **Place the Package:** Copy the contents of this `roo_package` directory into your project directory.

2. **Choose the Right Script:**
    * **For an existing project:** Use `apply-to-existing-project.ps1`.
    * **For a new project:** Use `setup-new-project.ps1`.

3. **Run the Script:** Open PowerShell, navigate to your project directory, and execute the chosen script.

    **Example: Applying to an Existing Project**
    Navigate to your project directory and run:
    ```powershell
    .\scripts\apply-to-existing-project.ps1
    ```

    **Example: Setting up a New Project**
    Navigate to your project directory and run:
    ```powershell
    .\scripts\setup-new-project.ps1
    ```
    
    The script will automatically use your current directory name as the project name. If you want to specify a different name, you can use:
    ```powershell
    .\scripts\setup-new-project.ps1 -ProjectName "CustomProjectName"
    ```

4. **Follow Script Prompts:** The scripts will output progress and may provide next steps upon completion.

5. **Verify:** Check the target project directory for the newly created files and folders (`.roo`, `.roomodes`, `memory-bank`, `docs/adf`, `tools/adf`, etc.).

## Synchronizing .roomodes Files

To ensure consistency across all your repositories, you can use the `sync-roomodes.ps1` script to find all `.roomodes` files in the `c:/repos` directory and make sure they match the reference file at `C:\repos\cce-cq\.roomodes`.

1. **Check for Mismatches:** Run the script to identify any mismatches without making changes:
   ```powershell
   .\scripts\sync-roomodes.ps1
   ```

2. **Update Mismatched Files:** To automatically update all mismatched files to match the reference:
   ```powershell
   .\scripts\sync-roomodes.ps1 -UpdateFiles $true
   ```

This ensures that all your repositories use the same Roo custom modes configuration.

## Git Integration

The setup scripts automatically add all Roo-related files and directories to your `.gitignore` file:
- `.roo/` - RooFlow configuration directory
- `.roomodes` - Custom modes configuration
- `.rooignore` - Roo ignore file
- `memory-bank/` - Memory Bank files
- `memory-archives/` - Memory Bank archives

This ensures that these files remain local to your development environment and are not committed to your Git repository. This is important because:
1. These files contain environment-specific configurations
2. Memory Bank files can become large and change frequently
3. Each developer may have their own custom Roo setup

The scripts make an exception for the ADF tools and documentation directories, which are excluded from the gitignore to ensure they're properly tracked in your repository.

## Troubleshooting

If you encounter any issues:

1. **Script Not Found:** Make sure you're running the script from the correct directory or using the full path to the script.

2. **Permission Issues:** You might need to run PowerShell as Administrator or adjust your execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Path Issues:** If you're using relative paths, make sure you're in the correct directory.

Now RooFlow should be fully configured for your project!