import pickle
from PIL import Image
import io
from transformers import BlipProcessor, BlipForConditionalGeneration

def save_processor(processor):
    with open('processor.pkl', 'wb') as f:
        pickle.dump(processor, f)
    print("Processor saved to disk.")

def load_processor():
    with open('processor.pkl', 'rb') as f:
        processor = pickle.load(f)
    return processor

def save_model_and_processor():
    # Load pre-trained model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

    # Save processor and model to disk
    with open('processor.pkl', 'wb') as f:
        pickle.dump(processor, f)

    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("Processor and model saved to disk.")

def generate_caption(image_buffer, text=None):
    try:
        # Load the processor from disk
        processor = load_processor()

        # Load the model from disk
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)

        image = Image.open(image_buffer).convert('RGB')
        if text:
            inputs = processor(image, text, return_tensors="pt")
        else:
            inputs = processor(image, return_tensors="pt")

        out = model.generate(**inputs)
        return processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        return f"Error: {str(e)}"


