import os
import json
import requests
from typing import Any, Dict, List

# URL de l'API Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Modèle par défaut (modifie selon ton besoin)
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def _get_api_key() -> str:
    """
    Vérifie que la variable d'environnement GROQ_API_KEY est définie.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "⚠️ GROQ_API_KEY n'est pas définie dans les variables d'environnement.\n"
            "Définis-la avant de lancer le projet.\n"
            "Exemple Windows :  setx GROQ_API_KEY \"ta_cle_ici\"\n"
            "Exemple Linux/Mac : export GROQ_API_KEY=\"ta_cle_ici\""
        )
    return api_key


def _call_groq(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> str:
    """
    Envoie une requête HTTP à Groq et retourne la réponse textuelle.
    """
    headers = {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Erreur API Groq {response.status_code} : {response.text}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_text(
    prompt: str,
    system: str = "Tu es un assistant utile, clair et concis.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 800,
) -> str:
    """
    Génère du texte libre via Groq (LLama, Mixtral...).
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    return _call_groq(messages, model, temperature, max_tokens)


def generate_json(
    prompt: str,
    system: str = (
        "Tu es un assistant qui renvoie STRICTEMENT du JSON valide, "
        "sans texte autour, sans markdown."
    ),
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 800,
) -> Dict[str, Any]:
    """
    Demande explicitement au modèle Groq de renvoyer du JSON, puis parse la sortie.
    """

    raw = generate_text(
        prompt=prompt,
        system=system,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    ).strip()

    cleaned = raw

    # Retire les "```json" ou "```"
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(
            f"❌ JSON invalide retourné par Groq.\n"
            f"Réponse brute :\n{raw}\nErreur : {e}"
        )


def chat(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 800,
) -> str:
    """
    Interface générique : conversation multi-tours.
    """
    return _call_groq(messages, model, temperature, max_tokens)
