# Model Configuration for VizLearn Ollama Setup
# This file contains recommended models and their specifications

# Educational/General Purpose Models
EDUCATIONAL_MODELS=(
    "llama2:7b"           # 4.1GB - Good general knowledge
    "mistral:7b"          # 4.1GB - Fast and efficient
    "neural-chat:7b"      # 4.1GB - Good for conversational AI
    "starling-lm:7b"      # 4.1GB - Instruction following
    "gemma2:9b"           # 5.4GB - Google's latest, excellent reasoning
    "gemma2:27b"          # 16GB - Google's flagship model, top performance
)

# Code-focused Models
CODE_MODELS=(
    "codellama:7b"        # 3.8GB - Code generation and explanation
    "codellama:13b"       # 7.3GB - Better code understanding
    "phind-codellama:34b" # 19GB - Advanced code assistance
)

# Lightweight Models (for development/testing)
LIGHTWEIGHT_MODELS=(
    "orca-mini:3b"        # 1.9GB - Compact but capable
    "phi:2.7b"           # 1.6GB - Microsoft's efficient model
    "tinyllama:1.1b"     # 637MB - Ultra lightweight
    "gemma2:2b"          # 1.6GB - Google's compact model
)

# Specialized Models
SPECIALIZED_MODELS=(
    "vicuna:7b"          # 3.8GB - Good for creative tasks
    "wizard-vicuna:13b"  # 7.3GB - Enhanced reasoning
    "orca:13b"           # 7.3GB - Microsoft's research model
    "gemma2:27b"         # 16GB - Google's flagship for complex tasks
)

# Model recommendations by use case
echo "📚 Model Recommendations for VizLearn:"
echo "====================================="
echo ""
echo "🎓 For Educational Content Generation:"
echo "  - gemma2:9b (recommended) - Google's latest, excellent reasoning"
echo "  - llama2:7b - Well-balanced, good knowledge"
echo "  - mistral:7b - Fast responses, efficient"
echo "  - neural-chat:7b - Great for Q&A generation"
echo ""
echo "� For High-Quality Content (if you have resources):"
echo "  - gemma2:27b (premium) - Google's flagship, top performance"
echo ""
echo "�💻 For Programming/Tech Content:"
echo "  - codellama:7b (recommended) - Specialized for code"
echo "  - codellama:13b - Better code understanding"
echo ""
echo "⚡ For Development/Testing:"
echo "  - gemma2:2b - Google's compact model, good quality"
echo "  - orca-mini:3b - Quick setup, good performance"
echo "  - phi:2.7b - Very efficient, good for testing"
echo ""
echo "🎯 Performance Comparison:"
echo "  - gemma2:27b - Best quality, needs 16GB+ RAM"
echo "  - gemma2:9b - Excellent balance of quality/speed"
echo "  - gemma2:2b - Fastest, still high quality"
echo ""
echo "Quick start commands:"
echo "  ./ollama-setup.sh pull gemma2:9b     # Recommended"
echo "  ./ollama-setup.sh pull gemma2:27b    # Premium quality"
echo "  ./ollama-setup.sh pull gemma2:2b     # Fast testing"
