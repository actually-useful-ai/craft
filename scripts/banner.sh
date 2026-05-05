#!/usr/bin/env bash
# banner.sh — ASCII banners for the craft cycle phases.
# Usage: bash scripts/banner.sh <PHASE> [subtitle]

set -euo pipefail

NAME="${1:-CRAFT}"
SUBTITLE="${2:-}"
RESET='\033[0m'

get_font() {
    case "$1" in
        DISCUSS)     echo "calvin_s" ;;
        COMPOSE)     echo "smbraille" ;;
        DISTILL)     echo "emboss2" ;;
        RECONSIDER)  echo "broadway_kb" ;;
        PRESENT)     echo "fourtops" ;;
        CONTEXT)     echo "linux" ;;
        BOARD)       echo "straight" ;;
        CRAFT)       echo "calvin_s" ;;
        *)           echo "small" ;;
    esac
}

get_color() {
    case "$1" in
        DISCUSS)     echo '\033[1;36m' ;;  # bold cyan
        COMPOSE)     echo '\033[1;33m' ;;  # bold yellow
        DISTILL)     echo '\033[1;32m' ;;  # bold green
        RECONSIDER)  echo '\033[1;31m' ;;  # bold red
        PRESENT)     echo '\033[1;35m' ;;  # bold magenta
        CONTEXT)     echo '\033[1;34m' ;;  # bold blue
        BOARD)       echo '\033[0;37m' ;;  # white
        CRAFT)       echo '\033[1;33m' ;;  # bold yellow
        PHASE*)      echo '\033[1;37m' ;;  # bold white
        *)           echo '\033[0m' ;;
    esac
}

FONT=$(get_font "$NAME")
COLOR=$(get_color "$NAME")

if python3 -c "import pyfiglet" 2>/dev/null; then
    printf "${COLOR}"
    python3 -c "import pyfiglet; print(pyfiglet.figlet_format('$NAME', font='$FONT').rstrip())"
    printf "${RESET}"
elif command -v toilet &>/dev/null; then
    printf "${COLOR}"
    toilet -f future "$NAME"
    printf "${RESET}"
elif command -v figlet &>/dev/null; then
    printf "${COLOR}"
    figlet -f small "$NAME"
    printf "${RESET}"
else
    printf "${COLOR}═══ %s ═══${RESET}\n" "$NAME"
fi

if [[ -n "$SUBTITLE" ]]; then
    printf "${COLOR}  %s${RESET}\n" "$SUBTITLE"
fi
