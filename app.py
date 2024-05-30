import io
from gtts import gTTS
from googletrans import Translator
import streamlit as st
import sounddevice as sd
import soundfile as sf
import os
from pdf_processing import read_text_from_pdf
from image_processing import recognize_image
from text_to_speech import translate_text, convert_text_to_speech
from braille_converter import braille_to_text
from PIL import Image
import concurrent.futures
from pathlib import Path
import tempfile
import speech_recognition as sr

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

# Function to handle text-to-speech requests from the queue
def read_braille():
    st.header("Read Braille")
    braille_input = st.text_area("Enter Braille text", height=200)

    if st.button("Read Braille"):
        if braille_input:
            text = braille_to_text(braille_input)
            audio_bytes = convert_text_to_speech(text, 'en')
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        else:
            st.warning("Please enter some Braille text.")

def record_audio():
    st.subheader("Record Voice Note 🎙️")

    # User input for file name
    file_name = st.text_input("Enter file name (without extension):", "recording")

    # Create a directory to save recordings
    recordings_dir = "recordings"
    Path(recordings_dir).mkdir(parents=True, exist_ok=True)

    # List saved recordings
    saved_recordings = os.listdir(recordings_dir)
    if saved_recordings:
        st.subheader("Saved Recordings")
        for recording in saved_recordings:
            file_path = os.path.join(recordings_dir, recording)
            # Display the file name
            st.write(f"File Name: {recording}")
            # Display the audio
            audio_bytes = open(file_path, 'rb').read()
            st.audio(audio_bytes, format="audio/wav")
            # Add a delete button for each saved recording
            if st.button(f"Delete {recording}", key=f"delete_{recording}"):
                # Delete the selected audio file
                os.remove(file_path)
                st.success(f"Deleted {recording}")
                # Refresh the page to reflect the changes
                st.experimental_rerun()

    # Recording functionality
    recording = None
    is_recording = False

    if st.button("Start Recording"):
        is_recording = True
        fs = 44100  # Sample rate
        recording = sd.rec(int(10 * fs), samplerate=fs, channels=2)

    if is_recording:
        with st.spinner("Recording..."):
            sd.wait()  # Wait until recording is finished

        # Save the recording as a WAV file with the provided file name
        file_path = os.path.join(recordings_dir, f"{file_name}.wav")
        sf.write(file_path, recording, fs)

        # Display the recorded audio
        audio_bytes = open(file_path, 'rb').read()
        st.audio(audio_bytes, format='audio/wav')

        # Display the file name
        st.write(f"File saved as: {file_name}.wav")

def text_to_speech():
    # Input options
    input_option = st.radio("Select input option", ("Text 📝", "PDF 📄"))

    # Input text or PDF file
    if input_option == "Text 📝":
        input_text = st.text_area("Enter text to convert to speech 🗣️")
    else:
        uploaded_file = st.file_uploader("Upload a PDF file 📂", type=["pdf"])
        if uploaded_file is not None:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(read_text_from_pdf, uploaded_file)
                input_text = future.result()
        else:
            input_text = ""

    # Display language selection with language codes and their corresponding languages
    input_lang = st.selectbox("Select input language 🌍", [(k, v) for k, v in language_names.items()], format_func=lambda x: f"{x[0]}: {x[1]}")
    target_lang = st.selectbox("Select target language 🌐", [(k, v) for k, v in language_names.items()], format_func=lambda x: f"{x[0]}: {x[1]}")

    # Convert text to speech
    if st.button("Convert Text to Speech 🔊"):
        if input_text:
            translated_text = translate_text(input_text, input_lang[0], target_lang[0])
            if translated_text:
                audio_bytes = convert_text_to_speech(translated_text, target_lang[0])
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
            else:
                st.warning("Failed to translate text. 🚫")
        else:
            st.warning("Please enter some text. 📝")

def image_captioning_app():
    st.title("Image Captioning")

    # Upload image
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        # Open the uploaded image file
        image_file = io.BytesIO(uploaded_image.read())

        image = Image.open(image_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Generate caption button
        if st.button("Generate Caption"):
            # Generate caption
            predicted_label = recognize_image(image_file)

            # Display caption
            st.subheader("Generated Caption")
            st.write("Predicted label:", predicted_label)

            # Convert text to speech
            tts = gTTS(text=predicted_label, lang='en')

            # Save the speech to a temporary file
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                tts.save(f"{fp.name}.mp3")
                audio_file = open(f"{fp.name}.mp3", "rb")
                audio_bytes = audio_file.read()

            # Play the speech
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

def description():
    st.header("VAANI - Empowering Inclusive Communication through AI")
    st.write("""
    VAANI is a software designed to empower blind and visually impaired individuals by providing inclusive access to various forms of content through AI-driven technologies. Here's how you can utilize its features:

    1. **Text-to-Speech:** Convert text into speech in multiple languages. You can either directly input text or upload a PDF file containing the text you want to convert.  

       - **Steps to use:**
           1. Enter or upload the text you want to convert.
           2. Select the input and target languages.
           3. Click the "Convert Text to Speech" button. 🔊

       - **Educational benefits:** Blind students can access educational materials, including textbooks and lecture notes, in audio format, facilitating independent learning and improving academic performance. 📚

    2. **Image Captioning:** Upload an image to generate a descriptive caption for it. This feature enables users to understand the content of images without relying on visual perception.  

       - **Steps to use:**
           1. Upload an image file.
           2. Click the "Generate Caption" button. 🖼️

       - **Educational benefits:** Blind students can comprehend visual content such as diagrams, charts, and illustrations, enhancing their understanding of complex concepts in subjects like science, mathematics, and geography. 🧠

    3. **Record Voice Note:** Start recording voice notes, which are saved for future reference. This functionality allows users to create audio recordings for personal memos or messages.  

       - **Steps to use:**
           1. Enter a name for the recording (optional).
           2. Click the "Start Recording" button to begin.
           3. Click the "Stop Recording" button to finish. 🎙️

       - **Educational benefits:** Blind students can create voice notes to summarize key points, review study materials, or dictate essays, improving organization and retention of information. 📝

    4. **Read Braille:** Convert Braille text into speech. Users can input Braille text, and VAANI will convert it into spoken language for auditory consumption.  

       - **Steps to use:**
           1. Enter Braille text into the text area.
           2. Click the "Read Braille" button. 📖

       - **Educational benefits:** Blind students can access Braille materials, including tactile graphics and equations, in audio format, facilitating learning in subjects like mathematics, music, and languages. 🎶

    VAANI leverages cutting-edge AI technologies such as text-to-speech synthesis, image recognition, and natural language processing to make text-based and visual content more accessible for individuals with visual impairments. By converting text to audio, providing image descriptions, and supporting Braille text conversion, VAANI promotes greater independence and inclusion for its users. 🌟
    """)





def handle_voice_command():
    st.write("Voice Command Instructions:")
    st.write("- Speak one of the following commands:")
    st.write("  - 'Text to Speech' to convert text into speech.")
    st.write("  - 'Image Description' to generate a caption for an uploaded image.")
    st.write("  - 'Record Voice Note' to start recording a voice note.")
    st.write("  - 'Read Braille' to convert Braille text into speech.")
    st.write("  - 'Description' to display information about the software.")
    st.write("- Make sure your microphone is enabled and speak clearly.")
    st.write("")

    command = None
    while not command:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Speak a command...")
            audio = r.listen(source)

        try:
            command = r.recognize_google(audio)
            st.write(f"You said: {command}")

            if command.lower() == "text to speech":
                text_to_speech()
            elif command.lower() == "image description":
                image_captioning_app()
            elif command.lower() == "record voice note":
                record_audio()
            elif command.lower() == "read braille":
                read_braille()
            elif command.lower() == "description":
                description()
            else:
                st.write("Invalid command. Please try again.")
                command = None  # Reset command to None to continue the loop

        except sr.UnknownValueError:
            st.write("Sorry, I couldn't understand that command. Can you speak again?")
            command = None  # Reset command to None to continue the loop
        except sr.RequestError as e:
            st.write(f"Error: {e}")


# Define the pages dictionary after the function definitions
pages = {
    "voice Command":handle_voice_command,
    "Description": description,
    "Text-to-Speech": text_to_speech,
    "Image-description": image_captioning_app,
    "Record Voice Note": record_audio,
    "Read Braille": read_braille,
    
}

# Add a sidebar for navigation
selection = st.sidebar.selectbox("Go to", list(pages.keys()))

# If the selection is "Voice Command", handle the voice command
if selection == "Voice Command":
    handle_voice_command()
else:
    # Call the selected function
    pages[selection]()
