import httpx
import pytest

from app.services.llm_client import (
    OpenRouterClient,
    OpenRouterError,
)


def test_client_builds_correct_request(monkeypatch):
    client = OpenRouterClient()

    def mock_post(url, **kwargs):
        assert url.endswith("/chat/completions")
        assert kwargs["headers"]["Authorization"].startswith("Bearer ")
        assert kwargs["json"]["model"] == client.settings.openrouter_model

        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Test briefing."
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    result = client.generate([
        {"role": "user", "content": "Generate a test briefing."}
    ])

    assert result == "Test briefing."


def test_empty_messages_are_rejected():
    client = OpenRouterClient()

    with pytest.raises(ValueError):
        client.generate([])


def test_http_errors_are_handled(monkeypatch):
    client = OpenRouterClient()

    def mock_post(url, **kwargs):
        return httpx.Response(
            429,
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(OpenRouterError, match="429"):
        client.generate([
            {"role": "user", "content": "Test"}
        ])


def test_malformed_response_is_rejected(monkeypatch):
    client = OpenRouterClient()

    def mock_post(url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"unexpected": "response"},
        )

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(OpenRouterError):
        client.generate([
            {"role": "user", "content": "Test"}
        ])