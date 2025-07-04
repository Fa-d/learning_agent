import anthropic
from .base_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        response = self.client.messages.create(
            model="claude-3-opus-20240229",  # Or another model
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_sequences=stop,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return {'choices': [{'text': response.content[0].text}]}
