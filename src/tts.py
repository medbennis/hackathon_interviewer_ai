import io
from gtts import gTTS


def question_to_audio(text: str) -> bytes:
    """
    Convertit un texte en audio MP3 (TTS) et renvoie les bytes.
    Compatible pour app1 (simple) et app2 (avancé).
    """
    audio_buffer = io.BytesIO()
    tts = gTTS(text=text, lang="fr")
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()
