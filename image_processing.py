import torch
from torchvision import transforms
from torchvision.models import resnet50
from PIL import Image
import streamlit as st
import io
import speech_recognition as sr

# Load the pre-trained ResNet-50 model
model = resnet50(pretrained=True)
model.eval()

# Define the transformation to preprocess the image before feeding it to the model
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load the ImageNet class labels
with open("imagenet_labels.txt") as f:
    labels = [line.strip() for line in f.readlines()]

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Function to perform image recognition
def recognize_image(image_file):
    # Open the image file
    image = Image.open(image_file).convert('RGB')  # Convert to RGB

    # Preprocess the image
    image = preprocess(image).unsqueeze(0)

    # Perform inference
    with torch.no_grad():
        outputs = model(image)

    # Get the predicted label index
    _, predicted_idx = torch.max(outputs, 1)
    predicted_idx = predicted_idx.item()

    # Get the name of the predicted image class
    predicted_class_name = labels[predicted_idx]
    return predicted_class_name