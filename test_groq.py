
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

key = config.get("XAI_API_KEY", "")
base_url = config.get("XAI_BASE_URL", "").rstrip("/")
model = config.get("XAI_MODEL", "")

print("API :", base_url)
print("Modèle :", model)
print("Clé présente :", bool(key))
print("Format de clé Groq :", key.startswith("gsk_"))

if not key or not base_url or not model:
    raise SystemExit("Configuration .env incomplète")

response = requests.post(
    f"{base_url}/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": model,
        "messages": [
            {"role": "user", "content": "Réponds simplement OK."}
        ],
        "max_tokens": 100
    },
    timeout=45
)

print("HTTP :", response.status_code)

if response.ok:
    print("Réponse :", response.json()["choices"][0]["message"]["content"])
else:
    try:
        error = response.json().get("error", {})
        print("Type :", error.get("type"))
        print("Code :", error.get("code"))
        print("Message :", error.get("message"))
    except ValueError:
        print("Réponse du serveur non JSON")
