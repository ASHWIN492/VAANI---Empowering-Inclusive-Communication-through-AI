import base64
import io
from gtts import gTTS
from googletrans import Translator
import streamlit as st
import sounddevice as sd
import soundfile as sf
import os
from transformers import BlipProcessor, BlipForConditionalGeneration
from pdf_processing import read_text_from_pdf
from image_processing import generate_caption
from text_to_speech import translate_text, convert_text_to_speech
from braille_converter import braille_to_text
from PIL import Image
import concurrent.futures
from pathlib import Path
import tempfile
import speech_recognition as sr
from streamlit_option_menu import option_menu

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
        recording = sd.rec(int(30 * fs), samplerate=fs, channels=2)

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



# Initialize session state for queries and images
if "queries" not in st.session_state:
    st.session_state["queries"] = []

if "images" not in st.session_state:
    st.session_state["images"] = []

def image_captioning_app():
    # Load pre-trained model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

    # Title and file uploader
    st.title("🖼️ Image Captioning App")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], help="Upload your image here")

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Generate caption for the uploaded image
        if st.button("Generate Caption"):
            with st.spinner("Generating caption..."):
                image_buffer = io.BytesIO(uploaded_file.getvalue())
                # Convert the image buffer to PIL Image
                image_pil = Image.open(image_buffer)
                # Process the image and generate the caption
                inputs = processor(images=image_pil, return_tensors="pt")
                outputs = model.generate(**inputs)
                response = processor.decode(outputs[0], skip_special_tokens=True)
                st.success(f"**Response:** {response}")  # Only display response

                # Convert the caption text to speech
                audio_bytes = convert_text_to_speech(response, 'en')
                st.audio(audio_bytes, format="audio/mp3", start_time=0)

                # Store the query and response in session state
                st.session_state["queries"].append({"question": "What is the image description?", "response": response})
                st.session_state["images"].append(uploaded_file.name)

        # Sidebar to show history of queries
        st.sidebar.title("📝 Query History")
        if st.session_state["queries"]:
            for idx, query in enumerate(st.session_state["queries"]):
                st.sidebar.write(f"**Image:** {st.session_state['images'][idx]}")
                st.sidebar.write(f"**Query:** {query['question']}")
                st.sidebar.write(f"**Response:** {query['response']}")
                                 
def description():
    # st.header("VAANI - Empowering Inclusive Communication through AI")
    st.write("""
    VAANI is a software designed to empower blind and visually impaired individuals by providing inclusive access to various forms of content through AI-driven technologies. Here's how you can utilize its features:

    1. **Text-to-Speech:** Convert text into speech in multiple languages. You can either directly input text or upload a PDF file containing the text you want to convert.  

       - **Steps to use:**
           1. Enter or upload the text you want to convert.
           2. Select the input and target languages.
           3. Click the "Convert Text to Speech" button. 🔊

       - **Educational benefits:** Blind students can access educational materials, including textbooks and lecture notes, in audio format, facilitating independent learning and improving academic performance. 📚

    2. **Image Captioning:** Upload an image to generate descriptive captions. It analyzes the content of the image and provides a verbal description of what is happening in the scene. 
            This feature enables users to understand the context and details of the image without relying on sight. 
            Additionally, VAANI converts the generated caption into speech, allowing users to listen to the description of the image.
       
        - **Steps to use:**
        
            1. Upload an image file.
            2. Click the "Generate Caption" button. 🖼️
            3. Educational Benefits: Enhance comprehension of visual content such as diagrams, charts, and illustrations, fostering a deeper understanding of various subjects. 🧠

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

    listening = True  # Variable to control the loop
    while listening:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Speak a command...")
            audio = r.listen(source)

        try:
            command = r.recognize_google(audio)
            st.write(f"You said: {command}")

            if command.lower() == "text to speech":
                text_to_speech()
                listening = False  # Stop listening after executing the command
            elif command.lower() == "image description":
                image_captioning_app()
                listening = False  # Stop listening after executing the command
            elif command.lower() == "record voice note":
                record_audio()
                listening = False  # Stop listening after executing the command
            elif command.lower() == "read braille":
                read_braille()
                listening = False  # Stop listening after executing the command
            elif command.lower() == "description":
                description()
                listening = False  # Stop listening after executing the command
            else:
                st.write("Invalid command. Please try again.")
                # Don't reset command to None to continue the loop

        except sr.UnknownValueError:
            st.write("Sorry, I couldn't understand that command. Can you speak again?")
            # Don't reset command to None to continue the loop
        except sr.RequestError as e:
            st.write(f"Error: {e}")
            # Don't reset command to None to continue the loop
    
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")
page_bg_img = f"""
<style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("https://img.freepik.com/free-vector/abstract-blue-circle-black-background-technology_1142-12714.jpg?size=626&ext=jpg&ga=GA1.1.1224184972.1712188800&semt=ais");
        background-size: cover; /* Cover the entire container */
        background-position: 30% center; /* Move the background image to the left */
        background-repeat: no-repeat;
        background-attachment: scroll; /* Scroll with the page */
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-image: url("data:image/png;base64,{img}");
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed; /* Fixed position */
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
        right: 2rem;
    }}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("VAANI - Empowering Inclusive Communication through AI")

selected = option_menu(
    menu_title=None,
    options=["about", "Voice Command", "Text-to-Speech", "Image Description", "Record Voice Note", "Read Braille"],
    icons=["file-person","mic","card-text","image","headset","chat"],
    orientation="horizontal",
)

if selected == "about":
    description()
elif selected == "Voice Command":
    handle_voice_command()
elif selected == "Text-to-Speech":
    text_to_speech()
elif selected == "Image Description":
    image_captioning_app()
elif selected == "Record Voice Note":
    record_audio()
elif selected == "Read Braille":
    read_braille()
