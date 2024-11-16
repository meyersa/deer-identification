import os
import cv2
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from duplicate_images.duplicate import get_matches
from duplicate_images.pair_finder_options import PairFinderOptions

# Define paths for processed images
IMAGE_DIR = os.path.join(os.getcwd(), "images")  # Path for original images
IMAGE_PROCESSED_DIR = os.path.join(os.getcwd(), "processed-images")  # Directory for processed images

def preflight_checks():
    """
    Ensure necessary directories exist.
    """
    print("Ensuring directory exists...")
    if not os.path.exists(IMAGE_PROCESSED_DIR):
        os.makedirs(IMAGE_PROCESSED_DIR)
        print(f"Created directory: {IMAGE_PROCESSED_DIR}")
    else:
        print(f"Directory already exists: {IMAGE_PROCESSED_DIR}")

def process_image(file_path, filename):
    """
    Process an image by cropping, resizing, and saving to the processed directory.

    Args:
        file_path (str): The path to the original image.
        filename (str): The name of the file to save the processed image as.
    """
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Image file could not be read.")

        # Crop the bottom 25 pixels
        img_cropped = img[:-25, :]

        # Resize the image (optional, adjust the scale factor as needed)
        img_resized = cv2.resize(
            img_cropped, (img_cropped.shape[1] // 2, img_cropped.shape[0] // 2)
        )

        # Save the processed image
        processed_file_path = os.path.join(IMAGE_PROCESSED_DIR, filename)
        cv2.imwrite(processed_file_path, img_resized)

        print(f"Processed and saved: {filename}")
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def remove_duplicates():
    """
    Search IMAGE_PROCESSED_DIR for duplicate images using duplicate_images library.

    Keeps the first image in each duplicate group and deletes the rest.
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

def process_images():
    """
    Iterate over all images in IMAGE_DIR, process them, and remove duplicates.

    Processes .png, .jpg, and .jpeg files using parallel processing.
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

if __name__ == "__main__":
    process_images()
