from app.services.llm_client import OpenRouterClient, OpenRouterError

client = OpenRouterClient()

try:
    response = client.generate(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant helping workplace safety "
                    "supervisors understand operational risk."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Explain in two sentences why a construction site "
                    "with a heat risk score of 92/100 needs urgent review."
                ),
            },
        ],
        temperature=0.2,
        max_tokens=120,
    )

    print("\nOPENROUTER RESPONSE")
    print("=" * 50)
    print(response)

except OpenRouterError as error:
    print(f"OpenRouter request failed: {error}")