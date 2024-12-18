import os
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from PIL import Image

def compress_image(input_path, output_path, max_size_mb=128, quality=85):
    # Open the image
    with Image.open(input_path) as img:
        # Convert to RGB for compatibility (JPEG format doesn't support transparency)
        img = img.convert("RGB")
        
        # Save the image with adjusted quality and progressive format if applicable
        img.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)
        
        # Check file size and adjust quality if needed
        while os.path.getsize(output_path) / (1024 * 1024) > max_size_mb:
            quality -= 5  # Gradually reduce quality
            img.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)

def process_images(brut_folder, compressed_folder, name_prefix):
    if not os.path.exists(compressed_folder):
        os.makedirs(compressed_folder)
    
    # Process each image in the brut files folder
    for idx, filename in enumerate(os.listdir(brut_folder), 1):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(brut_folder, filename)
            output_filename = f"{name_prefix}{idx}.jpeg"  # Create the new name
            output_path = os.path.join(compressed_folder, output_filename)

            print(f"Compressing {filename} -> {output_filename}")
            compress_image(input_path, output_path)

    messagebox.showinfo("Success", "Compression completed!")
    
def run_compression():
    name_prefix = name_entry.get()
    if not name_prefix:
        messagebox.showerror("Error", "Please enter a name prefix!")
        return
    
    process_images('Brut files folder', 'Compressed files folder', name_prefix)



# Create the GUI
root = Tk()
root.title("Image Compressor")

Label(root, text="Name Prefix:").grid(row=0, column=0, padx=10, pady=10)
name_entry = Entry(root)
name_entry.grid(row=0, column=1, padx=10, pady=10)

run_button = Button(root, text="Run", command=run_compression)
run_button.grid(row=1, column=0, columnspan=2, pady=20)

root.mainloop()

