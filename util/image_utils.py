import os
from PIL import Image

def get_image_files(folder):
    return [f for f in os.listdir(folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

def load_thumbnail(image_path, max_width, max_height):
    img = Image.open(image_path)
    img.thumbnail((max_width, max_height))
    return img
