#!/bin/bash

# News Summarizer API Startup Script
# This script helps you start the API server with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    print_info "Python 3 found: $(python3 --version)"
}

# Check if required files exist
check_files() {
    if [ ! -f "api.py" ]; then
        print_error "api.py not found. Make sure you're in the correct directory."
        exit 1
    fi

    if [ ! -f "news_summarizer.py" ]; then
        print_error "news_summarizer.py not found. Make sure you're in the correct directory."
        exit 1
    fi

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Make sure you're in the correct directory."
        exit 1
    fi

    print_info "Required files found"
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_info "Dependencies installed successfully"
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f ".env" ]; then
        if [ -f "config.example.env" ]; then
            print_info "Creating .env file from example..."
            cp config.example.env .env
            print_warning "Please edit .env file and update the API_KEY and other configuration values"
        else
            print_info "Creating basic .env file..."
            cat > .env << EOF
API_KEY=your-secure-api-key-here-please-change-this
RATE_LIMIT_REQUESTS=5/minute
RATE_LIMIT_BURST=10/hour
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
EOF
            print_warning "Please edit .env file and update the API_KEY"
        fi
    else
        print_info ".env file already exists"
    fi
}

# Create logs directory
create_logs_dir() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
        print_info "Created logs directory"
    fi
}

# Start the API server
start_server() {
    local mode=$1

    print_info "Starting News Summarizer API..."

    # Source environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi

    case $mode in
        "dev"|"development")
            print_info "Starting in development mode with auto-reload..."
            python3 api.py
            ;;
        "prod"|"production")
            print_info "Starting in production mode..."
            if command -v uvicorn &> /dev/null; then
                uvicorn api:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 4
            else
                print_warning "uvicorn not found, falling back to development mode"
                python3 api.py
            fi
            ;;
        *)
            print_info "Starting in default mode..."
            python3 api.py
            ;;
    esac
}

# Show help
show_help() {
    cat << EOF
News Summarizer API Startup Script

Usage: $0 [OPTION]

Options:
    dev, development     Start in development mode with auto-reload
    prod, production     Start in production mode with multiple workers
    install             Install dependencies only
    setup               Setup environment without starting server
    help                Show this help message

Examples:
    $0                  Start API in default mode
    $0 dev              Start API in development mode
    $0 prod             Start API in production mode
    $0 install          Install dependencies only
    $0 setup            Setup environment files

Environment Variables:
    API_KEY             Your secure API key (required)
    HOST                Server host (default: 0.0.0.0)
    PORT                Server port (default: 8000)
    LOG_LEVEL           Logging level (default: INFO)

EOF
}

# Main function
main() {
    print_info "News Summarizer API Startup Script"
    print_info "==================================="

    case "${1:-start}" in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "install")
            check_python
            check_files
            install_dependencies
            print_info "Dependencies installed. Run '$0 setup' to configure environment."
            exit 0
            ;;
        "setup")
            check_python
            check_files
            create_env_file
            create_logs_dir
            print_info "Environment setup complete. Edit .env file and run '$0' to start the server."
            exit 0
            ;;
        "dev"|"development")
            check_python
            check_files
            create_env_file
            create_logs_dir
            start_server "dev"
            ;;
        "prod"|"production")
            check_python
            check_files
            create_env_file
            create_logs_dir
            start_server "prod"
            ;;
        "start"|"")
            check_python
            check_files
            create_env_file
            create_logs_dir
            start_server
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
