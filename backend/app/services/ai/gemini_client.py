import hashlib
import json
import os
import time
from pathlib import Path

from app.utils.env_loader import load_project_env
from google import genai
from google.genai import types
from pydantic import BaseModel


load_project_env()


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
            print(
                "[GeminiClient] WARNING: GEMINI_API_KEY environment variable is not set. "
                "AI evaluations will use deterministic heuristics.",
                flush=True,
            )
            self.client = None
        else:
            print(
                "Gemini API key configured:",
                bool(api_key),
                flush=True,
            )
            self.client = genai.Client(
                api_key=api_key
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        self.fallback_models = list(
            dict.fromkeys(
                [
                    self.model,
                    "gemini-3.8-flash",
                    "gemini-3.6-flash",
                    "gemini-2.5-flash",
                ]
            )
        )

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

    def _text_cache_key(self, prompt: str) -> str:
        cache_input = self.model + "\ntext\n" + prompt
        return hashlib.sha256(cache_input.encode("utf-8")).hexdigest()

    def _load_text_cache(self, key: str) -> str | None:
        path = self.cache_dir / f"text_{key}.txt"
        if not path.exists():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return None

    def _save_text_cache(self, key: str, text: str) -> None:
        path = self.cache_dir / f"text_{key}.txt"
        try:
            path.write_text(text, encoding="utf-8")
        except Exception:
            pass

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
    # STRUCTURED SCHEMA
    # ==================================================

    @staticmethod
    def _flatten_schema(
        schema: dict,
    ) -> dict:

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

                    replacement = resolve(
                        dict(
                            defs[name]
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
    # PLAIN TEXT GENERATION
    # ==================================================

    def generate_text(
        self,
        prompt: str,
    ) -> str:

        print(
            "Gemini text generation START",
            flush=True,
        )

        if not self.client:
            raise GeminiQuotaError(
                "GEMINI_API_KEY environment variable is not configured."
            )

        cache_key = self._text_cache_key(prompt)
        cached = self._load_text_cache(cache_key)
        if cached is not None:
            print("Gemini text cache HIT", flush=True)
            return cached

        print("Gemini text cache MISS", flush=True)

        last_exception = None

        for model_candidate in self.fallback_models:
            for attempt in range(self.max_retries):
                try:
                    print(
                        f"Gemini text API call START ({model_candidate}, attempt {attempt + 1}/{self.max_retries})",
                        flush=True,
                    )

                    response = self.client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                    )

                    text = getattr(response, "text", None)
                    if not text:
                        raise ValueError("Gemini returned an empty text response.")

                    self.model = model_candidate
                    self._save_text_cache(cache_key, text)
                    print(f"Gemini text generation DONE with {model_candidate}", flush=True)
                    return text

                except Exception as exc:
                    last_exception = exc
                    error_text = str(exc)
                    normalized_error = error_text.lower()
                    print(f"Gemini text request ERROR ({model_candidate}): {exc!r}", flush=True)

                    if self._is_quota_exhausted(normalized_error):
                        retry_after = self._extract_retry_seconds(error_text)
                        raise GeminiQuotaError(
                            "Gemini API quota exhausted. Check your Gemini API key and project limits.",
                            retry_after=retry_after,
                        ) from exc

                    if "404" in normalized_error or "not_found" in normalized_error:
                        print(f"Model {model_candidate} not available, switching to next fallback.", flush=True)
                        break

                    if self._is_retryable(normalized_error) and attempt < self.max_retries - 1:
                        delay = self.retry_delays[attempt]
                        print(f"Gemini transient error. Retrying in {delay}s...", flush=True)
                        time.sleep(delay)
                    else:
                        break

        raise last_exception

    # ==================================================
    # STRUCTURED GENERATION
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

        if not self.client:
            raise GeminiQuotaError(
                "GEMINI_API_KEY environment variable is not configured."
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
                f"Gemini cache HIT [{response_schema.__name__}]",
                flush=True,
            )
            return cached

        print(
            f"Gemini cache MISS [{response_schema.__name__}]",
            flush=True,
        )

        schema = self._flatten_schema(
            response_schema.model_json_schema()
        )

        last_exception = None

        for model_candidate in self.fallback_models:
            for attempt in range(self.max_retries):
                try:
                    print(
                        f"Gemini API call START ({model_candidate}, attempt {attempt + 1}/{self.max_retries})",
                        flush=True,
                    )

                    response = self.client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=schema,
                        ),
                    )

                    if getattr(response, "parsed", None) is not None:
                        result = response_schema.model_validate(response.parsed)
                    else:
                        text = getattr(response, "text", None)
                        if not text:
                            raise ValueError("Gemini returned an empty response.")
                        result = response_schema.model_validate_json(text)

                    self.model = model_candidate
                    self._save_cache(cache_key, result)
                    print(f"Gemini structured generation DONE with {model_candidate}", flush=True)
                    return result

                except Exception as exc:
                    last_exception = exc
                    error_text = str(exc)
                    normalized_error = error_text.lower()
                    print(f"Gemini request ERROR ({model_candidate}): {exc!r}", flush=True)

                    if self._is_quota_exhausted(normalized_error):
                        retry_after = self._extract_retry_seconds(error_text)
                        raise GeminiQuotaError(
                            "Gemini API quota exhausted. Check your Gemini API key and project limits.",
                            retry_after=retry_after,
                        ) from exc

                    if "404" in normalized_error or "not_found" in normalized_error:
                        print(f"Model {model_candidate} not available, switching to next fallback.", flush=True)
                        break

                    if self._is_retryable(normalized_error) and attempt < self.max_retries - 1:
                        delay = self.retry_delays[attempt]
                        print(f"Gemini transient error. Retrying in {delay}s...", flush=True)
                        time.sleep(delay)
                    else:
                        break

        raise last_exception