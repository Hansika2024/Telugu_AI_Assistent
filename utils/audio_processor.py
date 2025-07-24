import numpy as np
import librosa
import io
import wave
import struct
from scipy import signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr
        
    def process_audio_data(self, audio_data, original_sr=44100):
        """Process raw audio data for speech recognition"""
        try:
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_array = audio_array.astype(np.float32) / 32768.0
            else:
                audio_array = audio_data
            if original_sr != self.target_sr:
                audio_array = librosa.resample(
                    audio_array, 
                    orig_sr=original_sr, 
                    target_sr=self.target_sr
                )
            audio_array = self.enhance_audio(audio_array)
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return np.array([])
    
    def enhance_audio(self, audio_array):
        """Apply audio enhancement techniques"""
        try:
            audio_array = audio_array - np.mean(audio_array)
        
            sos = signal.butter(5, 80, btype='high', fs=self.target_sr, output='sos')
            audio_array = signal.sosfilt(sos, audio_array)

            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array / np.max(np.abs(audio_array)) * 0.8
            audio_array = self.apply_noise_gate(audio_array, threshold=0.01)
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Audio enhancement error: {e}")
            return audio_array
    
    def apply_noise_gate(self, audio_array, threshold=0.01):
        """Apply noise gate to reduce background noise"""
        try:
            window_size = int(0.025 * self.target_sr) 
            hop_length = int(0.010 * self.target_sr) 
            
            gates = []
            for i in range(0, len(audio_array) - window_size, hop_length):
                window = audio_array[i:i + window_size]
                rms = np.sqrt(np.mean(window**2))
                gates.append(1.0 if rms > threshold else 0.3)
            gate_array = np.interp(
                np.arange(len(audio_array)),
                np.arange(0, len(audio_array), hop_length)[:len(gates)],
                gates
            )
            
            return audio_array * gate_array
            
        except Exception as e:
            logger.error(f"Noise gate error: {e}")
            return audio_array
    
    def detect_speech_segments(self, audio_array, min_duration=0.5):
        """Detect speech segments in audio"""
        try:
            window_size = int(0.025 * self.target_sr)
            hop_length = int(0.010 * self.target_sr)
            
            energies = []
            for i in range(0, len(audio_array) - window_size, hop_length):
                window = audio_array[i:i + window_size]
                energy = np.sum(window**2)
                energies.append(energy)
            threshold = np.mean(energies) * 2
            speech_frames = np.array(energies) > threshold
            segments = []
            in_speech = False
            start_time = 0
            
            for i, is_speech in enumerate(speech_frames):
                time = i * hop_length / self.target_sr
                
                if is_speech and not in_speech:
                    start_time = time
                    in_speech = True
                elif not is_speech and in_speech:
                    duration = time - start_time
                    if duration >= min_duration:
                        segments.append((start_time, time))
                    in_speech = False
            
            return segments
            
        except Exception as e:
            logger.error(f"Speech detection error: {e}")
            return []
    
    def trim_silence(self, audio_array, threshold=0.01):
        """Trim silence from beginning and end of audio"""
        try:
            non_silent = np.abs(audio_array) > threshold
            
            if not np.any(non_silent):
                return audio_array
            
            first_sound = np.argmax(non_silent)
            last_sound = len(audio_array) - np.argmax(non_silent[::-1])
            
            return audio_array[first_sound:last_sound]
            
        except Exception as e:
            logger.error(f"Silence trimming error: {e}")
            return audio_array
