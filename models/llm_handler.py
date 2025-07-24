import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

class PhiHandler:
    def __init__(self):
        self.model_name = "microsoft/Phi-3-mini-4k-instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.token = os.environ.get("HF_TOKEN") 
        self.tokenizer = None
        self.model = None
        self._model_loaded = False
        self.load_model_if_needed()

    def load_model_if_needed(self):
        if self._model_loaded:
            return

        try:
            print("🔄 Loading Phi-3 Mini model...")

            cache_dir = os.path.join(os.getcwd(), "hf_cache")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=cache_dir,
                token=self.token
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                cache_dir=cache_dir,
                token=self.token
            )

            self._model_loaded = True
            print(f"✅ Phi-3 Mini loaded successfully on {self.device}")

        except Exception as e:
            print(f"❌ Error loading model: {e}")

    def generate_response(self, user_input, max_length=512):
        try:
            self.load_model_if_needed()

            prompt = f"""<|system|>
You are a helpful AI assistant. Provide clear, accurate, and helpful responses.
<|end|>
<|user|>
{user_input}
<|end|>
<|assistant|>
"""

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    use_cache=False
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            assistant_response = response.split("<|assistant|>")[-1].strip()
            return assistant_response

        except Exception as e:
            return f"❌ Error generating response: {str(e)}"
