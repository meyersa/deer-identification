"""
Get all images from stealthcamcommand.com for training
"""

import requests 
import json
import os 
import dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

dotenv.load_dotenv()

# Can't be none - checked in preflight
API_URL = os.getenv("API_URL")
API_BEARER = os.getenv("API_BEARER")

# Defaults to checking if None
IMAGE_TOTAL = int(os.getenv("IMAGE_TOTAL"))

# Default values
TAKE_AMOUNT = int(os.getenv("TAKE_AMOUNT") or 50)
IMAGE_DIR = os.path.join(os.getcwd(), "images")
IMAGE_JSON = os.path.join(os.getcwd(), "images.json")

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
        image_dict[image.get("filename")] = {
            "imageUrl" : image.get("imageUrl"),
            "createdDateTime": image.get("createdDateTime"),
            "fullFilename": image.get("fullFilename"), 
            "imageGuid": image.get("imageGuid"),
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
    Download an image from the provided URL and save it to the IMAGE_DIR directory.

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
        
        # Save image to the original directory
        with open(file_path, 'wb') as f:
            f.write(res.content)

        print(f'Image {fullFilename} saved')

    except Exception as e:
        print(f'Failed to download image: {e}')

def build_images(): 
    """
    Main function to orchestrate the image download process with multithreading.

    This function performs the following steps:
    - Verifies that all required conditions (e.g., environment variables and directories) are met.
    - Retrieves the total number of images available from the API.
    - Iteratively fetches batches of images and downloads them concurrently to the local 'images' directory.
    - Continues fetching images until all available images have been downloaded.

    Raises:
        ValueError: If the preflight checks fail (e.g., missing environment variables).
        HTTPError: If any API request fails.
    """
    preflight_checks()

    skip = 0
    take = TAKE_AMOUNT
    image_total = IMAGE_TOTAL

    all_images = dict() 

    # Set default amount of images to get if not set
    if not image_total:
        image_total = get_image_count()

    while True:         
        if (skip + take) > image_total:
            take = image_total - skip

        print(f'Getting images {skip}/{image_total}...')

        res_images = get_image_range(skip, take)
        print(f'Received {len(res_images)}. Saving...')

        all_images.update(res_images) 

        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust `max_workers` as needed
            future_to_image = {
                executor.submit(get_image, image.get("imageUrl"), image.get("fullFilename")): image
                for image in res_images.values()
            }

            for future in as_completed(future_to_image):
                image = future_to_image[future]
                try:
                    future.result()  # Raises exception if download failed
                    print(f"Saved image: {image.get('fullFilename')}")
                except Exception as e:
                    print(f"Failed to save image {image.get('fullFilename')}: {e}")

        print('Saved all images')

        skip += take

        if skip > (image_total - 1): 
            break

    print(f'Saving image dictionary to JSON...')

    with open(IMAGE_JSON, 'w') as f: 
        json.dump(all_images, f, indent=6)

    print(f'Saved') 

if __name__ == "__main__": 
    build_images()