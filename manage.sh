#!/bin/bash

# VizLearn Management Script for LM Studio Integration
# Simple script to manage VizLearn container connected to local LM Studio

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🎯 VizLearn LM Studio Setup"
    echo "=========================="
    echo -e "${NC}"
}

show_help() {
    print_header
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start VizLearn container"
    echo "  stop      - Stop VizLearn container" 
    echo "  restart   - Restart VizLearn container"
    echo "  logs      - Show container logs"
    echo "  test      - Test LM Studio connection"
    echo "  clean     - Remove containers and images"
    echo "  help      - Show this help"
    echo ""
    echo "Prerequisites:"
    echo "  - LM Studio running on http://127.0.0.1:1234"
    echo "  - A model loaded in LM Studio"
    echo ""
    echo "API Access:"
    echo "  - VizLearn API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "  - API Key: vizlearn-static-key-2025"
}

check_lm_studio() {
    print_status "Checking LM Studio connection..."
    if curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
        print_success "LM Studio is running and accessible"
        return 0
    else
        print_error "LM Studio is not accessible at http://127.0.0.1:1234"
        print_warning "Please start LM Studio and load a model before proceeding"
        return 1
    fi
}

start_service() {
    print_header
    
    if ! check_lm_studio; then
        exit 1
    fi
    
    print_status "Starting VizLearn container..."
    docker-compose up -d --build
    
    print_status "Waiting for service to be ready..."
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "VizLearn API is running at http://localhost:8000"
        print_success "API Documentation available at http://localhost:8000/docs"
        print_success "Use API key: vizlearn-static-key-2025"
    else
        print_warning "Service may still be starting. Check logs with: $0 logs"
    fi
}

stop_service() {
    print_header
    print_status "Stopping VizLearn container..."
    docker-compose down
    print_success "VizLearn container stopped"
}

restart_service() {
    print_header
    print_status "Restarting VizLearn container..."
    docker-compose restart
    print_success "VizLearn container restarted"
}

show_logs() {
    print_header
    print_status "Showing VizLearn container logs..."
    docker-compose logs -f vizlearn-api
}

test_connection() {
    print_header
    
    # Test 1: LM Studio
    echo "1. Testing LM Studio..."
    if curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
        print_success "LM Studio is accessible"
        echo "   Available models:"
        curl -s http://127.0.0.1:1234/v1/models | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('data', []):
        print(f'     - {model.get(\"id\", \"unknown\")}')
except:
    print('     Model list available')
" 2>/dev/null || echo "     Model information available"
    else
        print_error "LM Studio not accessible"
        return 1
    fi
    
    echo ""
    
    # Test 2: VizLearn API
    echo "2. Testing VizLearn API..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "VizLearn API is accessible"
        health_status=$(curl -s http://localhost:8000/health)
        echo "   Status: $health_status"
    else
        print_error "VizLearn API not accessible"
        print_warning "Run '$0 start' to start the service"
        return 1
    fi
    
    echo ""
    print_success "All services are working correctly!"
}

clean_all() {
    print_header
    print_warning "This will remove all VizLearn containers and images!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker image rm vizlearn-vizlearn-api 2>/dev/null || true
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main command processing
case "${1:-}" in
    "start")
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        restart_service
        ;;
    "logs")
        show_logs
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
