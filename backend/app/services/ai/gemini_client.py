import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel


load_dotenv()


class GeminiQuotaError(Exception):
    """Raised when Gemini API quota has been exhausted."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.retry_after = retry_after


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

        # Only retry genuinely transient failures.
        self.max_retries = 3

        self.retry_delays = [
            2,
            5,
            10,
        ]

        # ==================================================
        # LOCAL CACHE
        # ==================================================

        self.cache_dir = (
            Path(__file__).resolve().parents[3]
            / ".gemini_cache"
        )

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # CACHE
    # ==================================================

    def _cache_key(
        self,
        prompt: str,
        response_schema: type[BaseModel],
    ) -> str:

        schema_name = (
            response_schema.__name__
        )

        schema_json = json.dumps(
            response_schema.model_json_schema(),
            sort_keys=True,
            default=str,
        )

        cache_input = (
            self.model
            + "\n"
            + schema_name
            + "\n"
            + schema_json
            + "\n"
            + prompt
        )

        return hashlib.sha256(
            cache_input.encode(
                "utf-8"
            )
        ).hexdigest()

    def _cache_path(
        self,
        key: str,
    ) -> Path:

        return (
            self.cache_dir
            / f"{key}.json"
        )

    def _load_cache(
        self,
        key: str,
        response_schema: type[BaseModel],
    ) -> BaseModel | None:

        path = self._cache_path(
            key
        )

        if not path.exists():
            return None

        try:

            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            return (
                response_schema.model_validate(
                    data
                )
            )

        except Exception as exc:

            print(
                f"\nGemini cache read failed: "
                f"{exc}"
            )

            # Broken cache entries should not
            # prevent a fresh API request.
            try:
                path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass

            return None

    def _save_cache(
        self,
        key: str,
        result: BaseModel,
    ) -> None:

        path = self._cache_path(
            key
        )

        try:

            path.write_text(
                json.dumps(
                    result.model_dump(),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        except Exception as exc:

            # Cache failure should NEVER
            # break CareerOS.
            print(
                f"\nGemini cache write failed: "
                f"{exc}"
            )

    # ==================================================
    # ERROR HELPERS
    # ==================================================

    @staticmethod
    def _is_quota_exhausted(
        error_text: str,
    ) -> bool:

        quota_indicators = (
            "generate_requests_per_day",
            "generaterequestsperday",
            "free_tier_requests",
            "daily quota",
            "quota exceeded",
            "quotaexceeded",
            "exceeded your current quota",
        )

        return any(
            indicator in error_text
            for indicator in quota_indicators
        )

    @staticmethod
    def _is_retryable(
        error_text: str,
    ) -> bool:

        retryable_indicators = (
            "503",
            "service unavailable",
            "temporarily unavailable",
            "high demand",
            "timeout",
            "deadline exceeded",
            "connection reset",
            "connection error",
        )

        return any(
            indicator in error_text
            for indicator in retryable_indicators
        )

    @staticmethod
    def _extract_retry_seconds(
        error_text: str,
    ) -> int | None:

        import re

        match = re.search(
            r"retry(?: in|after).*?(\d+(?:\.\d+)?)\s*s",
            error_text,
            re.IGNORECASE,
        )

        if not match:
            return None

        try:

            return int(
                float(
                    match.group(1)
                )
            )

        except ValueError:

            return None

    # ==================================================
    # STRUCTURED GENERATION
    # ==================================================


    @staticmethod
    def _flatten_schema(schema: dict) -> dict:
        """
        Convert Pydantic's JSON Schema into a Gemini-compatible
        structured-output schema by resolving $refs/$defs and
        removing unsupported JSON Schema metadata.
        """

        schema = dict(schema)
        defs = schema.pop("$defs", {})

        def resolve(node):
            if not isinstance(node, dict):
                return node

            # Remove fields Gemini does not support.
            node.pop("title", None)
            node.pop("$schema", None)
            node.pop("default", None)

            # Resolve Pydantic $ref definitions inline.
            ref = node.pop("$ref", None)

            if ref:
                name = ref.split("/")[-1]

                if name in defs:
                    replacement = resolve(dict(defs[name]))
                    node.update(replacement)

            # Recursively process nested dictionaries/lists.
            for key, value in list(node.items()):
                if isinstance(value, dict):
                    node[key] = resolve(value)

                elif isinstance(value, list):
                    node[key] = [
                        resolve(item)
                        if isinstance(item, dict)
                        else item
                        for item in value
                    ]

            return node

        return resolve(schema)
    
    def generate_structured(
        self,
        prompt: str,
        response_schema: type[BaseModel],
    ) -> BaseModel:

        # ==================================================
        # CACHE LOOKUP
        # ==================================================

        cache_key = self._cache_key(
            prompt,
            response_schema,
        )

        cached = self._load_cache(
            cache_key,
            response_schema,
        )

        if cached is not None:

            print(
                "\nGemini cache hit "
                f"[{response_schema.__name__}]"
            )

            return cached

        print(
            "\nGemini cache miss "
            f"[{response_schema.__name__}]"
        )

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        last_exception = None

        for attempt in range(
            self.max_retries
        ):

            try:

                schema = self._flatten_schema(
    response_schema.model_json_schema()
)

                response = (
                    self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=schema,
                        ),
                    )
                )

                if response.parsed is not None:

                    result = (
                        response.parsed
                    )

                else:

                    result = (
                        response_schema
                        .model_validate_json(
                            response.text
                        )
                    )

                # ==================================================
                # SAVE SUCCESSFUL RESULT
                # ==================================================

                self._save_cache(
                    cache_key,
                    result,
                )

                return result

            except Exception as exc:

                last_exception = exc

                error_text = str(
                    exc
                ).lower()

                # ==================================================
                # QUOTA EXHAUSTION
                #
                # NEVER retry daily/project quota exhaustion.
                # ==================================================

                if self._is_quota_exhausted(
                    error_text
                ):

                    retry_after = (
                        self._extract_retry_seconds(
                            str(exc)
                        )
                    )

                    raise GeminiQuotaError(
                        (
                            "Gemini API quota has been "
                            "exhausted for the current "
                            "project/model quota period."
                        ),
                        retry_after=retry_after,
                    ) from exc

                # ==================================================
                # TRANSIENT FAILURE
                # ==================================================

                retryable = (
                    self._is_retryable(
                        error_text
                    )
                    or (
                        "429" in error_text
                        and "quota" not in error_text
                    )
                    or (
                        "rate limit" in error_text
                        and "quota" not in error_text
                    )
                    or (
                        "resource exhausted"
                        in error_text
                        and "quota" not in error_text
                    )
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
                    f"\nGemini transient failure "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries}). "
                    f"Retrying in {delay}s..."
                )

                time.sleep(
                    delay
                )

        raise last_exception