
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

key = config["XAI_API_KEY"]
base_url = config["XAI_BASE_URL"].rstrip("/")
model = config["XAI_MODEL"]

response = requests.post(
    f"{base_url}/chat/completions",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "NutriSport RAG"
    },
    json={
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Réponds en français : à quoi servent les protéines ?"
            }
        ],
        "max_tokens": 500
    },
    timeout=120
)

print("HTTP :", response.status_code)

if response.ok:
    data = response.json()
    print("Modèle utilisé :", data.get("model"))
    print("Réponse :", data["choices"][0]["message"]["content"])
else:
    print("Erreur :", response.text[:500])
