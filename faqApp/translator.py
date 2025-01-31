from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

class CustomTranslator:
    def __init__(self, model_name="facebook/m2m100_418M"):
        """
        Initialize the translation model.
        :param model_name: Hugging Face model name (default: facebook/m2m100_418M)
        """
        self.tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        self.model = M2M100ForConditionalGeneration.from_pretrained(model_name)

        # Language Mapping
        self.lang_codes = {
            "english": "en",
            "hindi": "hi",
            "marathi": "mr",
            "gujarati": "gu"
        }

    def translate(self, text, src="english", dest="hindi"):
        """
        Translate text from source to destination language.
        :param text: Input text to be translated
        :param src: Source language (default: English)
        :param dest: Destination language (default: Hindi)
        :return: Translated text
        """
        src_code = self.lang_codes.get(src.lower(), "en")
        dest_code = self.lang_codes.get(dest.lower(), "hi")

        # Tokenize & Translate
        self.tokenizer.src_lang = src_code
        encoded_text = self.tokenizer(text, return_tensors="pt")

        generated_tokens = self.model.generate(**encoded_text, forced_bos_token_id=self.tokenizer.get_lang_id(dest_code))
        translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        return translated_text

# ✅ Example Usage
if __name__ == "__main__":
    translator = CustomTranslator()
    
    text = "Hello, how are you?"
    translated = translator.translate(text, src="english", dest="hindi")
    
    print(f"Original: {text}")
    print(f"Translated: {translated}")
