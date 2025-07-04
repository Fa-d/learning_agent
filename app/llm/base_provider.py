from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        pass
