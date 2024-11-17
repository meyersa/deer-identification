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
        try:
            with open(IMAGE_JSON, 'r') as file:
                data = json.load(file)
                print(f"Loaded JSON data from {IMAGE_JSON}")
                return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"JSON file not found: {IMAGE_JSON}")
    return {}

def save_tags():
    """Save the tagged images back to the JSON file."""
    try:
        with open(IMAGE_JSON, 'w') as file:
            json.dump(image_data, file, indent=4)
        print("Tags saved successfully.")
        tkinter.messagebox.showinfo("Save Tags", "Tags have been saved successfully.")
    except IOError as e:
        print(f"Error saving tags: {e}")
        tkinter.messagebox.showerror("Error", f"Could not save tags: {e}")

def load_image(image_id):
    """Load and display the current image."""
    image_info = image_data.get(image_id, {})
    image_path = os.path.join(IMAGE_PROCESSED_DIR, image_info.get("fullFilename"))
    
    try:
        img = Image.open(image_path)
        img = img.resize((int(1.5 * 512), int(1.5 * 272)))  # Resize to fit the window
        return ImageTk.PhotoImage(img)
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
        return None

def update_image_info(image_id):
    """Update the image info display."""
    image_info = image_data.get(image_id, {})
    image_info_text.config(state=tk.NORMAL)
    image_info_text.delete(1.0, tk.END)
    image_info_text.insert(tk.END, f"ID: {image_id}\nFile: {image_info.get('fullFilename', 'Unknown')}")
    image_info_text.config(state=tk.DISABLED)

def update_tags_display(image_id):
    """Update the current image's tags display."""
    tags = image_data.get(image_id, {}).get("newTags", [])
    tags_text.config(state=tk.NORMAL)
    tags_text.delete(1.0, tk.END)
    tags_text.insert(tk.END, f"Tags: {', '.join(tags) if tags else 'None'}")
    tags_text.config(state=tk.DISABLED)

def update_progress(current_index, total_images):
    """Update the progress label."""
    progress_label.config(text=f"Progress: {current_index + 1}/{total_images}")

def tag_image(tag, image_id):
    """Tag the current image with the given tag."""
    image_data[image_id]["newTags"] = [tag]
    print(f"Tagged image {image_id} with '{tag}'")

    show_next_image()

def create_gui():
    """Set up the GUI and run the application."""
    global image_label, progress_label, tags_text, image_info_text, current_image

    # Initialize the tkinter window
    window = tk.Tk()
    window.title("Image Tagging Tool")

    # Initialize widgets
    image_label = tk.Label(window)
    image_label.pack(pady=10)

    progress_label = tk.Label(window, text="Progress: 0/0", font=("Arial", 12))
    progress_label.pack(pady=5)

    image_info_text = tk.Text(window, height=4, width=50, wrap=tk.WORD, font=("Arial", 10))
    image_info_text.config(state=tk.DISABLED)
    image_info_text.pack(pady=5)

    tags_text = tk.Text(window, height=2, width=50, wrap=tk.WORD, font=("Arial", 10))
    tags_text.config(state=tk.DISABLED)
    tags_text.pack(pady=5)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)

    # Tag buttons
    deer_button = tk.Button(button_frame, text="Deer", command=lambda: tag_image("deer", current_image_id), width=15)
    deer_button.grid(row=0, column=0, padx=10)

    not_deer_button = tk.Button(button_frame, text="Not Deer", command=lambda: tag_image("not-deer", current_image_id), width=15)
    not_deer_button.grid(row=0, column=1, padx=10)

    bad_button = tk.Button(button_frame, text="Bad Image", command=lambda: tag_image("bad", current_image_id), width=15)
    bad_button.grid(row=0, column=3, padx=10)

    # Navigation buttons
    back_button = tk.Button(window, text="Back", command=show_previous_image, width=20)
    back_button.pack(pady=10)

    save_button = tk.Button(window, text="Save Tags", command=save_tags, width=20)
    save_button.pack(pady=10)

    # Bind keyboard shortcuts
    window.bind('b', lambda event: show_previous_image())
    window.bind('n', lambda event: tag_image("not-deer", current_image_id))
    window.bind('m', lambda event: tag_image("deer", current_image_id))
    window.bind('v', lambda event: tag_image("bad", current_image_id))

    # Start the application
    load_next_image()

    window.mainloop()

def load_next_image():
    """Load the next image."""
    global current_image_id, current_image

    if not image_data:
        print("No images to display.")
        return

    # Find the next image without tags (start with the first untagged image)
    current_image_id = next((img_id for img_id, info in image_data.items() if "newTags" not in info), None)

    if current_image_id:
        img = load_image(current_image_id)
        if img:
            current_image = img  # Keep a reference to the image
            image_label.config(image=current_image)
            update_progress(list(image_data).index(current_image_id), len(image_data))
            update_tags_display(current_image_id)
            update_image_info(current_image_id)
        else:
            print(f"Image {current_image_id} failed to load.")
    else:
        print("All images tagged.")
        tkinter.messagebox.showinfo("End of Images", "You have tagged all images.")

def show_previous_image():
    """Go back to the previous image."""
    global current_image_id, current_image
    image_ids = list(image_data.keys())
    current_index = image_ids.index(current_image_id)
    
    # Make sure the previous image is loaded and properly handles going up and down
    if current_index > 0:
        current_image_id = image_ids[current_index - 1]
        img = load_image(current_image_id)
        if img:
            current_image = img  # Keep a reference to the image
            image_label.config(image=current_image)
            update_tags_display(current_image_id)
            update_image_info(current_image_id)
            update_progress(current_index - 1, len(image_data))

def show_next_image():
    """Go to the next image."""
    global current_image_id, current_image
    image_ids = list(image_data.keys())
    current_index = image_ids.index(current_image_id)
    
    # Make sure the next image is loaded and properly handles going up and down
    if current_index < len(image_ids) - 1:
        current_image_id = image_ids[current_index + 1]
        img = load_image(current_image_id)
        if img:
            current_image = img  # Keep a reference to the image
            image_label.config(image=current_image)
            update_tags_display(current_image_id)
            update_image_info(current_image_id)
            update_progress(current_index + 1, len(image_data))

# Driver code
if __name__ == "__main__":
    image_data = load_json_data()  # Load image data at the start
    create_gui()
