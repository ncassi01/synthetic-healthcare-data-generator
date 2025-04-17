# ADF Documentation

This directory contains documentation in Atlassian Document Format (ADF).

## Viewing Documentation

To view these documents:

1. Open ../tools/adf/adf-viewer.html in a web browser
2. Click "Load from File" and select an ADF JSON file from this directory

## Updating Documentation

When updating documentation:

1. Edit the original Markdown files in the parent directory
2. Run the conversion script to regenerate the ADF files:
   `powershell
   .\convert-docs.ps1
   `
3. Commit both the Markdown and ADF versions to version control
