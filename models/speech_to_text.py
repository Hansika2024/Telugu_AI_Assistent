import whisper
import io
import numpy as np
import librosa

class WhisperSTT:
    def __init__(self):
        self.model = whisper.load_model("base")  # or "small" for better accuracy
        
    def transcribe(self, audio_data, language='te'):
        """Transcribe audio to text with Telugu support"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            if len(audio_array) > 0:
                audio_array = librosa.resample(audio_array, orig_sr=44100, target_sr=16000)
            result = self.model.transcribe(
                audio_array, 
                language=language,
                task="transcribe"
            )
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"STT Error: {e}")
            return "Speech recognition failed"