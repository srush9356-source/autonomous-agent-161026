import time

from google import genai
from groq import Groq
from pydantic import BaseModel

from app.llm.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    validate_config,
)


class LLMClient:
    """Provider-independent gateway for LLM interactions."""

    def __init__(self):
        validate_config()

        if LLM_PROVIDER == "gemini":
            self.provider = "gemini"
            self.client = genai.Client(
                api_key=GEMINI_API_KEY
            )
            self.model = GEMINI_MODEL

        elif LLM_PROVIDER == "groq":
            self.provider = "groq"
            self.client = Groq(
                api_key=GROQ_API_KEY
            )
            self.model = GROQ_MODEL

        else:
            raise ValueError(
                f"Unsupported LLM provider: {LLM_PROVIDER}"
            )

    def generate(self, prompt: str) -> str:
        """Generate a text response from the configured LLM."""

        if self.provider == "gemini":
            response = self._generate_with_retry(
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
            )

            return response.text

        response = self._generate_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        )

        return response.choices[0].message.content

    def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:
        """Generate and validate a structured response."""

        if self.provider == "gemini":
            response = self._generate_with_retry(
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": response_model,
                    },
                )
            )

            return response_model.model_validate_json(
                response.text
            )

        response = self._generate_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "schema": response_model.model_json_schema(),
                    },
                },
            )
        )

        return response_model.model_validate_json(
            response.choices[0].message.content
        )

    @staticmethod
    def _generate_with_retry(
        request,
        max_attempts: int = 3,
    ):
        """Retry temporary failures but fail fast on quota errors."""

        for attempt in range(max_attempts):
            try:
                return request()

            except Exception as exc:
                error_text = str(exc).lower()

                if (
                    "429" in error_text
                    or "resource_exhausted" in error_text
                    or "rate limit" in error_text
                    or "quota" in error_text
                ):
                    raise RuntimeError(
                        "LLM quota/rate limit exceeded. "
                        "Please wait for the provider quota to reset "
                        "or use another available provider."
                    ) from exc

                if attempt == max_attempts - 1:
                    raise exc

                wait_time = 2 ** attempt
                time.sleep(wait_time)