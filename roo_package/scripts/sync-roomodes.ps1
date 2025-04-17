# Sync .roomodes Files
# This script finds all .roomodes files in the c:/repos directory and ensures they match the reference file at C:/repos/.roomodes
# Usage: .\sync-roomodes.ps1 [-UpdateFiles $true]

param(
    [Parameter(Mandatory=$false)]
    [bool]$UpdateFiles = $false
)

# Define the reference .roomodes file path
$referenceFilePath = "C:/repos/.roomodes"

# Check if the reference file exists
if (-not (Test-Path -Path $referenceFilePath)) {
    Write-Error "Reference .roomodes file not found at $referenceFilePath"
    exit 1
}

# Read the reference file content
try {
    $referenceContent = Get-Content -Path $referenceFilePath -Raw
    Write-Host "Reference .roomodes file loaded from $referenceFilePath" -ForegroundColor Green
} catch {
    Write-Error "Failed to read reference .roomodes file: $_"
    exit 1
}

# Find all .roomodes files in the c:/repos directory
Write-Host "Searching for .roomodes files in c:/repos..." -ForegroundColor Yellow
$roomodesFiles = Get-ChildItem -Path "c:/repos" -Filter ".roomodes" -Recurse -File -ErrorAction SilentlyContinue

# Initialize counters
$matchCount = 0
$mismatchCount = 0
$updatedCount = 0
$errorCount = 0

# Process each found file
Write-Host "Found $($roomodesFiles.Count) .roomodes files" -ForegroundColor Cyan
foreach ($file in $roomodesFiles) {
    # Skip the reference file
    if ($file.FullName -eq $referenceFilePath) {
        Write-Host "Skipping reference file: $($file.FullName)" -ForegroundColor Gray
        continue
    }
    
    try {
        # Read the current file content
        $currentContent = Get-Content -Path $file.FullName -Raw
        
        # Compare with reference content
        if ($currentContent -eq $referenceContent) {
            Write-Host "MATCH: $($file.FullName)" -ForegroundColor Green
            $matchCount++
        } else {
            Write-Host "MISMATCH: $($file.FullName)" -ForegroundColor Red
            $mismatchCount++
            
            # Update the file if requested
            if ($UpdateFiles) {
                try {
                    # Display file content before update for debugging
                    Write-Host "  Original content:" -ForegroundColor Gray
                    $originalContentLines = $currentContent -split "`n" | Select-Object -First 3
                    foreach ($line in $originalContentLines) {
                        Write-Host "    $line" -ForegroundColor Gray
                    }
                    
                    # Check if file is read-only
                    $fileInfo = Get-Item -Path $file.FullName
                    if ($fileInfo.IsReadOnly) {
                        Write-Host "  File is read-only, attempting to make it writable..." -ForegroundColor Yellow
                        Set-ItemProperty -Path $file.FullName -Name IsReadOnly -Value $false
                    }
                    
                    # Try to take ownership of the file (requires admin privileges)
                    try {
                        Write-Host "  Attempting to take ownership of the file..." -ForegroundColor Yellow
                        $acl = Get-Acl -Path $file.FullName
                        $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
                        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($currentUser, "FullControl", "Allow")
                        $acl.SetAccessRule($rule)
                        Set-Acl -Path $file.FullName -AclObject $acl
                    } catch {
                        Write-Host "  Unable to take ownership (may require admin privileges): $_" -ForegroundColor Yellow
                    }
                    
                    # Try different methods to update the file
                    Write-Host "  Attempting to update file using multiple methods..." -ForegroundColor Yellow
                    
                    # Method 1: Using Set-Content with UTF8 encoding
                    [System.IO.File]::WriteAllText($file.FullName, $referenceContent, [System.Text.Encoding]::UTF8)
                    
                    # Verify the update
                    Start-Sleep -Seconds 1  # Give the file system a moment to update
                    $verifyContent = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
                    
                    # Compare content ignoring line ending differences
                    $normalizedReference = $referenceContent.Replace("`r`n", "`n").Replace("`r", "`n")
                    $normalizedVerify = $verifyContent.Replace("`r`n", "`n").Replace("`r", "`n")
                    
                    if ($normalizedVerify -eq $normalizedReference) {
                        Write-Host "  Updated to match reference file (Verified)" -ForegroundColor Green
                        $updatedCount++
                    } else {
                        Write-Host "  Update failed verification - content doesn't match after update" -ForegroundColor Red
                        Write-Host "  This may be due to file permissions or the file being locked by another process" -ForegroundColor Yellow
                        $errorCount++
                    }
                } catch {
                    Write-Host "  Failed to update file: $_" -ForegroundColor Red
                    $errorCount++
                }
            }
        }
    } catch {
        Write-Host "ERROR processing $($file.FullName): $_" -ForegroundColor Red
        $errorCount++
    }
}

# Display summary
Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "Total .roomodes files found: $($roomodesFiles.Count)" -ForegroundColor White
Write-Host "Files matching reference: $matchCount" -ForegroundColor Green
Write-Host "Files not matching reference: $mismatchCount" -ForegroundColor Red
if ($UpdateFiles) {
    Write-Host "Files updated: $updatedCount" -ForegroundColor Yellow
    Write-Host "Files failed to update: $($mismatchCount - $updatedCount)" -ForegroundColor Red
} else {
    Write-Host "To update mismatched files, run with -UpdateFiles `$true parameter" -ForegroundColor Yellow
}
Write-Host "Errors encountered: $errorCount" -ForegroundColor Red

# Provide instructions for updating files
if ($mismatchCount -gt 0 -and -not $UpdateFiles) {
    Write-Host "`nTo update all mismatched files to match the reference, run:" -ForegroundColor Yellow
    Write-Host ".\sync-roomodes.ps1 -UpdateFiles `$true" -ForegroundColor White
}
