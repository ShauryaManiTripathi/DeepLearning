#!/bin/bash

# Configuration
REPO_PATH="$(pwd)"  # Default to current directory
BRANCH="main"
COMMIT_INTERVAL=3600  # Default interval in seconds (1 hour)
MAX_RETRIES=3
LOG_FILE="$HOME/.git-auto-commit.log"
COMMIT_PREFIX="[Auto]"  # Prefix for commit messages

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} - ${message}" >> "$LOG_FILE"
    echo -e "${message}"
}

# Function to check if repository is clean
check_repo_status() {
    cd "$REPO_PATH" || exit 1
    
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_message "${RED}Error: Not a git repository${NC}"
        return 1
    fi

    if [ -z "$(git status --porcelain)" ]; then
        log_message "${YELLOW}No changes to commit${NC}"
        return 1
    fi

    return 0
}

# Function to perform git operations
do_git_operations() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        # Pull latest changes
        if git pull origin "$BRANCH"; then
            # Add all changes
            git add .
            
            # Create commit message with date and changes summary
            local changes=$(git status --porcelain | wc -l)
            local commit_message="${COMMIT_PREFIX} $(date '+%Y-%m-%d %H:%M:%S') - ${changes} files changed"
            
            # Commit changes
            if git commit -m "$commit_message"; then
                # Push changes
                if git push origin "$BRANCH"; then
                    log_message "${GREEN}Successfully committed and pushed changes${NC}"
                    return 0
                fi
            fi
        fi
        
        # If we get here, something failed
        retry_count=$((retry_count + 1))
        log_message "${YELLOW}Retry attempt $retry_count of $MAX_RETRIES${NC}"
        sleep 5
    done
    
    log_message "${RED}Failed to complete git operations after $MAX_RETRIES attempts${NC}"
    return 1
}

# Function to check internet connection
check_internet() {
    if ping -c 1 github.com >/dev/null 2>&1; then
        return 0
    else
        log_message "${YELLOW}No internet connection. Waiting...${NC}"
        return 1
    fi
}

# Main loop
main() {
    log_message "Starting git auto-commit service..."
    
    while true; do
        if check_internet; then
            if check_repo_status; then
                do_git_operations
            fi
        fi
        
        sleep "$COMMIT_INTERVAL"
    done
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--path)
            REPO_PATH="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -i|--interval)
            COMMIT_INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-p|--path <repo_path>] [-b|--branch <branch>] [-i|--interval <seconds>]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Start the script
main
