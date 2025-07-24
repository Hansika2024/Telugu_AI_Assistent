import torch
from TTS.api import TTS
import io

class CoquiTTS:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False
        ).to(self.device)
        
    def synthesize(self, text, language="te"):
        """Convert text to speech in Telugu"""
        try:
            audio_data = self.tts.tts(
                text=text,
                language=language,
                split_sentences=True
            )
            audio_bytes = io.BytesIO()
            import soundfile as sf
            sf.write(audio_bytes, audio_data, 22050, format='WAV')
            audio_bytes.seek(0)
            
            return audio_bytes.read()
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return b''