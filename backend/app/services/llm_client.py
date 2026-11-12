
import httpx

from app.config import get_settings


class OpenRouterError(Exception):
    """Raised when an OpenRouter request fails."""


class OpenRouterClient:

    def __init__(self):
        self.settings = get_settings()

        if not self.settings.openrouter_api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.endpoint = (
            f"{self.settings.openrouter_base_url.rstrip('/')}"
            "/chat/completions"
        )

        self.headers = {
            "Authorization": (
                f"Bearer {self.settings.openrouter_api_key}"
            ),
            "Content-Type": "application/json",
        }

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str:

        if not messages:
            raise ValueError("At least one message is required.")

        payload = {
            "model": self.settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = httpx.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.settings.request_timeout_seconds,
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise OpenRouterError(
                "OpenRouter request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise OpenRouterError(
                f"OpenRouter returned HTTP {exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise OpenRouterError(
                "Could not connect to OpenRouter."
            ) from exc

        try:
            result = response.json()
            content = result["choices"][0]["message"]["content"]

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(
                "OpenRouter returned an unexpected response format."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError(
                "OpenRouter returned an empty response."
            )

        return content.strip()
