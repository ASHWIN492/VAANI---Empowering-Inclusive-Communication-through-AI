import tempfile
from gtts import gTTS
from googletrans import Translator
import json

def convert_text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(f"{fp.name}.mp3")
        audio_file = open(f"{fp.name}.mp3", "rb")
        audio_bytes = audio_file.read()
    return audio_bytes

def translate_text(text, src_lang, dest_lang):
    translator = Translator()
    try:
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except json.JSONDecodeError:
        return "Error: Unable to translate the text. Please try again later."