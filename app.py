import streamlit as st
from text_to_speech import convert_text_to_speech, translate_text
from pdf_processing import read_text_from_pdf

# Dictionary mapping language codes to language names
language_names = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "kn": "Kannada"
}

def text_to_speech():
    # Input options
    input_option = st.radio("Select input option", ("Text", "PDF"))

    # Input text or PDF file
    if input_option == "Text":
        input_text = st.text_area("Enter text to convert to speech")
    else:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file is not None:
            input_text = read_text_from_pdf(uploaded_file)
        else:
            input_text = ""

    # Display language selection with language codes and their corresponding languages
    input_lang = st.selectbox("Select input language", [(k, v) for k, v in language_names.items()], format_func=lambda x: f"{x[0]}: {x[1]}")
    target_lang = st.selectbox("Select target language", [(k, v) for k, v in language_names.items()], format_func=lambda x: f"{x[0]}: {x[1]}")

    # Convert text to speech
    if input_option == "Text":
        if st.button("Convert Text to Speech"):
            if input_text:
                translated_text = translate_text(input_text, input_lang[0], target_lang[0])
                if translated_text:
                    audio_bytes = convert_text_to_speech(translated_text, target_lang[0])
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                else:
                    st.warning("Failed to translate text.")
            else:
                st.warning("Please enter some text.")
    else:
        if st.button("Convert PDF Text to Speech"):
            if input_text:
                translated_text = translate_text(input_text, input_lang[0], target_lang[0])
                if translated_text:
                    audio_bytes = convert_text_to_speech(translated_text, target_lang[0])
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                else:
                    st.warning("Failed to translate text.")
            else:
                st.warning("Please upload a PDF file.")

def description():
    st.header("VAANI---Empowering-Inclusive-Communication-through-AI")
    st.write("""
    This software is designed to help blind and visually impaired individuals access and interact with text-based content in a more accessible way. Here's how you can use it:

    1. To use the Text-to-Speech functionality, click the "Text-to-Speech" button on the left.
    2. Choose the input option: You can either enter text directly or upload a PDF file.
    3. Select the input language: Choose the language of the text you want to convert to speech.
    4. Select the target language: Choose the language you want the text to be converted to for speech output.
    5. Click the "Convert Text to Speech" or "Convert PDF Text to Speech" button, depending on your input option.
    6. The software will translate the text to the target language and generate an audio output that you can listen to.

    This software leverages AI technologies like text-to-speech and translation to make text-based content more accessible for blind and visually impaired individuals. By converting text to audio, it enables users to listen to documents, books, and other materials in their preferred language, promoting greater independence and inclusion.
    """)

# Define the pages dictionary after the function definitions
pages = {
    "Description": description,
    "Text-to-Speech": text_to_speech
}

# st.title("Text-to-Speech App")

# Add a sidebar for navigation
selection = st.sidebar.selectbox("Go to", list(pages.keys()))

# Call the selected function
pages[selection]()