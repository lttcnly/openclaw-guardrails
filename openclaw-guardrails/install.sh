#!/usr/bin/env bash
# OpenClaw Guardrails - Cross-Platform Installer
# Supports: macOS, Linux, Windows (Git Bash/WSL)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.sh | bash
#   # or
#   wget -qO- https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
detect_os() {
    if [[ "$(uname)" == "Darwin" ]]; then
        OS="macos"
    elif [[ "$(uname)" == "Linux" ]]; then
        OS="linux"
    elif [[ "$(uname)" == *"MINGW"* ]] || [[ "$(uname)" == *"MSYS"* ]]; then
        OS="windows"
    else
        log_error "Unsupported OS: $(uname)"
        exit 1
    fi
    log_info "Detected OS: $OS"
}

# Check prerequisites
check_prereqs() {
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed."
        log_info "Install git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
        exit 1
    fi

    # Check python3
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is required but not installed."
        log_info "Install Python 3.10+: https://www.python.org/downloads/"
        exit 1
    fi

    # Check OpenClaw
    if ! command -v openclaw &> /dev/null; then
        log_error "OpenClaw is required but not installed."
        log_info "Install OpenClaw: https://docs.openclaw.ai/"
        exit 1
    fi

    log_info "All prerequisites met"
}

# Install to OpenClaw skills directory
install_skills() {
    local skills_dir="$HOME/.openclaw/skills"
    
    # Create skills directory if not exists
    if [[ ! -d "$skills_dir" ]]; then
        log_info "Creating skills directory: $skills_dir"
        mkdir -p "$skills_dir"
    fi

    # Remove existing installation
    if [[ -d "$skills_dir/openclaw-guardrails" ]]; then
        log_info "Removing existing installation..."
        rm -rf "$skills_dir/openclaw-guardrails"
    fi

    # Clone repository
    log_info "Cloning openclaw-guardrails..."
    git clone --depth 1 https://github.com/lttcnly/openclaw-guardrails.git "$skills_dir/openclaw-guardrails"

    log_info "Installation complete: $skills_dir/openclaw-guardrails"
}

# Setup daily cron job
setup_cron() {
    log_info "Setting up daily monitoring..."
    
    # Check if cron job already exists
    if openclaw cron list 2>/dev/null | grep -q "guardrails:daily"; then
        log_warn "Cron job 'guardrails:daily' already exists, skipping..."
        return 0
    fi

    # Create cron job
    openclaw cron add --name guardrails:daily \
        --cron "17 3 * * *" \
        --session isolated \
        --light-context \
        --no-deliver \
        --message "Daily guardrails: exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py (fallback: python). Save artifacts under reports/. Alert on critical."

    log_info "Daily cron job created (runs at 03:17)"
}

# Run initial scan
run_initial_scan() {
    log_info "Running initial security scan..."
    
    cd "$HOME/.openclaw/skills/openclaw-guardrails"
    python3 scripts/run_daily.py > /tmp/guardrails-initial.log 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_info "Initial scan completed successfully"
        log_info "View reports in: $HOME/.openclaw/skills/openclaw-guardrails/reports/"
    else
        log_warn "Initial scan completed with warnings (check logs)"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    log_info "✅ Installation complete!"
    echo ""
    echo "📊 Next steps:"
    echo "   1. View reports: ls ~/.openclaw/skills/openclaw-guardrails/reports/"
    echo "   2. Open dashboard: open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html"
    echo "   3. Run manual scan: python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
    echo "   4. View cron jobs: openclaw cron list"
    echo ""
    echo "📚 Documentation: https://github.com/lttcnly/openclaw-guardrails"
    echo ""
}

# Main
main() {
    echo "🛡️  OpenClaw Guardrails Installer"
    echo "================================"
    echo ""

    detect_os
    check_prereqs
    install_skills
    setup_cron
    run_initial_scan
    print_next_steps
}

main "$@"
