import time
import tkinter as tk
import numpy as np
from PIL import ImageGrab, Image, ImageTk


UPDATE_DELAY_MS = 50 # How often to update (in milliseconds), e.g., 50ms = 20 FPS
TRANSPARENT_COLOR = "#fe01dc" # Choose a color that you will NOT draw with
APP_NAME = "Overlay Example"


# Replace this function with your actual image processing logic
def process_image(screen):
    """
    Processes the captured screen image.

    Args:
        screen (PIL.Image.Image): The captured screen image.

    Returns:
        A list of drawing commands for the overlay canvas.
        Example command format:
        ("rectangle", x1, y1, x2, y2, outline_color, fill_color)
        ("text", x, y, text_content, fill_color, font_details)
        ("image", x, y, tk_photo_image)
    """
    draw_commands = []

    # Example: Crop the US box and convert to grayscale
    # Coordinates match the Echo Wave GUI on a 1920x1080px display (adjust to match your setup)
    us_box = (578, 280, 1343, 819)
    us_pil = screen.crop(us_box).convert("L")
    # Convert to a numpy array
    us_np = np.array(us_pil)

    # Example: Draw the mean US pixel value below the US box
    draw_commands.append(("text", 887, 902, f"{us_np.mean():>6.2f}", "yellow", ("Courier New", 24, "bold")))

    # Example: Draw a red rectangle below the US box
    draw_commands.append(("rectangle", 194, 839, 1726, 1009, "red", ""))

    # Example: Draw a resized, flipped version of the US image to the right of the US box
    small_us_pil = us_pil.resize((266, 187)).transpose(Image.FLIP_TOP_BOTTOM)
    small_us_tk = ImageTk.PhotoImage(small_us_pil)
    draw_commands.append(("image", 1460, 642, small_us_tk))

    return draw_commands

# Tkinter overlay setup
root = tk.Tk()
root.title(APP_NAME)

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Make window borderless, always on top, and cover the screen
root.overrideredirect(True)
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.lift()
root.wm_attributes("-topmost", True)

# Configure for color key transparency
# Set root window background to the transparent color
root.config(bg=TRANSPARENT_COLOR)
# Set the attribute to make this color transparent
root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
# Create Canvas with the same background color and no border
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg=TRANSPARENT_COLOR, highlightthickness=0)
canvas.pack()

# Flag to signal the main loop to stop
running = True

# Store PhotoImage references to prevent garbage collection if drawing images
image_references = []

# Main update loop
def update_overlay():
    global running, image_references
    if not running:
        root.destroy()
        return

    start_time = time.time()

    # Capture screen
    # Set bbox=(x, y, width, height) to specify a region or specific monitor
    # For the primary monitor, None usually works
    screenshot = ImageGrab.grab(bbox=None, all_screens=False)

    # Process image
    drawing_commands = process_image(screenshot)

    # Update overlay canvas
    # Clear previous drawings
    canvas.delete("all")
    image_references = []
    # Execute drawing commands returned by process_image
    for cmd in drawing_commands:
        command_type = cmd[0]
        if command_type == "rectangle":
            _, x1, y1, x2, y2, outline_color, fill_color = cmd
            canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, fill=fill_color)
        elif command_type == "text":
            _, x, y, text, fill_color, font_details = cmd
            canvas.create_text(x, y, text=text, fill=fill_color, font=font_details, anchor=tk.NW)
        elif command_type == "image":
            _, x, y, tk_photo_image = cmd
            canvas.create_image(x, y, image=tk_photo_image, anchor=tk.NW)
            image_references.append(tk_photo_image)

    elapsed_time = time.time() - start_time

    # Ensure a delay of at least 1ms
    delay = max(1, UPDATE_DELAY_MS - int(elapsed_time * 1000))
    # Schedule the next update
    root.after(delay, update_overlay)

# Exit mechanism
def quit_app(event=None):
    global running
    print("Exiting application")
    running = False

# Bind the Q key press to the quit_app function
root.bind("<q>", quit_app)

# Start the application
print("Starting application")
print("Press Q in the overlay window to exit")

# Start the first update cycle after a brief moment
root.after(10, update_overlay)

# Start the Tkinter event loop
root.mainloop()
