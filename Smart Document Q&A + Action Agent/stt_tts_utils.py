import tempfile
import os
import streamlit as st
import requests

# For speech-to-text (STT) using OpenAI Whisper API (or any public STT API)
def speech_to_text(audio_bytes, api_key):
    url = "https://api.openai.com/v1/audio/transcriptions"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    files = {"file": open(tmp_path, "rb")}
    data = {"model": "whisper-1"}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, files=files, data=data, headers=headers)
    os.remove(tmp_path)
    if response.status_code == 200:
        return response.json()["text"]
    else:
        return "[Speech recognition failed]"

# For text-to-speech (TTS) using gTTS (Google Text-to-Speech)
def text_to_speech(text, lang="en"):
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        audio_bytes = tmp.read()
        tmp_path = tmp.name
    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()
    os.remove(tmp_path)
    return audio_bytes
