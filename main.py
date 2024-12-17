import os
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

# 

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
    

if __name__ == "__main__":
    brut_folder = 'brut_files'  # Change to the path of your brut folder
    compressed_folder = 'compressed_files'  # Change to your desired output folder
    process_images(brut_folder, compressed_folder, "wedding_pic_")
