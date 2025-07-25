#!/bin/bash

echo "🎯 VizLearn LM Studio Connection Test"
echo "===================================="
echo

# Test 1: LM Studio Direct Connection
echo "1. Testing LM Studio direct connection..."
if curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio is accessible at http://127.0.0.1:1234"
    echo "📦 Available models:"
    curl -s http://127.0.0.1:1234/v1/models | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('data', []):
        print(f'  - {model.get(\"id\", \"unknown\")}')
except:
    print('  Model list available via API')
" 2>/dev/null || echo "  Model information available"
else
    echo "❌ LM Studio is not accessible"
    echo "   Please ensure LM Studio is running with a model loaded"
    exit 1
fi

echo

# Test 2: VizLearn Container Status
echo "2. Testing VizLearn container..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ VizLearn API is running"
    health_status=$(curl -s http://localhost:8000/health)
    echo "📊 Health Status: $health_status"
else
    echo "❌ VizLearn API is not running"
    echo "   Run: docker-compose -f docker-compose.ollama.yml up -d"
    exit 1
fi

echo

# Test 3: Container to LM Studio Connection
echo "3. Testing container to LM Studio connection..."
if docker exec vizlearn-vizlearn-api-1 python -c "
import requests
try:
    r = requests.get('http://host.docker.internal:1234/v1/models', timeout=5)
    print(f'✅ Container can reach LM Studio (Status: {r.status_code})')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "✅ Container networking is working"
else
    echo "❌ Container cannot reach LM Studio"
    exit 1
fi

echo
echo "🎉 Setup Summary:"
echo "✅ LM Studio: Running and accessible"
echo "✅ VizLearn API: Running on http://localhost:8000"
echo "✅ Docker Networking: Container can reach host LM Studio"
echo
echo "🔗 Your VizLearn container is now connected to LM Studio!"
echo "   - LM Studio endpoint: http://127.0.0.1:1234"
echo "   - VizLearn API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo
echo "Next steps:"
echo "1. Test the API at http://localhost:8000/docs"
echo "2. Use API key: vizlearn-static-key-2025"
echo "3. Enjoy generating content with your local Gemma model!"
