import React, { useState, useRef, useCallback } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onVoiceMessage, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const animationFrameRef = useRef(null);
  const setupAudioAnalysis = useCallback((stream) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      analyser.smoothingTimeConstant = 0.8;
      analyser.fftSize = 1024;
      
      microphone.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      const updateAudioLevel = () => {
        if (analyserRef.current && isRecording) {
          const bufferLength = analyserRef.current.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
          setAudioLevel(average / 255);
          
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
      
    } catch (error) {
      console.error('Error setting up audio analysis:', error);
    }
  }, [isRecording]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 44100,
          channelCount: 1,
          volume: 1.0,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      streamRef.current = stream;
      setupAudioAnalysis(stream);

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 128000
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Convert to WAV format for better compatibility
        const reader = new FileReader();
        reader.onload = () => {
          onVoiceMessage(audioBlob);
        };
        reader.readAsArrayBuffer(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  }, [onVoiceMessage, setupAudioAnalysis]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setAudioLevel(0);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  }, [isRecording]);

  const toggleRecording = useCallback(() => {
    if (disabled) return;
    
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, disabled, startRecording, stopRecording]);

  return (
    <div className="voice-recorder">
      <button
        className={`record-button ${isRecording ? 'recording' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={toggleRecording}
        disabled={disabled}
        title={isRecording ? "Stop recording" : "Start voice recording"}
      >
        <div className="record-icon">
          {isRecording ? '⏹️' : '🎤'}
        </div>
        
        {isRecording && (
          <div className="audio-visualizer">
            <div 
              className="audio-level"
              style={{ height: `${audioLevel * 100}%` }}
            />
          </div>
        )}
      </button>
      
      {isRecording && (
        <div className="recording-status">
          <div className="pulse-dot" />
          <span>Recording...</span>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
