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

        print(
            "Gemini API key configured:",
            bool(api_key),
            flush=True,
        )

        self.client = genai.Client(
            api_key=api_key
        )

        # Use the model configured for the current
        # Gemini API/free-tier environment.
        self.model = "gemini-3.6-flash"

        self.max_retries = 2

        self.retry_delays = [
            2,
            5,
        ]

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
                "Gemini cache read failed:",
                repr(exc),
                flush=True,
            )

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

            print(
                "Gemini cache write failed:",
                repr(exc),
                flush=True,
            )

    # ==================================================
    # ERROR HELPERS
    # ==================================================

    @staticmethod
    def _is_quota_exhausted(
        error_text: str,
    ) -> bool:

        indicators = (
            "generate_requests_per_day",
            "generaterequestsperday",
            "free_tier_requests",
            "daily quota",
            "quota exceeded",
            "quotaexceeded",
            "exceeded your current quota",
            "resource exhausted",
        )

        return any(
            indicator in error_text
            for indicator in indicators
        )

    @staticmethod
    def _is_retryable(
        error_text: str,
    ) -> bool:

        indicators = (
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
            for indicator in indicators
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
    # SCHEMA
    # ==================================================

    @staticmethod
    def _flatten_schema(
        schema: dict,
    ) -> dict:
        """
        Convert Pydantic JSON Schema into a simpler schema
        suitable for Gemini structured output.
        """

        schema = dict(schema)

        defs = schema.pop(
            "$defs",
            {},
        )

        def resolve(node):

            if not isinstance(
                node,
                dict,
            ):
                return node

            node.pop(
                "title",
                None,
            )

            node.pop(
                "$schema",
                None,
            )

            node.pop(
                "default",
                None,
            )

            ref = node.pop(
                "$ref",
                None,
            )

            if ref:

                name = (
                    ref.split("/")[-1]
                )

                if name in defs:

                    replacement = (
                        resolve(
                            dict(
                                defs[name]
                            )
                        )
                    )

                    node.update(
                        replacement
                    )

            for key, value in list(
                node.items()
            ):

                if isinstance(
                    value,
                    dict,
                ):

                    node[key] = resolve(
                        value
                    )

                elif isinstance(
                    value,
                    list,
                ):

                    node[key] = [
                        resolve(item)
                        if isinstance(
                            item,
                            dict,
                        )
                        else item
                        for item in value
                    ]

            return node

        return resolve(
            schema
        )

    # ==================================================
    # GENERATE STRUCTURED
    # ==================================================

    def generate_structured(
        self,
        prompt: str,
        response_schema: type[BaseModel],
    ) -> BaseModel:

        print(
            "Gemini structured generation START",
            flush=True,
        )

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
                "Gemini cache HIT "
                f"[{response_schema.__name__}]",
                flush=True,
            )

            return cached

        print(
            "Gemini cache MISS "
            f"[{response_schema.__name__}]",
            flush=True,
        )

        schema = (
            self._flatten_schema(
                response_schema.model_json_schema()
            )
        )

        print(
            "Gemini schema prepared",
            flush=True,
        )

        last_exception = None

        for attempt in range(
            self.max_retries
        ):

            try:

                print(
                    f"Gemini API call START "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries})",
                    flush=True,
                )

                response = (
                    self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=(
                            types.GenerateContentConfig(
                                response_mime_type=(
                                    "application/json"
                                ),
                                response_schema=schema,
                            )
                        ),
                    )
                )

                print(
                    "Gemini API call DONE",
                    flush=True,
                )

                # --------------------------------------------------
                # Parse structured result
                # --------------------------------------------------

                if (
                    getattr(
                        response,
                        "parsed",
                        None,
                    )
                    is not None
                ):

                    result = (
                        response_schema
                        .model_validate(
                            response.parsed
                        )
                    )

                else:

                    text = (
                        getattr(
                            response,
                            "text",
                            None,
                        )
                    )

                    if not text:

                        raise ValueError(
                            "Gemini returned an empty response."
                        )

                    result = (
                        response_schema
                        .model_validate_json(
                            text
                        )
                    )

                print(
                    "Gemini response parsed",
                    flush=True,
                )

                self._save_cache(
                    cache_key,
                    result,
                )

                print(
                    "Gemini structured generation DONE",
                    flush=True,
                )

                return result

            except Exception as exc:

                last_exception = exc

                error_text = str(
                    exc
                )

                normalized_error = (
                    error_text.lower()
                )

                print(
                    "Gemini request ERROR:",
                    repr(exc),
                    flush=True,
                )

                # ==================================================
                # QUOTA
                # ==================================================

                if self._is_quota_exhausted(
                    normalized_error
                ):

                    retry_after = (
                        self._extract_retry_seconds(
                            error_text
                        )
                    )

                    raise GeminiQuotaError(
                        (
                            "Gemini API quota exhausted. "
                            "Check the Gemini project/model quota "
                            "associated with GEMINI_API_KEY."
                        ),
                        retry_after=retry_after,
                    ) from exc

                # ==================================================
                # RETRY TRANSIENT ERRORS
                # ==================================================

                retryable = (
                    self._is_retryable(
                        normalized_error
                    )
                )

                if (
                    not retryable
                    or attempt
                    >= self.max_retries - 1
                ):

                    raise

                delay = (
                    self.retry_delays[
                        attempt
                    ]
                )

                print(
                    f"Gemini transient error. "
                    f"Retrying in {delay}s...",
                    flush=True,
                )

                time.sleep(
                    delay
                )

        if last_exception:

            raise last_exception

        raise RuntimeError(
            "Gemini generation failed."
        )