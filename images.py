"""
Get all images from stealthcamcommand.com for training
"""

import requests 
import json
import os 
import dotenv
import time 
import cv2
import numpy as np
from PIL import Image
import imagehash

dotenv.load_dotenv()

# Can't be none - checked in preflight
API_URL = os.getenv("API_URL")
API_BEARER = os.getenv("API_BEARER")

# Defaults to checking if None
IMAGE_TOTAL = int(os.getenv("IMAGE_TOTAL"))

# Default values
TAKE_AMOUNT = int(os.getenv("TAKE_AMOUNT") or 50)
IMAGE_DIR = os.path.join(os.getcwd(), "images")
IMAGE_SIM_THRESH = int(os.getenv("IMAGE_SIM_THRESH") or 100)

post_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Authorization": f'Bearer {API_BEARER}',
    "Accept": "application/json",
    "Content-Type": "application/json"

}

def preflight_checks(): 
    """
    Perform preflight checks to validate the environment variables and ensure necessary directories exist.

    This function checks if the required environment variables (API_URL, API_BEARER) are set and if the 
    image directory exists. If the directory does not exist, it will be created.

    Raises:
        ValueError: If any environment variables are missing.
    """
    print("Checking conditions...")

    if None in [API_URL, API_BEARER]: 
        raise ValueError("Missing ENV values")

    print("ENVs are valid")

    if not os.path.exists(IMAGE_DIR): 
        os.makedirs(IMAGE_DIR)
        print("Image dir does not exist, created")

    else: 
        print("Image dir exists")

    print("Conditions met")

def get_image_count(): 
    """
    Fetch the total number of images available from the API.

    Sends a request to the API to retrieve the image count.

    Returns:
        int: The total number of images available in the system.

    Raises:
        HTTPError: If the request to the API fails.
    """
    print("Requesting image count...")

    post_url = f'{API_URL}/api/v3/file-manager/images/count'
    post_body = json.dumps({"skipcount": 0})

    res = requests.post(post_url, headers=post_headers, data=post_body)
    res.raise_for_status()

    image_count = res.json()

    print(f'Found {image_count} images')

    return image_count

def get_image_range(skip, take): 
    """
    Fetch a range of image data from the API starting at the specified skip value.

    Args:
        skip (int): The starting index (offset) for fetching the images.
        take (int): The amount of images to take when fetching the images.

    Returns:
        dict: A dictionary where each key is an image GUID, and the value is another dictionary with details about the image.
            - 'imageUrl': URL of the image
            - 'createdDateTime': The creation date and time of the image
            - 'fullFilename': The full filename of the image
            - 'imageGuid': GUID of the image
            - 'imageTags': Tags associated with the image
            - 'moonPhase': The moon phase during image capture
            - 'pressure': Atmospheric pressure recorded
            - 'pressureTendency': Pressure trend (e.g., rising, falling)
            - 'temperature': Temperature recorded during image capture
            - 'wind': Wind speed recorded
            - 'windDirection': Wind direction recorded as an integer (degrees)

    Raises:
        HTTPError: If the request to the API fails.
    """
    print(f'Requesting image range {skip}...')

    post_url = f'{API_URL}/api/v4/file-manager/images'
    post_body = json.dumps({"skipcount": skip, "takeCount": take})

    res = requests.post(post_url, headers=post_headers, data=post_body)
    res.raise_for_status()

    image_res = res.json()

    print(f'Found {len(image_res.get("images"))} images for {skip}')

    image_dict = dict() 
    for image in image_res.get("images"): 
        imageGuid = image.get("imageGuid")

        image_dict[imageGuid] = {
            "imageUrl" : image.get("imageUrl"),
            "createdDateTime": image.get("createdDateTime"),
            "fullFilename": image.get("fullFilename"), 
            "imageGuid": imageGuid,
            "imageTags": image.get("imageTags"), 
            "moonPhase": image.get("moonPhase"),
            "pressure": image.get("pressure"),
            "pressureTendency": image.get("pressureTendency"),
            "temperature": image.get("temperature"),
            "wind": image.get("wind"),
            "windDirection": image.get("windDirection"), 

        }

    return image_dict

def get_image(url, fullFilename):
    """
    Download an image from the provided URL, save it, and remove a 50-pixel border at the bottom.

    Args:
        url (str): The URL from which the image will be downloaded.
        fullFilename (str): The name with which the image will be saved in the local directory.
    """
    print(f'Getting image {fullFilename}...')
    file_path = os.path.join(IMAGE_DIR, fullFilename)

    if os.path.exists(file_path):
        print(f'Image {fullFilename} already exists, skipping')
        return

    try:
        res = requests.get(url, stream=True)
        res.raise_for_status()
        
        # Load image into memory
        image_array = np.asarray(bytearray(res.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is not None:
            # Remove 50-pixel border at the bottom
            cropped_image = image[:-35, :]  # Crop 50 pixels from the bottom

            # Save cropped image
            cv2.imwrite(file_path, cropped_image)
            print(f'Image {fullFilename} saved with border removed')
        else:
            print(f'Failed to decode image {fullFilename}')

    except Exception as e:
        print(f'Failed to download image.', e)

def build_images(): 
    """
    Main function to orchestrate the image download process.

    This function performs the following steps:
    - Verifies that all required conditions (e.g., environment variables and directories) are met.
    - Retrieves the total number of images available from the API.
    - Iteratively fetches batches of images and downloads them to the local 'images' directory.
    - Continues fetching images until all available images have been downloaded.

    Raises:
        ValueError: If the preflight checks fail (e.g., missing environment variables).
        HTTPError: If any API request fails.
    """
    preflight_checks()

    skip = 0
    take = TAKE_AMOUNT
    image_total = IMAGE_TOTAL

    # Set default amount of images to get if not set
    if not image_total:
        image_total = get_image_count()

    while True:         
        # <-- Decide how many images to get -->
        if (skip + take) > image_total:

            # Should be the remainder
            # Fail logic is considered before starting loop
            take = image_total - skip

        # <-- Get images section -->
        print(f'Getting images {skip}/{image_total}...')

        res_images = get_image_range(skip, take)
        print(f'Received {len(res_images)}. Saving...')

        print(f'Saving images...')
        for image in res_images.values(): 
            fail_count = 0
            while True: 
                try:
                    get_image(image.get("imageUrl"), image.get("fullFilename"))
                    break 

                except: 
                    fail_count += 1

                    # If failed more than 3 times, continue
                    if fail_count > 3: 
                        print(f'Failed to download {image.get("fullFilename")} after 3 attemps, skipping')
                        break

                    print(f'Failed to get image {image.get("fullFilename")}. Retrying in {15 * fail_count} seconds...')
                    time.sleep(15 * fail_count)
        
        print(f'Saved all images')

        # <-- Skip logic --> 
        skip += take

        # Over
        if skip > (image_total - 1): 
            break

def remove_similar_images():
    """
    Remove visually similar images based on perceptual hash.
    """
    removed = 0 

    hashes = {}
    for filename in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, filename)
        if os.path.isfile(file_path):
            try:
                img = Image.open(file_path)
                phash = imagehash.phash(img)  # Calculate perceptual hash
                if any(phash - h >= IMAGE_SIM_THRESH for h in hashes.keys()):
                    print(f"Similar image found: {file_path}, removing.")
                    os.remove(file_path)
                    removed += 1
                else:

                    hashes[phash] = file_path
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(str(IMAGE_SIM_THRESH) + " " + str(removed))


if __name__ == "__main__":
    build_images()
    remove_similar_images()