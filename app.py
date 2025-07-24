from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
import io
import time
import logging
from models.llm_handler import PhiHandler
from models.speech_to_text import WhisperSTT
from models.text_to_speech import CoquiTTS
from utils.translator import TeluguTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

CORS(app, origins="*")

phi_model = None
whisper_stt = None
coqui_tts = None
translator = None

def initialize_models():
    global phi_model, whisper_stt, coqui_tts, translator
    
    try:
        logger.info("Initializing PhiHandler...")
        phi_model = PhiHandler()
        logger.info("✓ PhiHandler initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize PhiHandler: {e}")
        phi_model = None
    
    try:
        logger.info("Initializing WhisperSTT...")
        whisper_stt = WhisperSTT()
        logger.info("✓ WhisperSTT initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize WhisperSTT: {e}")
        whisper_stt = None
    
    try:
        logger.info("Initializing CoquiTTS...")
        coqui_tts = CoquiTTS()
        logger.info("✓ CoquiTTS initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize CoquiTTS: {e}")
        coqui_tts = None
    
    try:
        logger.info("Initializing TeluguTranslator...")
        translator = TeluguTranslator()
        logger.info("✓ TeluguTranslator initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize TeluguTranslator: {e}")
        translator = None
    
    if phi_model is None:
        logger.error("CRITICAL: PhiHandler failed to initialize - system not ready")
        return False
    
    logger.info(f"Model initialization complete. Ready models: {sum([m is not None for m in [phi_model, whisper_stt, coqui_tts, translator]])}/4")
    return True

models_ready = initialize_models()

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('audio_message')
def handle_audio_message(data):
    try:
        if not models_ready or phi_model is None:
            emit('error', {'message': 'System not ready - models not initialized'})
            return
            
        if whisper_stt is None:
            emit('error', {'message': 'Speech recognition not available'})
            return
            
        if coqui_tts is None:
            emit('error', {'message': 'Text-to-speech not available'})
            return
            
        if translator is None:
            emit('error', {'message': 'Translator not available'})
            return
        logger.info(f"Received audio message from client: {request.sid}")
        
        if not data or 'audio' not in data:
            emit('error', {'message': 'Invalid audio data received'})
            return
        
        try:
            audio_data = base64.b64decode(data['audio'])
        except Exception as e:
            emit('error', {'message': f'Failed to decode audio data: {str(e)}'})
            return
        
        try:
            telugu_text = whisper_stt.transcribe(audio_data, language='te')
            if not telugu_text or telugu_text.strip() == '':
                emit('error', {'message': 'Could not transcribe audio'})
                return
        except Exception as e:
            emit('error', {'message': f'Speech recognition failed: {str(e)}'})
            return
        
        try:
            english_text = translator.translate_to_english(telugu_text)
        except Exception as e:
            emit('error', {'message': f'Translation to English failed: {str(e)}'})
            return
        
        try:
            llm_response = phi_model.generate_response(english_text)
        except Exception as e:
            emit('error', {'message': f'LLM response generation failed: {str(e)}'})
            return
        
        try:
            telugu_response = translator.translate_to_telugu(llm_response)
        except Exception as e:
            emit('error', {'message': f'Translation to Telugu failed: {str(e)}'})
            return
        
        try:
            audio_response = coqui_tts.synthesize(telugu_response)
            audio_base64 = base64.b64encode(audio_response).decode('utf-8')
        except Exception as e:
            emit('error', {'message': f'Speech synthesis failed: {str(e)}'})
            return
        
        emit('ai_response', {
            'text_input': telugu_text,
            'text_response': telugu_response,
            'audio_response': audio_base64,
            'timestamp': time.time()
        })
        
        logger.info(f"Successfully processed audio message for client: {request.sid}")
        
    except Exception as e:
        logger.error(f"Unexpected error in handle_audio_message: {e}")
        emit('error', {'message': f'Server error: {str(e)}'})

@app.route('/text_chat', methods=['POST'])
def text_chat():
    try:
        if not models_ready or phi_model is None:
            return jsonify({'error': 'System not ready - models not initialized'}), 503
            
        if translator is None:
            return jsonify({'error': 'Translator not available'}), 503
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Received text chat message: {user_message[:50]}...")
        
        try:
            if translator.is_telugu(user_message):
                english_message = translator.translate_to_english(user_message)
            else:
                english_message = user_message
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return jsonify({'error': f'Translation failed: {str(e)}'}), 500
        
        try:
            llm_response = phi_model.generate_response(english_message)
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return jsonify({'error': f'Response generation failed: {str(e)}'}), 500
        
        try:
            telugu_response = translator.translate_to_telugu(llm_response)
        except Exception as e:
            logger.error(f"Telugu translation error: {e}")
            return jsonify({'error': f'Telugu translation failed: {str(e)}'}), 500
        
        response_data = {
            'response': telugu_response,
            'original_input': user_message,
            'status': 'success',
            'timestamp': time.time()
        }
        
        logger.info("Text chat processed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in text_chat: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        models_status = {
            'phi_model': phi_model is not None,
            'whisper_stt': whisper_stt is not None,
            'coqui_tts': coqui_tts is not None,
            'translator': translator is not None
        }
        
        system_ready = models_ready and phi_model is not None
        
        return jsonify({
            'backend': True,
            'models': all(models_status.values()),
            'audio': whisper_stt is not None and coqui_tts is not None,
            'system_ready': system_ready,
            'model_details': models_status,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'backend': True,
            'models': False,
            'audio': False,
            'system_ready': False,
            'error': str(e)
        }), 500

@app.route('/debug', methods=['GET'])
def debug_models():
    """Debug endpoint to check individual model status"""
    debug_info = {
        'python_version': f"{__import__('sys').version}",
        'models_ready': models_ready,
        'model_status': {
            'phi_model': {
                'initialized': phi_model is not None,
                'type': str(type(phi_model)) if phi_model else None
            },
            'whisper_stt': {
                'initialized': whisper_stt is not None,
                'type': str(type(whisper_stt)) if whisper_stt else None
            },
            'coqui_tts': {
                'initialized': coqui_tts is not None,
                'type': str(type(coqui_tts)) if coqui_tts else None
            },
            'translator': {
                'initialized': translator is not None,
                'type': str(type(translator)) if translator else None
            }
        }
    }
    return jsonify(debug_info)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask-SocketIO server...")
        logger.info(f"Server will run on http://0.0.0.0:5000")
        
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            use_reloader=False,
            log_output=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise