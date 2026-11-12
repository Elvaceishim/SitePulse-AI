from app.config import get_settings

settings = get_settings()

print("Application:", settings.app_name)
print("OpenRouter model:", settings.openrouter_model)
print(
    "API key loaded:",
    bool(settings.openrouter_api_key)
)