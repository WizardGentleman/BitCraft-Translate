from deep_translator import GoogleTranslator

class ChatTranslator:
    def __init__(self, target_lang='pt'):
        self.target_lang = target_lang
        self.to_target = GoogleTranslator(source='auto', target=target_lang)
        self.to_en = GoogleTranslator(source='auto', target='en')

    def set_target_lang(self, lang_code):
        self.target_lang = lang_code
        self.to_target = GoogleTranslator(source='auto', target=lang_code)

    def translate_to_target(self, text):
        if not text or not isinstance(text, str):
            return text
        try:
            return self.to_target.translate(text)
        except Exception as e:
            print(f"Translation error (AUTO->{self.target_lang}): {e}")
            return text

    def translate_to_en(self, text):
        if not text or not isinstance(text, str):
            return text
        try:
            return self.to_en.translate(text)
        except Exception as e:
            print(f"Translation error (AUTO->EN): {e}")
            return text

    @staticmethod
    def get_supported_languages():
        try:
            return GoogleTranslator().get_supported_languages(as_dict=True)
        except Exception:
            # Fallback to a minimal list if API fails
            return {"portuguese": "pt", "english": "en", "spanish": "es", "french": "fr", "german": "de"}

if __name__ == "__main__":
    translator = ChatTranslator()
    test_en = "Hello, how are you today?"
    test_pt = "Eu estou bem, obrigado!"
    
    print(f"EN -> PT: {test_en} => {translator.translate_to_pt(test_en)}")
    print(f"PT -> EN: {test_pt} => {translator.translate_to_en(test_pt)}")
