#!/bin/bash

echo "🚀 Setting up VizLearn for Docker..."

# Update .env for Docker usage
if [ -f ".env" ]; then
    echo "📝 Updating .env for Docker..."
    # Update LLM_BASE_URL for Docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's|LLM_BASE_URL=http://localhost:1234/v1|LLM_BASE_URL=http://host.docker.internal:1234/v1|g' .env
    else
        # Linux
        sed -i 's|LLM_BASE_URL=http://localhost:1234/v1|LLM_BASE_URL=http://host.docker.internal:1234/v1|g' .env
    fi
    echo "✅ Updated .env for Docker networking"
else
    echo "📝 Creating .env for Docker..."
    cat > .env << EOF
# VizLearn Configuration for Docker
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_API_KEY=sk-not-needed
LLM_MODEL=local-model
API_HOST=0.0.0.0
API_PORT=8000
STATIC_API_KEY=vizlearn-static-key-2025
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
USER_AGENT=VizLearn/1.0 (https://github.com/Fa-d/learning_agent)
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env for Docker"
fi

echo ""
echo "🐳 Docker Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Make sure LM Studio is running on your host machine (port 1234)"
echo "2. Run: docker-compose up --build"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "Note: The API will start even if LM Studio is not running,"
echo "      but will work in degraded mode without LLM features."
