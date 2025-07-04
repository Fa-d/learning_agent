import openai
from .base_provider import LLMProvider

class DeepSeekProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        response = self.client.completions.create(
            model="deepseek-chat",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
        return {'choices': [{'text': response.choices[0].text}]}
