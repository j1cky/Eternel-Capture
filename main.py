import os
from PIL import Image

def compress_image(input_path, output_path, max_size_mb=128):
    # Open an image file
    with Image.open(input_path) as img:
        # Calculate the current size
        img_size = os.path.getsize(input_path) / (1024 * 1024)  # in MB
        if img_size <= max_size_mb:
            img.save(output_path, optimize=True, quality=95)  # Keep quality high if under limit
        else:
            # Reduce the image size while maintaining proportions
            width, height = img.size
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.save(output_path, optimize=True, quality=85)

        # Check size and ensure it's under the max size
        while os.path.getsize(output_path) / (1024 * 1024) > max_size_mb:
            # Continue reducing the image until it's under the desired size
            width, height = img.size
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.save(output_path, optimize=True, quality=85)

def process_images(brut_folder, compressed_folder, name_prefix):
    if not os.path.exists(compressed_folder):
        os.makedirs(compressed_folder)
    
    # Process each image in the brut files folder
    for idx, filename in enumerate(os.listdir(brut_folder), 1):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(brut_folder, filename)
            output_filename = f"{name_prefix}{idx}.png"  # Create the new name
            output_path = os.path.join(compressed_folder, output_filename)

            print(f"Compressing {filename} -> {output_filename}")
            compress_image(input_path, output_path)

if __name__ == "__main__":
    brut_folder = 'brut_files'  # Change to the path of your brut folder
    compressed_folder = 'compressed_files'  # Change to your desired output folder
    process_images(brut_folder, compressed_folder, "wedding_pic_")
