import google.generativeai as genai
from .base_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_completion(self, prompt: str, max_tokens: int, temperature: float, top_p: float, stop: list[str]) -> dict:
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop
            )
        )
        return {'choices': [{'text': response.text}]}
