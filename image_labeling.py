import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import json
import os

# Environment variable paths
IMAGE_JSON = os.getenv("IMAGES_JSON", "images.json")
IMAGE_PROCESSED_DIR = os.getenv("IMAGE_PROCESSED_DIR", "processed-images")

def load_json_data():
    """Load image data from the JSON file."""
    if os.path.exists(IMAGE_JSON):
        with open(IMAGE_JSON, 'r') as file:
            return json.load(file)
    else:
        print(f"JSON file not found: {IMAGE_JSON}")
        return {}

# Initialize data
image_data = load_json_data()
image_keys = list(image_data.keys())
current_index = 0
tagged_images = {}

def update_progress():
    """Update the progress label."""
    progress_label.config(
        text=f"Progress: {current_index + 1}/{len(image_keys)}"
    )

def update_tags_display():
    """Update the current tags display."""
    image_id = image_keys[current_index]
    tags = image_data.get(image_id).get("newTags")
    tags_text.config(state=tk.NORMAL)
    tags_text.delete(1.0, tk.END)
    tags_text.insert(tk.END, f"Tags: {', '.join(tags) if tags else 'None'}")
    tags_text.config(state=tk.DISABLED)

def update_image_info_display():
    """Update the image ID and file name display."""
    image_id = image_keys[current_index]
    image_info = image_data[image_id]
    image_info_text.config(state=tk.NORMAL)
    image_info_text.delete(1.0, tk.END)
    image_info_text.insert(tk.END, f"ID: {image_id}\nFile: {image_info['fullFilename']}")
    image_info_text.config(state=tk.DISABLED)

def load_image():
    """Load the current image on the screen."""
    global current_image, image_label

    # Clear existing image
    image_label.config(image="")

    # Get the current image data
    image_id = image_keys[current_index]
    image_info = image_data[image_id]
    image_path = os.path.join(IMAGE_PROCESSED_DIR, image_info["fullFilename"])

    # Open and display the image
    try:
        img = Image.open(image_path)
        img = img.resize((512, 272))  # Resize to fit the window
        current_image = ImageTk.PhotoImage(img)
        image_label.config(image=current_image)
    except FileNotFoundError:
        print(f"Image not found: {image_path}")

    update_progress()
    update_tags_display()
    update_image_info_display()

def save_tags():
    """Save the current tagged images to the JSON file."""
    for image_id, tags in tagged_images.items():
        image_data[image_id]["newTags"] = tags

    with open(IMAGE_JSON, 'w') as file:
        json.dump(image_data, file, indent=4)

    tk.messagebox.showinfo("Save Tags", "Tags have been saved successfully.")

def tag_image(tag):
    """Tag the current image and move to the next."""
    global current_index

    # Add the tag to the current image
    image_id = image_keys[current_index]
    if image_id not in tagged_images:
        tagged_images[image_id] = []
    tagged_images[image_id].append(tag)

    # Move to the next image
    if current_index < len(image_keys) - 1:
        current_index += 1
        load_image()
    else:
        tk.messagebox.showinfo("End of Images", "You have tagged all images.")
        save_tags()

def create_gui():
    """Set up the GUI and run the application."""
    global image_label, progress_label, tags_text, image_info_text

    # Initialize the tkinter window
    window = tk.Tk()
    window.title("Image Tagging Tool")
    window.geometry("600x800")

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

    # Save button
    save_button = tk.Button(
        window, text="Save Tags", command=save_tags, width=20
    )
    save_button.pack(pady=10)

    # Start by loading the first image
    load_image()

    # Start the tkinter main loop
    window.mainloop()

# Driver code
if __name__ == "__main__":
    create_gui()
