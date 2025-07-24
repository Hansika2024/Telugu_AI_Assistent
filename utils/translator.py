from googletrans import Translator
import re

class TeluguTranslator:
    def __init__(self):
        self.translator = Translator()
        
    def is_telugu(self, text):
        """Check if text contains Telugu characters"""
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        return bool(telugu_pattern.search(text))
        
    def translate_to_english(self, telugu_text):
        """Translate Telugu to English"""
        try:
            result = self.translator.translate(telugu_text, src='te', dest='en')
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return telugu_text
            
    def translate_to_telugu(self, english_text):
        """Translate English to Telugu"""
        try:
            result = self.translator.translate(english_text, src='en', dest='te')
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return english_text