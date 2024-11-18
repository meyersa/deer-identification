import os
import cv2
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from duplicate_images.duplicate import get_matches
from duplicate_images.pair_finder_options import PairFinderOptions

# Define paths for processed images
IMAGE_DIR = os.path.join(os.getcwd(), "images")  # Path for original images
IMAGE_PROCESSED_DIR = os.path.join(os.getcwd(), "processed-images")  # Directory for processed images
IMAGE_JSON = os.path.join(os.getcwd(), "images.json")

def preflight_checks() -> None:
    """
    Ensure the required directories for processing images exist. 
    Creates the processed images directory if it does not exist.
    """
    print("Ensuring directory exists...")
    if not os.path.exists(IMAGE_PROCESSED_DIR):
        os.makedirs(IMAGE_PROCESSED_DIR)
        print(f"Created directory: {IMAGE_PROCESSED_DIR}")
    else:
        print(f"Directory already exists: {IMAGE_PROCESSED_DIR}")

def process_image(file_path: str, filename: str) -> None:
    """
    Process an image by cropping, resizing, and saving it to the processed directory.

    Args:
        file_path (str): The full path to the original image file.
        filename (str): The name of the file to save the processed image under.
    """
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Image file could not be read.")

        # Crop the bottom 25 pixels
        img_cropped = img[:-35, :]

        # Save the processed image
        processed_file_path = os.path.join(IMAGE_PROCESSED_DIR, filename)
        cv2.imwrite(processed_file_path, img_cropped)

        print(f"Processed and saved: {filename}")
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def remove_duplicates() -> None:
    """
    Identify and remove duplicate images in the processed images directory.
    
    Uses the `duplicate_images` library to find duplicates based on image hashes.
    Retains only the first image in each duplicate group.
    """
    print("Searching for duplicates...")
    try:
        dup_options = PairFinderOptions(
            max_distance=0,
            hash_size=None,
            show_progress_bars=False,
            parallel=True,
            slow=False,
            group=True,
        )

        duplicates = get_matches(
            [Path(IMAGE_PROCESSED_DIR)], 'phash', dup_options, None, None
        )

        for duplicate_group in duplicates:
            # Keep the first image, delete the rest
            for duplicate in duplicate_group[1:]:
                os.remove(duplicate)
                print(f"Removed duplicate: {duplicate}")

        print("Duplicate removal complete.")
    except Exception as e:
        print(f"Error during duplicate removal: {e}")

def clean_json() -> None:
    """
    Update the JSON file to include only the images currently in the processed directory.

    Loads existing image data from the JSON file, filters it to match current processed images,
    and saves the updated data back to the file.
    """
    print("Saving new JSON to file...")

    all_images = dict()
    cur_images = [
        f for f in os.listdir(IMAGE_PROCESSED_DIR)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    try:
        with open(IMAGE_JSON, 'r') as f:
            all_images.update(json.load(f))
    except FileNotFoundError:
        print("JSON file not found. Creating a new one.")

    final_images = {key: value for key, value in all_images.items() if f'{key}.JPG' in cur_images}

    # Delete imageUrl since it is crazy long with AWS access token
    for k, v in final_images.items(): 
        if "imageUrl" in v:
            del v["imageUrl"]

    with open(IMAGE_JSON, 'w') as f:
        json.dump(final_images, f, indent=6)

    print("Done saving to file.")

def process_images() -> None:
    """
    Orchestrate the full image processing workflow:
    - Ensure necessary directories exist.
    - Process all images in the `IMAGE_DIR` directory.
    - Remove duplicate images from the processed directory.
    - Update the JSON file with the current processed images.
    """
    preflight_checks()
    print("Starting image processing...")

    # List of valid image files
    image_files = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    if not image_files:
        print("No images found in the directory.")
        return

    # Process images in parallel
    with ThreadPoolExecutor() as executor:
        for filename in image_files:
            file_path = os.path.join(IMAGE_DIR, filename)
            executor.submit(process_image, file_path, filename)

    print("Image processing complete. Now removing duplicates...")

    remove_duplicates()
    clean_json()

if __name__ == "__main__":
    process_images()
