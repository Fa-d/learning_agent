# VizLearn - AI-Powered Learning Content Generator

VizLearn is a production-ready FastAPI application that generates interactive learning content using local LLM models. It supports streaming responses and generates various types of educational questions including fill-in-the-blank, true/false, and ordering tasks.

## 🚀 Features

- **Streaming Content Generation**: Real-time question generation with Server-Sent Events
- **Multiple Question Types**: Fill-in-the-blank, True/False, and Ordering tasks
- **Local LLM Integration**: Works with local language models via LM Studio or similar
- **Production Ready**: Includes authentication, health checks, and proper error handling
- **Containerized**: Docker and Docker Compose support
- **Web Search Integration**: Enriches content using DuckDuckGo search
- **Type-Safe**: Full TypeScript interfaces and Pydantic models

## 🏗️ Architecture

```
Frontend → FastAPI → Local LLM (localhost:1234)
                  ↓
              Web Search (DuckDuckGo)
```

## 📁 Project Structure

```
VizLearn/
├── src/                      # Source code
│   ├── api/                  # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/                 # Core configuration and models
│   │   ├── __init__.py
│   │   ├── config.py         # Application settings
│   │   └── models.py         # Pydantic models
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication service
│   │   └── content_generation.py  # LLM content generation
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── web_search.py     # Web search functionality
│   └── __init__.py
├── examples/                 # Example scripts and tests
├── app.py                    # FastAPI application factory
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Docker Compose setup
└── .env.example             # Environment variables template
```

## 📋 Prerequisites

- Python 3.11+
- Docker (optional)
- Local LLM server running on `localhost:1234` (e.g., LM Studio)

## 🛠️ Installation

### Option 1: Local Development

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/VizLearn
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start your local LLM server** (e.g., LM Studio on port 1234)

5. **Run the application**:
   ```bash
   python main.py
   # or
   python app.py
   ```

### Option 2: Docker with Host LLM

**Important**: When running in Docker, the container needs to access your host machine's LM Studio server.

1. **Setup for Docker**:
   ```bash
   ./docker-setup.sh
   ```

2. **Start your local LLM server** (e.g., LM Studio on port 1234)

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

### Option 3: Docker with Ollama (Recommended)

**Best option for containerized open-source models**

1. **Setup Ollama environment**:
   ```bash
   ./ollama-setup.sh setup
   ```

2. **Download a model** (choose based on your needs):
   ```bash
   # Recommended for educational content (Google's latest)
   ./ollama-setup.sh pull gemma2:9b
   
   # Premium quality (requires more resources)
   ./ollama-setup.sh pull gemma2:27b
   
   # For code-focused content
   ./ollama-setup.sh pull codellama:7b
   
   # Lightweight for testing
   ./ollama-setup.sh pull gemma2:2b
   ```

3. **Start all services**:
   ```bash
   ./ollama-setup.sh start
   ```

4. **Test the setup**:
   ```bash
   ./ollama-setup.sh test
   ```

**Ollama Benefits:**
- ✅ Fully containerized - no host dependencies
- ✅ Multiple open-source models available
- ✅ GPU acceleration support
- ✅ OpenAI-compatible API
- ✅ Easy model management

4. **Or build and run manually**:
   ```bash
   docker build -t vizlearn .
   docker run -p 8000:8000 --add-host host.docker.internal:host-gateway vizlearn
   ```

**Note**: The API will start successfully even if LM Studio is not running, but will operate in degraded mode without LLM features.

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# LLM Configuration
# For local development:
LLM_BASE_URL=http://localhost:1234/v1
# For Docker:
# LLM_BASE_URL=http://host.docker.internal:1234/v1
# For Ollama:
# LLM_BASE_URL=http://ollama-openai-proxy:8080/v1

LLM_API_KEY=sk-not-needed
LLM_MODEL=local-model  # or llama2, codellama, etc. for Ollama

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Authentication
STATIC_API_KEY=vizlearn-static-key-2025

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Docker Note**: Use `./docker-setup.sh` to automatically configure `.env` for Docker networking.
**Ollama Note**: Use `./ollama-setup.sh setup` to automatically configure for Ollama.

## 🦙 Ollama Model Management

### Available Models
```bash
# List all available models
./ollama-setup.sh list

# List downloaded models
./ollama-setup.sh models
```

### Recommended Models by Use Case

**🎓 Educational Content (Recommended)**:
- `gemma2:9b` (5.4GB) ⭐ **New Recommendation** - Google's latest, excellent reasoning
- `gemma2:27b` (16GB) 🚀 **Premium** - Google's flagship, top performance  
- `llama2:7b` (4.1GB) - Well-balanced, good general knowledge
- `mistral:7b` (4.1GB) - Fast responses, efficient

**💻 Programming/Tech Content**:
- `codellama:7b` (3.8GB) - Specialized for code explanations
- `codellama:13b` (7.3GB) - Better code understanding

**⚡ Development/Testing**:
- `gemma2:2b` (1.6GB) ⭐ **Fast & Quality** - Google's compact model
- `orca-mini:3b` (1.9GB) - Quick setup, good performance
- `phi:2.7b` (1.6GB) - Very efficient, good for testing

### Model Management Commands
```bash
# Download a specific model
./ollama-setup.sh pull llama2:7b

# Start/stop services
./ollama-setup.sh start
./ollama-setup.sh stop
./ollama-setup.sh restart

# View logs
./ollama-setup.sh logs

# Test connections
./ollama-setup.sh test

# Clean up everything
./ollama-setup.sh clean
```

## 📚 API Documentation

Once running, visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Key Endpoints

#### POST `/generate-content`
Generate learning content in batch mode.

```json
{
  "title": "Introduction to Python",
  "description": "Basic Python programming concepts",
  "num_questions": 5,
  "question_types": ["fill_in_the_blank", "true_false", "ordering_task"]
}
```

#### POST `/generate-content/stream`
Generate learning content with streaming (Server-Sent Events).

Same request format as batch, but returns streaming responses:

```
data: {"status": "started", "message": "Starting content generation..."}
data: {"status": "progress", "item": {...}}
data: {"status": "completed", "message": "Content generation completed"}
```

#### GET `/content-types`
Get supported question types and descriptions.

### Authentication

All endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer vizlearn-static-key-2025" \
     http://localhost:8000/health
```

## 🧪 Testing

### Python Test Script
```bash
cd examples
python test_api.py
```

### Frontend Integration
Open `examples/frontend_example.js` to see JavaScript integration examples.

### Manual Testing with curl

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Generate Content**:
```bash
curl -X POST http://localhost:8000/generate-content \
  -H "Authorization: Bearer vizlearn-static-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "JavaScript Basics",
    "description": "Variables and functions in JavaScript",
    "num_questions": 3
  }'
```

**Streaming Generation**:
```bash
curl -X POST http://localhost:8000/generate-content/stream \
  -H "Authorization: Bearer vizlearn-static-key-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Python fundamentals",
    "num_questions": 2
  }'
```

## 📊 Question Types

### Fill in the Blank
```json
{
  "type": "fill_in_the_blank",
  "content": {
    "template": "Python is a ____ programming language that supports ____.",
    "gaps": ["high-level", "multiple paradigms"]
  }
}
```

### True/False
```json
{
  "type": "true_false",
  "content": {
    "question": {
      "text": "Python is an interpreted language.",
      "image": null
    },
    "options": [
      {"id": "1", "text": "True", "image": null, "is_correct": true},
      {"id": "2", "text": "False", "image": null, "is_correct": false}
    ]
  }
}
```

### Ordering Task
```json
{
  "type": "ordering_task",
  "content": {
    "sequences": [
      "Write the code",
      "Run the program", 
      "Debug errors",
      "Deploy to production"
    ]
  }
}
```

## 🚀 Deployment

### Production Checklist

1. **Update authentication**: Replace static API key with proper JWT/OAuth
2. **Configure CORS**: Set specific allowed origins
3. **Set up monitoring**: Add logging and metrics
4. **SSL/TLS**: Use HTTPS in production
5. **Rate limiting**: Implement request rate limiting
6. **Database**: Add persistent storage for generated content

### Docker Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  vizlearn-api:
    build: .
    ports:
      - "80:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - LOG_LEVEL=INFO
    restart: always
```

## 🔍 Monitoring

Health check endpoint provides service status:

```json
{
  "status": "healthy",
  "llm_service": "healthy",
  "timestamp": "2025-07-25T10:00:00.000Z"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**LLM Connection Failed**:
- Ensure local LLM server is running on port 1234
- Check firewall settings
- Verify LM Studio or similar is properly configured

**Docker Networking Issues**:
- For Docker: Use `http://host.docker.internal:1234/v1` as LLM_BASE_URL
- For Linux Docker: You may need to use `--network host` or the host's IP address
- Run `./docker-setup.sh` to automatically configure for Docker
- Ensure LM Studio is bound to `0.0.0.0:1234`, not just `localhost:1234`

**Docker Build Issues**:
- Ensure Docker daemon is running
- Check Docker Compose version compatibility

**Import Errors**:
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.11+ required)

**CORS Issues**:
- Update `ALLOWED_ORIGINS` in `.env`
- Check browser console for CORS errors

**API Starts but LLM Features Don't Work**:
- Check that LM Studio server is accessible from within Docker container
- Test connection: `curl http://host.docker.internal:1234/v1/models` from host
- The API will start in "degraded mode" if LLM is unavailable

### Logs

Check application logs:
```bash
# Docker
docker-compose logs -f vizlearn-api

# Local
python main.py  # Logs will appear in console
```

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review the examples directory

---

**Happy Learning! 🎓**

1.  **LM Studio:**
    *   Make sure your local LLM is running on LM Studio and the server is started (usually at `http://localhost:1234/v1`).

2.  **Install Dependencies:**
    *   Make sure you have Python installed. Then, open your terminal, activate the virtual environment, and run:
        ```bash
        pip install -r requirements.txt
        ```

## Usage

Once the setup is complete, run the application:

```bash
python src/app.py
```

The agent can also scrape content from specific URLs. To use this feature, simply include a URL in your prompt and ask the agent to summarize it, extract information, or perform other tasks based on the content of the page.