#!/bin/bash

# VizLearn Startup Script
# This script sets up and runs the VizLearn API server

set -e  # Exit on any error

echo "🚀 VizLearn API Startup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_success "Found Python $PYTHON_VERSION"
    
    # Check if version is 3.11+
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        print_warning "Python 3.11+ is recommended. Current version: $PYTHON_VERSION"
    fi
}

# Check if local LLM is running
check_llm_server() {
    print_status "Checking local LLM server..."
    
    if curl -s http://localhost:1234/v1/models &> /dev/null; then
        print_success "Local LLM server is running on port 1234"
    else
        print_warning "Local LLM server not detected on port 1234"
        print_warning "Please start your LLM server (e.g., LM Studio) before running the API"
        echo
        echo "To start LM Studio:"
        echo "1. Open LM Studio"
        echo "2. Load a model"
        echo "3. Start the local server on port 1234"
        echo
        read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
    fi
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env from .env.example"
            print_warning "Please review and update .env file with your configuration"
        else
            print_warning ".env file not found, creating basic configuration..."
            cat > .env << EOF
# VizLearn Configuration
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=sk-not-needed
LLM_MODEL=local-model
API_HOST=0.0.0.0
API_PORT=8000
STATIC_API_KEY=vizlearn-static-key-2025
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
USER_AGENT=VizLearn/1.0 (https://github.com/Fa-d/learning_agent)
LOG_LEVEL=INFO
EOF
            print_success "Created basic .env file"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Run the application
run_app() {
    print_status "Starting VizLearn API server..."
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        print_error "main.py not found in current directory"
        exit 1
    fi
    
    print_success "Starting server on http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health Check: http://localhost:8000/health"
    echo
    print_status "Press Ctrl+C to stop the server"
    echo
    
    # Run with uvicorn for better production performance
    if command -v uvicorn &> /dev/null; then
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    else
        $PYTHON_CMD main.py
    fi
}

# Handle command line arguments
case "${1:-}" in
    "docker")
        print_status "Building and running with Docker..."
        docker-compose up --build
        ;;
    "docker-build")
        print_status "Building Docker image..."
        docker build -t vizlearn .
        print_success "Docker image built successfully"
        ;;
    "test")
        print_status "Running API tests..."
        if [ -f "examples/test_api.py" ]; then
            check_python
            setup_venv
            $PYTHON_CMD examples/test_api.py
        else
            print_error "Test file not found: examples/test_api.py"
            exit 1
        fi
        ;;
    "clean")
        print_status "Cleaning up..."
        rm -rf venv __pycache__ src/__pycache__ .pytest_cache
        print_success "Cleanup completed"
        ;;
    "help"|"-h"|"--help")
        echo "VizLearn Startup Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  (no args)    - Run the API server normally"
        echo "  docker       - Build and run with Docker Compose"
        echo "  docker-build - Build Docker image only"
        echo "  test         - Run API tests"
        echo "  clean        - Clean up generated files"
        echo "  help         - Show this help message"
        echo
        exit 0
        ;;
    "")
        # Default: run the application
        check_python
        check_llm_server
        setup_venv
        install_dependencies
        setup_env
        run_app
        ;;
    *)
        print_error "Unknown command: $1"
        print_status "Use '$0 help' for usage information"
        exit 1
        ;;
esac
