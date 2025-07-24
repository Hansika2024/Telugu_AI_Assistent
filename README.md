## Telugu AI Assistant

<img width="1353" height="629" alt="Screenshot 2025-07-24 211549" src="https://github.com/user-attachments/assets/72344263-5dc9-422d-ab00-5e7159b65a44" />

# Features

- Voice and text input (Telugu + English)
- Uses Phi-3 Mini (LLM) for smart response generation
- Converts speech to text using Whisper
- Converts responses to speech using Coqui TTS (Telugu-supported)
- Automatically translates between Telugu ↔ English
- Runs fully offline — no OpenAI or third-party APIs
- Faster performance on systems with GPU (CUDA enabled)

# Requirements

Backend (Python)
- Python 3.8+
- torch
- transformers
- openai-whisper
- TTS
- librosa
- soundfile
- googletrans==4.0.0-rc1
- flask

Install with:

# bash
pip install -r requirements.txt
