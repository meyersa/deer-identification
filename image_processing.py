import os
import numpy as np
import cv2
from PIL import Image
import imagehash

# Define paths for processed images
IMAGE_DIR = os.path.join(os.getcwd(), "images")  # Path for original images
IMAGE_PROCESSED_DIR = os.path.join(os.getcwd(), "processed-images")  # Directory for processed images
IMAGE_SIM_THRESH = 30  # Perceptual hash threshold for detecting duplicates

# Create processed-images directory if it doesn't exist
if not os.path.exists(IMAGE_PROCESSED_DIR):
    os.makedirs(IMAGE_PROCESSED_DIR)

def process_image(file_path, filename):
    """
    Process an image by cropping the bottom 25 pixels, resizing, and saving it to the processed directory.

    Args:
        file_path (str): The path to the original image.
        filename (str): The name of the file to save the processed image as.
    """
    try:
        img = cv2.imread(file_path)

        # Crop the bottom 25 pixels
        img_cropped = img[:-25, :]

        # Resize the image (optional, you can adjust the scale factor as needed)
        img_resized = cv2.resize(img_cropped, (img_cropped.shape[1] // 2, img_cropped.shape[0] // 2))

        # Save the processed image
        processed_file_path = os.path.join(IMAGE_PROCESSED_DIR, filename)
        cv2.imwrite(processed_file_path, img_resized)

        print(f"Processed and saved {filename} to {processed_file_path}")

    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def remove_similar_images():
    """
    Remove visually similar images from the processed images directory based on perceptual hash.
    """
    removed = 0
    hashes = {}

    for filename in os.listdir(IMAGE_PROCESSED_DIR):
        file_path = os.path.join(IMAGE_PROCESSED_DIR, filename)

        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        try:
            # Compute the perceptual hash of the image
            img = Image.open(file_path)
            hash_value = imagehash.phash(img)

            # Check if any image with the same hash already exists
            if hash_value in hashes:
                print(f"Duplicate found: {filename}. Removing...")
                os.remove(file_path)
                removed += 1
            else:
                hashes[hash_value] = filename

        except Exception as e:
            print(f"Failed to process image for duplicate check: {filename} - {e}")

    print(f"Removed {removed} duplicate images")

def process_images():
    """
    Iterate over all images in the IMAGE_DIR, process them, and remove duplicates.
    """
    for filename in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, filename)

        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        process_image(file_path, filename)

    # After processing, remove duplicates
    remove_similar_images()

if __name__ == "__main__":
    process_images()
