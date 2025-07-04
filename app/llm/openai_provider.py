from openai import OpenAI
from .base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        response = self.client.completions.create(
            model="text-davinci-003",  # Or another model
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
        return {'choices': [{'text': response.choices[0].text}]}
