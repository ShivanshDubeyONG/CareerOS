import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel


load_dotenv()


class GeminiClient:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable "
                "is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

        self.max_retries = 4

        self.retry_delays = [
            2,
            5,
            10,
            20,
        ]

    def generate_structured(
        self,
        prompt: str,
        response_schema: type[BaseModel],
    ) -> BaseModel:

        last_exception = None

        for attempt in range(
            self.max_retries
        ):

            try:

                response = (
                    self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type=(
                                "application/json"
                            ),
                            response_schema=(
                                response_schema
                            ),
                        ),
                    )
                )

                if response.parsed is not None:
                    return response.parsed

                return (
                    response_schema
                    .model_validate_json(
                        response.text
                    )
                )

            except Exception as exc:

                last_exception = exc

                error_text = str(
                    exc
                ).lower()

                retryable = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "high demand" in error_text
                    or "429" in error_text
                    or "rate limit" in error_text
                    or "resource exhausted" in error_text
                    or "timeout" in error_text
                    or "deadline" in error_text
                )

                if (
                    not retryable
                    or attempt
                    == self.max_retries - 1
                ):

                    raise

                delay = (
                    self.retry_delays[
                        attempt
                    ]
                )

                print(
                    f"\nGemini request failed "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries}). "
                    f"Retrying in {delay}s..."
                )

                time.sleep(
                    delay
                )

        raise last_exception