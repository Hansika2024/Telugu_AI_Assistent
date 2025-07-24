import React, { useState, useEffect, useRef } from 'react';
import VoiceRecorder from './VoiceRecorder';
import AudioPlayer from './AudioPlayer';
import useSocket from '../hooks/useSocket';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const socket = useSocket();

  useEffect(() => {
    if (socket) {
      socket.on('ai_response', (data) => {
        setMessages(prev => [...prev, {
          type: 'ai',
          text: data.text_response,
          audio: data.audio_response,
          timestamp: data.timestamp
        }]);
        setIsLoading(false);
      });

      socket.on('error', (error) => {
        console.error('Socket error:', error);
        setIsLoading(false);
      });
    }
  }, [socket]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = {
      type: 'user',
      text: inputText,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/text_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputText })
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        type: 'ai',
        text: data.response,
        timestamp: Date.now()
      }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setInputText('');
    }
  };

  const handleVoiceMessage = (audioBlob) => {
    const reader = new FileReader();
    reader.onload = () => {
      const audioData = reader.result.split(',')[1]; // Remove data:audio/wav;base64,
      
      setMessages(prev => [...prev, {
        type: 'user',
        text: 'Voice message',
        timestamp: Date.now()
      }]);
      
      setIsLoading(true);
      socket.emit('audio_message', { audio: audioData });
    };
    reader.readAsDataURL(audioBlob);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>🤖 Telugu AI Assistant</h2>
        <div className="status-indicator">
          {isLoading ? '🔄 Thinking...' : '✅ Ready'}
        </div>
      </div>

      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-content">
              <p>{message.text}</p>
              {message.audio && (
                <AudioPlayer audioData={message.audio} />
              )}
            </div>
            <div className="timestamp">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message ai">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <form onSubmit={handleTextSubmit} className="text-input-form">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type in Telugu or English..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !inputText.trim()}>
            Send
          </button>
        </form>
        
        <VoiceRecorder onVoiceMessage={handleVoiceMessage} />
      </div>
    </div>
  );
};

export default ChatInterface;