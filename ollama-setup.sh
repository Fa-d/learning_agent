#!/bin/bash

# VizLearn LM Studio Setup Script
# Sets up and manages VizLearn container with LM Studio integration

set -e

echo "🎯 VizLearn LM Studio Setup"
echo "==========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\03    # Test LM Studio first
    echo "🔍 Testing LM Studio endpoint..."
    if curl -s http://127.0.0.1:1234/health > /dev/null 2>&1 || \
       curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
        print_success "LM Studio is accessible at http://127.0.0.1:1234"
        
        # Show available models if possible
        echo "📦 Available models:"
        curl -s http://127.0.0.1:1234/v1/models | python3 -m json.tool 2>/dev/null | grep '"id"' || echo "  Model information available via API"
    else
        print_error "LM Studio is not accessible at http://127.0.0.1:1234"
        print_warning "Please ensure LM Studio is running and a model is loaded"
        return 1
    fit_status() {
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

# Available models
AVAILABLE_MODELS=(
    "llama2:7b"
    "llama2:13b"
    "codellama:7b"
    "codellama:13b"
    "mistral:7b"
    "neural-chat:7b"
    "starling-lm:7b"
    "vicuna:7b"
    "orca-mini:3b"
    "phi:2.7b"
    "gemma2:27b"
    "gemma2:9b"
    "gemma2:2b"
)

show_help() {
    echo "VizLearn LM Studio Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  setup         - Initial setup of VizLearn container"
    echo "  start         - Start VizLearn services"
    echo "  stop          - Stop VizLearn services"
    echo "  restart       - Restart VizLearn services"
    echo "  logs          - Show VizLearn logs"
    echo "  shell         - Open shell in VizLearn container"
    echo "  test          - Test the API connections"
    echo "  clean         - Remove all containers and volumes"
    echo "  help          - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup                    # Initial setup"
    echo "  $0 start                    # Start VizLearn API"
    echo "  $0 test                     # Test LM Studio connection"
    echo ""
    echo "Prerequisites:"
    echo "  - LM Studio running on http://127.0.0.1:1234"
    echo "  - Your Gemma model loaded in LM Studio"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    print_success "Docker and Docker Compose are available"
}

setup_environment() {
    print_status "Setting up environment for Ollama..."
    
    # Create models directory
    mkdir -p models
    print_success "Created models directory"
    
    # Create .env file for Ollama
    if [ ! -f ".env.ollama" ]; then
        cat > .env.ollama << EOF
# VizLearn with llama.cpp Configuration
LLM_BASE_URL=http://llama-cpp:8080/v1
LLM_API_KEY=sk-not-needed
LLM_MODEL=gemma-3n-e4b
API_HOST=0.0.0.0
API_PORT=8000
STATIC_API_KEY=vizlearn-static-key-2025
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
USER_AGENT=VizLearn/1.0 (https://github.com/Fa-d/learning_agent)
LOG_LEVEL=INFO
EOF
        print_success "Created .env.ollama configuration"
    else
        print_status ".env.ollama already exists"
    fi
    
    # Copy to .env for use
    cp .env.ollama .env
    print_success "Environment configured for Ollama"
}

start_services() {
    print_status "Starting llama.cpp services..."
    docker-compose -f docker-compose.ollama.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
        echo "🌐 VizLearn API: http://localhost:8000"
        echo "🤖 llama.cpp API: http://localhost:8080"
        echo ""
        print_status "Waiting for services to be ready..."
        wait_for_services
    else
        print_error "Failed to start services"
        exit 1
    fi
}

stop_services() {
    print_status "Stopping llama.cpp services..."
    docker-compose -f docker-compose.ollama.yml down
    print_success "Services stopped"
}

restart_services() {
    print_status "Restarting llama.cpp services..."
    docker-compose -f docker-compose.ollama.yml restart
    print_success "Services restarted"
}

show_logs() {
    print_status "Showing llama.cpp logs (press Ctrl+C to exit)..."
    docker-compose -f docker-compose.ollama.yml logs -f
}

open_shell() {
    print_status "Opening shell in llama.cpp container..."
    docker-compose -f docker-compose.ollama.yml exec llama-cpp /bin/bash
}

stop_services() {
    print_status "Stopping Ollama services..."
    docker-compose -f docker-compose.ollama.yml down
    print_success "Services stopped"
}

restart_services() {
    print_status "Restarting Ollama services..."
    docker-compose -f docker-compose.ollama.yml restart
    print_success "Services restarted"
}

pull_model() {
    local model=${1:-"llama2:7b"}
    print_status "Downloading model: $model"
    print_warning "This may take a while depending on model size..."
    
    docker-compose -f docker-compose.ollama.yml exec ollama ollama pull "$model"
    
    if [ $? -eq 0 ]; then
        print_success "Model $model downloaded successfully"
    else
        print_error "Failed to download model $model"
        exit 1
    fi
}

import_model() {
    local model_path="$1"
    local model_name="$2"
    
    if [ -z "$model_path" ] || [ -z "$model_name" ]; then
        print_error "Usage: $0 import <model-path> <model-name>"
        echo "Example: $0 import /lmstudio_models/unsloth/gemma-3n-E4B-it-GGUF/gemma-3n-E4B-it-UD-Q6_K_XL.gguf gemma-3n-e4b"
        exit 1
    fi
    
    print_status "Importing local GGUF model: $model_path"
    print_status "Model will be named: $model_name"
    
    # Create Modelfile for the import
    local modelfile="/tmp/Modelfile.${model_name}"
    cat > "$modelfile" << EOF
FROM $model_path
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF
    
    # Copy Modelfile to container
    docker cp "$modelfile" "$(docker-compose -f docker-compose.ollama.yml ps -q ollama):/tmp/Modelfile"
    
    # Import the model
    print_status "Creating model from GGUF file..."
    docker-compose -f docker-compose.ollama.yml exec ollama ollama create "$model_name" -f /tmp/Modelfile
    
    if [ $? -eq 0 ]; then
        print_success "Model $model_name imported successfully"
        print_status "You can now use the model with name: $model_name"
        
        # Clean up
        rm -f "$modelfile"
        docker-compose -f docker-compose.ollama.yml exec ollama rm /tmp/Modelfile
        
        # Test the model
        print_status "Testing the imported model..."
        docker-compose -f docker-compose.ollama.yml exec ollama ollama run "$model_name" "Hello, can you introduce yourself?" || true
    else
        print_error "Failed to import model $model_name"
        rm -f "$modelfile"
        exit 1
    fi
}

list_available_models() {
    echo "📚 Available Models:"
    echo "==================="
    for model in "${AVAILABLE_MODELS[@]}"; do
        echo "  - $model"
    done
    echo ""
    echo "To download a model: $0 pull <model-name>"
    echo "Example: $0 pull llama2:7b"
}

list_downloaded_models() {
    print_status "Listing downloaded models..."
    docker-compose -f docker-compose.ollama.yml exec ollama ollama list
}

show_logs() {
    print_status "Showing Ollama logs (press Ctrl+C to exit)..."
    docker-compose -f docker-compose.ollama.yml logs -f ollama
}

open_shell() {
    print_status "Opening shell in llama.cpp container..."
    docker-compose -f docker-compose.ollama.yml exec llama-cpp /bin/bash
}

wait_for_services() {
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for services to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "VizLearn API is ready!"
            
            # Check if llama.cpp is also ready (using /v1/models endpoint)
            if curl -s http://localhost:8080/v1/models > /dev/null 2>&1; then
                print_success "llama.cpp API is ready!"
                return 0
            fi
        fi
        
        echo "  Attempt $attempt/$max_attempts - Waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_warning "Services may not be fully ready. Use '$0 test' to check status."
    return 1
}

test_connection() {
    print_status "Testing API connections..."
    
    # Test llama.cpp OpenAI-compatible API
    echo "🔍 Testing llama.cpp API..."
    if curl -s http://localhost:8080/v1/models > /dev/null; then
        print_success "llama.cpp API is accessible"
        
        # Show available models
        echo "� Available models:"
        curl -s http://localhost:8080/v1/models | python3 -m json.tool 2>/dev/null | grep '"id"' || echo "  Model information available via API"
    else
        print_error "llama.cpp API is not accessible"
    fi
    
    # Test VizLearn API
    echo "🔍 Testing VizLearn API..."
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "VizLearn API is accessible"
        
        # Get health details
        health_response=$(curl -s http://localhost:8000/health)
        echo "Health status: $health_response"
        
        # Test LLM integration
        echo "🤖 Testing LLM integration..."
        test_response=$(curl -s -X POST "http://localhost:8000/chat/completions" \
            -H "Content-Type: application/json" \
            -d '{"model": "default", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10}')
        
        if echo "$test_response" | grep -q "choices"; then
            print_success "LLM integration working"
            echo "Response preview: $(echo "$test_response" | head -c 100)..."
        else
            print_warning "LLM integration test failed"
            echo "Response: $test_response"
        fi
    else
        print_error "VizLearn API is not accessible"
        print_warning "Run '$0 start' to start the VizLearn service"
    fi
}

clean_all() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose -f docker-compose.ollama.yml down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main command processing
case "${1:-}" in
    "setup")
        check_docker
        setup_environment
        print_success "Setup completed! Run '$0 start' to begin."
        ;;
    "start")
        check_docker
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "logs")
        show_logs
        ;;
    "shell")
        open_shell
        ;;
    "test")
        test_connection
        ;;
    "clean")
        clean_all
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        print_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
