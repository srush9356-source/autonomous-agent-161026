from google import genai

from app.llm.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_PROVIDER,
    validate_config,
)


class LLMClient:
    """Gateway for interacting with the configured LLM provider."""

    def __init__(self):
        validate_config()

        if LLM_PROVIDER == "gemini":
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = GEMINI_MODEL
        else:
            raise ValueError(
                f"Unsupported LLM provider: {LLM_PROVIDER}"
            )

    def generate(self, prompt: str) -> str:
        """Generate a response from the configured LLM."""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text