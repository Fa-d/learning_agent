import os
from llama_cpp import Llama
from .llm.base_provider import LLMProvider
from .llm.llama_provider import LlamaProvider
from .llm.openai_provider import OpenAIProvider
from .llm.gemini_provider import GeminiProvider
from .llm.anthropic_provider import AnthropicProvider
from .llm.deepseek_provider import DeepSeekProvider

_llama_model = None

def get_llm_provider(provider_name: str) -> LLMProvider:
    global _llama_model
    provider_name = provider_name.lower()

    if provider_name == "llama":
        home_dir = os.path.expanduser("~")
        MODEL_PATH = os.path.join(home_dir, ".lmstudio", "models", "unsloth", "gemma-3n-E4B-it-GGUF", "gemma-3n-E4B-it-UD-Q6_K_XL.gguf")
        if _llama_model is None:
            _llama_model = Llama(model_path=MODEL_PATH, n_ctx=4096, n_gpu_layers=-1)
        return LlamaProvider(model=_llama_model)
    elif provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: raise ValueError("OPENAI_API_KEY environment variable not set.")
        return OpenAIProvider(api_key=api_key)
    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: raise ValueError("GEMINI_API_KEY environment variable not set.")
        return GeminiProvider(api_key=api_key)
    elif provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key: raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        return AnthropicProvider(api_key=api_key)
    elif provider_name == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key: raise ValueError("DEEPSEEK_API_KEY environment variable not set.")
        return DeepSeekProvider(api_key=api_key)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
