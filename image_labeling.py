import json
import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import os

# Environment variables
IMAGE_JSON = os.path.join(os.getcwd(), "images.json")
IMAGE_PROCESSED_DIR = os.path.join(os.getcwd(), "processed-images")

# Load the image data from the JSON file
def load_image_json():
    """
    Load the image JSON data.
    Returns a dictionary of image file names and their associated metadata.
    """
    try:
        with open(IMAGE_JSON, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("JSON file not found, starting with an empty dictionary.")
        return {}

# Save the image JSON data to file
def save_image_json(data):
    """
    Save the updated image JSON data to file.
    """
    with open(IMAGE_JSON, 'w') as f:
        json.dump(data, f, indent=6)
    print("Image tags saved.")

# Display an image using Tkinter
def display_image(image_path, window):
    """
    Display an image in the Tkinter window.
    """
    img = Image.open(image_path)
    img = img.resize((512, 272))  # Resize to fit the window

    # Convert the image to a Tkinter-compatible format
    img_tk = ImageTk.PhotoImage(img)

    label = tk.Label(window, image=img_tk)
    label.image = img_tk  # Keep a reference to the image
    label.grid(row=0, column=0, padx=10, pady=10)

# Add a tag to an image's metadata in memory
def add_tag_to_image(image_id, tag, image_data):
    """
    Add a tag to an image based on its ID in the image data.
    """
    if image_id in image_data:
        if tag not in image_data[image_id]["imageTags"]:
            image_data[image_id]["imageTags"].append(tag)
            print(f"Tag '{tag}' added to image ID: {image_id}")
        else:
            print(f"Tag '{tag}' already exists for image ID: {image_id}")
    else:
        print(f"Image ID '{image_id}' not found in the data.")

# Get the next image to display (first untagged image)
def get_next_image(image_data):
    """
    Get the next untagged image to display. Return the image ID and file path.
    """
    for image_id, data in image_data.items():
        if not data.get("imageTags"):  # If the image has no tags
            return image_id, os.path.join(IMAGE_PROCESSED_DIR, data["fullFilename"])
    return None, None  # No untagged images left

# Create the tagging window using Tkinter
def create_tagging_window():
    """
    Create the Tkinter window for image tagging.
    """
    # Load the image data from JSON
    image_data = load_image_json()

    # Create a new window
    window = tk.Tk()
    window.title("Image Tagging for CNN Training")

    # Get the next untagged image
    image_id, image_path = get_next_image(image_data)

    if image_id is None:
        print("All images are tagged.")
        window.quit()
        return

    # Display the image
    display_image(image_path, window)

    # Functions for tagging as "deer" or "not-deer"
    def tag_deer():
        add_tag_to_image(image_id, "deer", image_data)
        window.quit()

    def tag_not_deer():
        add_tag_to_image(image_id, "not-deer", image_data)
        window.quit()

    # Button for tagging as 'deer'
    deer_button = tk.Button(window, text="Deer", command=tag_deer)
    deer_button.grid(row=1, column=0, padx=10, pady=10)

    # Button for tagging as 'not-deer'
    not_deer_button = tk.Button(window, text="Not Deer", command=tag_not_deer)
    not_deer_button.grid(row=1, column=1, padx=10, pady=10)

    # Run the Tkinter event loop
    window.mainloop()

    # After closing the window, ask the user if they want to save changes
    save_prompt = tkinter.messagebox.askyesno("Save Tags", "Do you want to save all tagged images?")
    if save_prompt:
        save_image_json(image_data)

# Main loop to run the image tagging process
if __name__ == "__main__":
    create_tagging_window()
