# OpenClaw Guardrails - Windows Installer
# PowerShell script for Windows 10/11
#
# Usage:
#   Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.ps1 | Invoke-Expression
#   # or
#   powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

function Log-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Log-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Check-Prereqs {
    # Check git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Log-Error "git is required but not installed."
        Log-Info "Install from: https://git-scm.com/download/win"
        exit 1
    }

    # Check python3
    if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            Log-Error "python3 is required but not installed."
            Log-Info "Install from: https://www.python.org/downloads/"
            exit 1
        }
    }

    # Check OpenClaw
    if (-not (Get-Command openclaw -ErrorAction SilentlyContinue)) {
        Log-Error "OpenClaw is required but not installed."
        Log-Info "Install from: https://docs.openclaw.ai/"
        exit 1
    }

    Log-Info "All prerequisites met"
}

function Install-Skills {
    $SkillsDir = Join-Path $HOME ".openclaw\skills"
    $InstallDir = Join-Path $SkillsDir "openclaw-guardrails"

    # Create skills directory
    if (-not (Test-Path $SkillsDir)) {
        Log-Info "Creating skills directory: $SkillsDir"
        New-Item -ItemType Directory -Path $SkillsDir | Out-Null
    }

    # Remove existing installation
    if (Test-Path $InstallDir) {
        Log-Info "Removing existing installation..."
        Remove-Item -Recurse -Force $InstallDir
    }

    # Clone repository
    Log-Info "Cloning openclaw-guardrails..."
    git clone --depth 1 https://github.com/lttcnly/openclaw-guardrails.git $InstallDir

    Log-Info "Installation complete: $InstallDir"
}

function Setup-Cron {
    Log-Info "Setting up daily monitoring..."

    # Check if cron job exists
    $cronList = openclaw cron list 2>$null
    if ($cronList -match "guardrails:daily") {
        Log-Warn "Cron job 'guardrails:daily' already exists, skipping..."
        return
    }

    # Create cron job
    openclaw cron add --name guardrails:daily `
        --cron "17 3 * * *" `
        --session isolated `
        --light-context `
        --no-deliver `
        --message "Daily guardrails: exec python3 `$env:USERPROFILE\.openclaw\skills\openclaw-guardrails\scripts\run_daily.py. Save artifacts under reports/. Alert on critical."

    Log-Info "Daily cron job created (runs at 03:17)"
}

function Run-Initial-Scan {
    Log-Info "Running initial security scan..."
    
    $InstallDir = Join-Path $HOME ".openclaw\skills\openclaw-guardrails"
    $LogPath = "$env:TEMP\guardrails-initial.log"
    
    Set-Location $InstallDir
    python3 scripts\run_daily.py > $LogPath 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Log-Info "Initial scan completed successfully"
        Log-Info "View reports in: $InstallDir\reports\"
    } else {
        Log-Warn "Initial scan completed with warnings (check logs)"
    }
}

function Print-Next-Steps {
    Write-Host ""
    Log-Info "✅ Installation complete!"
    Write-Host ""
    Write-Host "📊 Next steps:"
    Write-Host "   1. View reports: ls `$env:USERPROFILE\.openclaw\skills\openclaw-guardrails\reports\"
    Write-Host "   2. Open dashboard: start `$env:USERPROFILE\.openclaw\skills\openclaw-guardrails\reports\dashboard-*.html"
    Write-Host "   3. Run manual scan: python3 `$env:USERPROFILE\.openclaw\skills\openclaw-guardrails\scripts\run_daily.py"
    Write-Host "   4. View cron jobs: openclaw cron list"
    Write-Host ""
    Write-Host "📚 Documentation: https://github.com/lttcnly/openclaw-guardrails"
    Write-Host ""
}

# Main
Write-Host "🛡️  OpenClaw Guardrails Installer" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Check-Prereqs
Install-Skills
Setup-Cron
Run-Initial-Scan
Print-Next-Steps
