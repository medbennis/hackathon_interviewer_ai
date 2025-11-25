import requests
import os


GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MODEL = "whisper-large-v3"


def transcribe_audio(audio_bytes: bytes, file_ext="wav") -> str:
    """
    Transcrit un audio (en bytes) via l'API Groq Whisper.
    Compatible pour :
      - app1 (upload fichier audio)
      - app2 (enregistrement micro via WebRTC)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY non définie.")

    files = {
        "file": ("audio." + file_ext, audio_bytes),
    }
    data = {
        "model": MODEL,
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(
        GROQ_WHISPER_URL,
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Erreur Whisper Groq : {response.status_code}\n{response.text}"
        )

    result = response.json()
    return result.get("text", "").strip()
