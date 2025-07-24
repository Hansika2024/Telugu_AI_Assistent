## Telugu AI Voice Assistant

# Features

- Voice and text input (Telugu + English)
- Uses Phi-3 Mini (LLM) for smart response generation
- Converts speech to text using Whisper
- Converts responses to speech using Coqui TTS (Telugu-supported)
- Automatically translates between Telugu ↔ English
- Runs fully offline — no OpenAI or third-party APIs
- Faster performance on systems with GPU (CUDA enabled)

# Project Structure
telugu-ai-assistant/
├── backend/
│ ├── app.py # Flask main application
│ ├── config.py
│ ├── requirements.txt
│ ├── models/
│ │ ├── llm_handler.py # Phi-3 Mini integration
│ │ ├── speech_to_text.py # Whisper integration
│ │ └── text_to_speech.py # Coqui TTS integration
│ └── utils/
│ ├── translator.py # Telugu translation
│ └── audio_processor.py # Audio handling
├── frontend/
│ ├── public/
│ │ └── index.html
│ ├── src/
│ │ ├── components/
│ │ │ ├── ChatInterface.js
│ │ │ ├── VoiceRecorder.js
│ │ │ └── AudioPlayer.js
│ │ ├── hooks/
│ │ │ └── useSocket.js
│ │ ├── App.js
│ │ └── index.js
│ └── package.json

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
