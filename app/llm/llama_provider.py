from llama_cpp import Llama
from .base_provider import LLMProvider

class LlamaProvider(LLMProvider):
    def __init__(self, model: Llama):
        self.model = model

    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        return self.model.create_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
