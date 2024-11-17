import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import json
import os
from typing import Dict, List, Any

# Environment variable paths
IMAGE_JSON: str = os.getenv("IMAGES_JSON", "images.json")
IMAGE_PROCESSED_DIR: str = os.getenv("IMAGE_PROCESSED_DIR", "processed-images")


def load_json_data() -> Dict[str, Any]:
    """
    Load image data from the JSON file.

    Returns:
        A dictionary containing image metadata.
    """
    if os.path.exists(IMAGE_JSON):
        try:
            with open(IMAGE_JSON, 'r') as file:
                data = json.load(file)
                print(f"Loaded JSON data from {IMAGE_JSON}")
                return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
    else:
        print(f"JSON file not found: {IMAGE_JSON}")
        return {}


# Initialize data
image_data: Dict[str, Any] = load_json_data()
image_keys: List[str] = list(image_data.keys())
current_index: int = 0
tagged_images: Dict[str, List[str]] = {}

def get_next_image() -> None:
    """Get the next image that hasn't been tagged yet."""
    global current_index
    while current_index < len(image_keys) and image_keys[current_index] in tagged_images:
        current_index += 1

    if current_index >= len(image_keys):  # All images tagged
        print("All images have been tagged.")
        tk.messagebox.showinfo("End of Images", "You have tagged all images.")
        save_tags()
        return

    load_image()

def get_previous_image() -> None:
    """Go back to the previous image."""
    global current_index
    if current_index > 0:
        current_index -= 1
        load_image()


def update_progress() -> None:
    """Update the progress label to show the current image index."""
    progress_label.config(
        text=f"Progress: {current_index + 1}/{len(image_keys)}"
    )


def update_tags_display() -> None:
    """Update the tags display for the current image."""
    image_id = image_keys[current_index]
    tags = image_data.get(image_id, {}).get("newTags", [])
    tags_text.config(state=tk.NORMAL)
    tags_text.delete(1.0, tk.END)
    tags_text.insert(tk.END, f"Tags: {', '.join(tags) if tags else 'None'}")
    tags_text.config(state=tk.DISABLED)


def update_image_info_display() -> None:
    """Update the image ID and file name display."""
    image_id = image_keys[current_index]
    image_info = image_data.get(image_id, {})
    image_info_text.config(state=tk.NORMAL)
    image_info_text.delete(1.0, tk.END)
    image_info_text.insert(tk.END, f"ID: {image_id}\nFile: {image_info.get('fullFilename', 'Unknown')}")
    image_info_text.config(state=tk.DISABLED)


def load_image() -> None:
    """Load the current image onto the screen."""
    global current_image, image_label

    # Clear existing image
    image_label.config(image="")

    if not image_keys:
        print("No images to display.")
        return

    # Get the current image data
    image_id = image_keys[current_index]
    image_info = image_data.get(image_id, {})
    image_path = os.path.join(IMAGE_PROCESSED_DIR, image_info.get("fullFilename", ""))

    # Open and display the image
    try:
        img = Image.open(image_path)
        img = img.resize((int(1.5 * 512), int(1.5 * 272)))  # Resize to fit the window
        current_image = ImageTk.PhotoImage(img)
        image_label.config(image=current_image)
    except FileNotFoundError:
        print(f"Image not found: {image_path}")

    update_progress()
    update_tags_display()
    update_image_info_display()


def save_tags() -> None:
    """Save the current tagged images back to the JSON file."""
    for image_id, tags in tagged_images.items():
        image_data[image_id]["newTags"] = tags

    try:
        with open(IMAGE_JSON, 'w') as file:
            json.dump(image_data, file, indent=4)
        print("Tags saved successfully.")
        tk.messagebox.showinfo("Save Tags", "Tags have been saved successfully.")
    except IOError as e:
        print(f"Error saving tags: {e}")
        tk.messagebox.showerror("Error", f"Could not save tags: {e}")


def tag_image(tag: str) -> None:
    """Tag the current image with the given tag and move to the next.

    Args:
        tag: The tag to apply to the current image.
    """
    global current_index

    if not image_keys:
        print("No images to tag.")
        return

    # Add the tag to the current image
    image_id = image_keys[current_index]
    if image_id not in tagged_images:
        tagged_images[image_id] = []
    tagged_images[image_id] = [tag]
    print(f"Tagged image {image_id} with '{tag}'.")

    get_next_image()


def create_gui() -> None:
    """Set up the GUI and run the application."""
    global image_label, progress_label, tags_text, image_info_text

    # Initialize the tkinter window
    window = tk.Tk()
    window.title("Image Tagging Tool")

    # Display the current image
    image_label = tk.Label(window)
    image_label.pack(pady=10)

    # Progress label
    progress_label = tk.Label(window, text="Progress: 0/0", font=("Arial", 12))
    progress_label.pack(pady=5)

    # Image info display (copyable)
    image_info_text = tk.Text(window, height=4, width=50, wrap=tk.WORD, font=("Arial", 10))
    image_info_text.config(state=tk.DISABLED)
    image_info_text.pack(pady=5)

    # Current tags display (copyable)
    tags_text = tk.Text(window, height=2, width=50, wrap=tk.WORD, font=("Arial", 10))
    tags_text.config(state=tk.DISABLED)
    tags_text.pack(pady=5)

    # Button container frame
    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)

    # Deer and Not Deer buttons
    deer_button = tk.Button(
        button_frame, text="Deer", command=lambda: tag_image("deer"), width=15
    )
    deer_button.grid(row=0, column=0, padx=10)

    not_deer_button = tk.Button(
        button_frame, text="Not Deer", command=lambda: tag_image("not-deer"), width=15
    )
    not_deer_button.grid(row=0, column=1, padx=10)

    # Back button
    back_button = tk.Button(
        window, text="Back", command=get_previous_image, width=20
    )
    back_button.pack(pady=10)

    # Save button
    save_button = tk.Button(
        window, text="Save Tags", command=save_tags, width=20
    )
    save_button.pack(pady=10)

    window.bind('b', lambda event: get_previous_image())
    window.bind('n', lambda event: tag_image("not-deer"))
    window.bind('m', lambda event: tag_image("deer"))

    # Start by loading the first image
    get_next_image()

    # Start the tkinter main loop
    window.mainloop()


# Driver code
if __name__ == "__main__":
    create_gui()
