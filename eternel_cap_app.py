from tkinter import Tk, Label, Button, Radiobutton, StringVar, Frame, Entry, filedialog, messagebox, ttk, filedialog
import tkinter as tk
import os
from PIL import Image
import re

# ----------------------- Directory window ------------------------------------
def custom_select_folder(initial_dir, title, geometry):
    match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", geometry)
    if match:
        width_g, height_g, pos_x, pos_y = map(int, match.groups())  
    else:
        width_g, height_g, pos_x, pos_y = None, None, None, None

    width_w = 500
    height_w = 400

    def populate_treeview(parent_path, parent_node):
        """Populate the treeview with directories."""
        for entry in os.listdir(parent_path):
            full_path = os.path.join(parent_path, entry)
            if os.path.isdir(full_path):  # Only add directories
                node = tree.insert(parent_node, "end", text=entry, values=[full_path])
                tree.insert(node, "end")  # Add a dummy child to make it expandable

    def update_treeview(event):
        """Update the treeview when a node is expanded."""
        node = tree.focus()
        if tree.get_children(node):  # If already populated, skip
            return
        parent_path = tree.item(node, "values")[0]
        tree.delete(*tree.get_children(node))  # Clear dummy child
        populate_treeview(parent_path, node)

    def select_folder():
        """Handle folder selection and close the dialog."""
        selected_item = tree.focus()
        selected_folder = tree.item(selected_item, "values")[0] if selected_item else ""
        result_var.set(selected_folder)
        custom_dialog.destroy()
    
    custom_dialog = tk.Toplevel()

    custom_dialog.geometry(str(width_w)+"x"+str(height_w)+"+"+str(int(pos_x+width_g/2-width_w/2))+"+"+str(int(pos_y+height_g/2-height_w/2)))  # Set the desired window geometry
    custom_dialog.title(title)

    # Create a StringVar to hold the selected folder path
    result_var = tk.StringVar()

    # Create a frame for the Treeview and Scrollbar
    frame = ttk.Frame(custom_dialog, padding="10")
    frame.pack(fill="both", expand=True)

    # Treeview for directory selection
    tree = ttk.Treeview(frame, columns=("full_path",), show="tree")
    tree.heading("#0", text="Folder Name")
    tree.heading("full_path", text="Full Path")
    tree.bind("<<TreeviewOpen>>", update_treeview)

    # Scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Populate the Treeview with the initial directory
    root_node = tree.insert("", "end", text=initial_dir, values=[initial_dir])
    populate_treeview(initial_dir, root_node)
    tree.item(root_node, open=True)

    # Confirm button
    confirm_button = ttk.Button(custom_dialog, text="Select", command=select_folder)
    confirm_button.pack(pady=10)

    # Wait for the dialog to close
    custom_dialog.wait_window()

    return result_var.get()  # Return the selected folder

# ----------------------- Compression functions -------------------------------
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

    show_custom_message(bar_title="C'est fait !", geometry=current_geometry,message_text="Compression terminée :D")

def open_compression_window():
    save_geometry(root)
    root.withdraw()
    compression_window = Tk()
    compression_window.title("Compression de photos")
    apply_geometry(compression_window)
    compression_window.deiconify()


    # Create a frame for layout
    frame = Frame(compression_window)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Compression
    Label(frame, text="Interface de compression de photos").pack(pady=(0, 10))  

    # Nom de fichier apres compression
    Label(frame, text="Nom de fichiers après compression:").pack(anchor="w")  # Align to the left within the frame
    
    name_entry = Entry(frame)
    name_entry.insert(0, "ex: Photo_compress_") 
    name_entry.config(fg='gray')
    name_entry.pack(fill="x", pady=5)  

    def on_click(event): # Function to clear placeholder text when the user starts typing
        if name_entry.get() == "ex: Photo_compress_":
            name_entry.delete(0, "end")
            name_entry.config(fg='black')

    def on_focus_out(event):   # Function to restore placeholder if nothing is entered
        if not name_entry.get():
            name_entry.insert(0, "ex: Photo_compress_")
            name_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown

    # Bind events to Entry widget
    name_entry.bind("<FocusIn>", on_click)  # When Entry is clicked, remove placeholder
    name_entry.bind("<FocusOut>", on_focus_out)  # When Entry loses focus, restore placeholder if empty
    
    # chemin pour dossier de photos a compresser
    Label(frame, text="Selectionne le dossier contenant les images à compresser:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    folder_frame = Frame(frame)
    folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    brut_folder_entry = Entry(folder_frame)
    brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/images/brut") 
    brut_folder_entry.config(fg='gray', width=50)  # Set width if needed
    brut_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder(event): # Function to clear placeholder text when the user starts typing
        if brut_folder_entry.get() == "ex: Chemin/pour/dossier/images/brut":
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.config(fg='black')

    def on_focus_out_folder(event):   # Function to restore placeholder if nothing is entered
        if not brut_folder_entry.get():
            brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/images/brut")
            brut_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    brut_folder_entry.bind("<FocusIn>", on_click_folder)  # When Entry is clicked, remove placeholder
    brut_folder_entry.bind("<FocusOut>", on_focus_out_folder)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder():
        save_geometry(compression_window)
        brut_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier contenant les photos à compresser",geometry=current_geometry)
        # brut_folder = filedialog.askdirectory(title="Select Brut Files Folder",initialdir=os.getcwd())
        if brut_folder:  # Only update if a folder was selected
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.insert(0, brut_folder)
            brut_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button = Button(folder_frame, text="Parcourir", command=select_folder)
    Parcourir_button.pack(side="left")
    


    # chemin pour dossier de photos compressées
    Label(frame, text="Selectionne le dossier pour déposer les photos compressées:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    compressed_folder_frame = Frame(frame)
    compressed_folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    compress_folder_entry = Entry(compressed_folder_frame)
    compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/images/brut") 
    compress_folder_entry.config(fg='gray', width=50)  # Set width if needed
    compress_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder_compress(event): # Function to clear placeholder text when the user starts typing
        if compress_folder_entry.get() == "ex: Chemin/pour/dossier/images/brut":
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.config(fg='black')

    def on_focus_out_folder_compress(event):   # Function to restore placeholder if nothing is entered
        if not compress_folder_entry.get():
            compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/images/brut")
            compress_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    compress_folder_entry.bind("<FocusIn>", on_click_folder_compress)  # When Entry is clicked, remove placeholder
    compress_folder_entry.bind("<FocusOut>", on_focus_out_folder_compress)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder_compress():
        save_geometry(compression_window)
        compress_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier pour déposer les photos compressées",geometry=current_geometry)
        # compress_folder= filedialog.askdirectory(title="Select Compressed Files Folder",initialdir=os.getcwd())
        if compress_folder_entry:  # Only update if a folder was selected
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.insert(0, compress_folder)
            compress_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button_compress = Button(compressed_folder_frame, text="Parcourir", command=select_folder_compress)
    Parcourir_button_compress.pack(side="left")

    def go_back(): # Fonction de retour à la fenêtre principale
        save_geometry(root)
        compression_window.withdraw()
        apply_geometry(root)
        root.deiconify()

    # Frame for buttons
    button_frame = Frame(compression_window)
    button_frame.pack(side="bottom", pady=10)  # Place buttons at the bottom with padding

    def run_compression():
        name_prefix = name_entry.get()
        brut_folder = brut_folder_entry.get()   
        compress_folder = compress_folder_entry.get()   
        process_images(brut_folder, compress_folder, name_prefix)
        compression_window.destroy()
        root.deiconify()

    # Boutons Précédent et Compress
    previous_button = Button(button_frame, text="Précédent", state="normal", command=go_back, width=10, height=1)
    previous_button.pack(side="left", padx=(window_width-240, 10))  

    run_button = Button(button_frame, text="Compresser", state="normal", command=run_compression, width=10, height=1)
    run_button.pack(side="left", padx=(0,10))

    compression_window.mainloop()

# ----------------------- Function to handle Enter key press -------------------

def on_enter_key(event): 
    if next_button["state"] == "normal":  # Only trigger if the button is enabled
        next_button.invoke()  # Simulate button click

# ----------------------- Signature functions ---------------------------------

def adjust_opacity(logo, opacity):
    # Adjust the logo's opacity by modifying its alpha channel
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # Split the logo into individual channels
    r, g, b, a = logo.split()

    # Adjust the alpha channel (opacity)
    a = a.point(lambda p: p * opacity // 100)  # opacity is in percentage (0-100)

    # Recombine the channels back with the new alpha channel
    logo = Image.merge('RGBA', (r, g, b, a))
    return logo

def add_logo_to_image(image_path, logo_path, output_path, opacity=80):
    # Open the main image and logo
    img = Image.open(image_path)
    logo = Image.open(logo_path)

    # Adjust the logo opacity
    logo = adjust_opacity(logo, opacity)

    # Get dimensions of the image
    img_width, img_height = img.size
    logo_width, logo_height = logo.size

    # Check if the image is portrait or landscape
    if img_width > img_height:
        # Landscape (paysage)
        grid_columns = 7
        grid_lines = 13
        pos_x = img_width - (img_width // grid_columns)  
        pos_y = img_height - (img_height // grid_lines)  

        # Resize the logo to fit proportionally in the image
        max_logo_width = img_width // 8  
        max_logo_height = img_height // 8  
        logo.thumbnail((max_logo_width, max_logo_height))

    else:
        # Portrait
        grid_columns = 5
        grid_lines = 20
        pos_x = img_width - (img_width // grid_columns) 
        pos_y = img_height - (img_height // grid_lines)  

        # Resize the logo to fit proportionally in the image
        max_logo_width = img_width // 5  
        max_logo_height = img_height // 5  
        logo.thumbnail((max_logo_width, max_logo_height))

    # Position the logo in the bottom left corner
    img.paste(logo, (pos_x, pos_y), logo.convert("RGBA").split()[3])  # Use alpha for transparency

    # Save the resulting image
    img.save(output_path)

def open_logo_window():
    save_geometry(root)
    root.withdraw()
    logo_window = Tk()
    logo_window.title("Signature des photos")
    apply_geometry(logo_window)
    logo_window.deiconify()

    # Create a frame for layout
    frame = Frame(logo_window)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Signature
    Label(frame, text="Interface d'ajout de signature").pack(pady=(0, 10))  

    # chemin pour dossier de photos a signer
    Label(frame, text="Selectionne le dossier contenant les photos à signer:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    folder_frame = Frame(frame)
    folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    brut_folder_entry = Entry(folder_frame)
    brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut") 
    brut_folder_entry.config(fg='gray', width=50)  # Set width if needed
    brut_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder(event): # Function to clear placeholder text when the user starts typing
        if brut_folder_entry.get() == "ex: Chemin/pour/dossier/photos/brut":
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.config(fg='black')

    def on_focus_out_folder(event):   # Function to restore placeholder if nothing is entered
        if not brut_folder_entry.get():
            brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut")
            brut_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    brut_folder_entry.bind("<FocusIn>", on_click_folder)  # When Entry is clicked, remove placeholder
    brut_folder_entry.bind("<FocusOut>", on_focus_out_folder)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder():
        # -------------
        save_geometry(logo_window)
        compress_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier contenant les photos à signer",geometry=current_geometry)
        if compress_folder:  # Only update if a folder was selected
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.insert(0, compress_folder)
            brut_folder_entry.config(fg='black')  # Change text color to black
        # -------------
        # brut_folder = filedialog.askdirectory(title="Dossier contenant les photos à signer",initialdir=os.getcwd())
        # if brut_folder:  # Only update if a folder was selected
        #     brut_folder_entry.delete(0, "end")
        #     brut_folder_entry.insert(0, brut_folder)
        #     brut_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button = Button(folder_frame, text="Parcourir", command=select_folder)
    Parcourir_button.pack(side="left")
    


    # chemin pour dossier de photos signées
    Label(frame, text="Selectionne le dossier pour déposer les photos signées:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    compressed_folder_frame = Frame(frame)
    compressed_folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    compress_folder_entry = Entry(compressed_folder_frame)
    compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut") 
    compress_folder_entry.config(fg='gray', width=50)  # Set width if needed
    compress_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder_compress(event): # Function to clear placeholder text when the user starts typing
        if compress_folder_entry.get() == "ex: Chemin/pour/dossier/photos/brut":
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.config(fg='black')

    def on_focus_out_folder_compress(event):   # Function to restore placeholder if nothing is entered
        if not compress_folder_entry.get():
            compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut")
            compress_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    compress_folder_entry.bind("<FocusIn>", on_click_folder_compress)  # When Entry is clicked, remove placeholder
    compress_folder_entry.bind("<FocusOut>", on_focus_out_folder_compress)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder_compress():
        save_geometry(logo_window)
        compress_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier de dépot de photos signées",geometry=current_geometry)
        # compress_folder= filedialog.askdirectory(title="Dossier de dépot de photos signées",initialdir=os.getcwd())
        if compress_folder_entry:  # Only update if a folder was selected
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.insert(0, compress_folder)
            compress_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button_compress = Button(compressed_folder_frame, text="Parcourir", command=select_folder_compress)
    Parcourir_button_compress.pack(side="left")

    def go_back(): # Fonction de retour à la fenêtre principale
        save_geometry(root)
        logo_window.withdraw()
        apply_geometry(root)
        root.deiconify()

    # Frame for buttons
    button_frame = Frame(logo_window)
    button_frame.pack(side="bottom", pady=10)  # Place buttons at the bottom with padding


    def add_logo_to_folder():    
        folder_path = brut_folder_entry.get() 
        output_folder = compress_folder_entry.get() 
        logo_path = 'logos/ec_nb.png'

        # List files in the folder and filter for images
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_files = len(image_files)
        
        # Create a progress bar window
        save_geometry(logo_window)
        progress_window = Tk()
        progress_window.title("Processing...")
        apply_geometry(progress_window)
        progress_window.deiconify()

        ttk.Label(progress_window, text="Signature de photos, veillez attendre...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate', maximum=total_files)
        progress_bar.pack(pady=20)
        progress_window.update()

        for i, file_name in enumerate(image_files, start=1):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(folder_path, file_name)
                output_path = os.path.join(output_folder, file_name)
                add_logo_to_image(image_path, logo_path, output_path)  
            
            # Update the progress bar
            progress_bar['value'] = i
            progress_window.update_idletasks()
        
        progress_window.destroy()  
        show_custom_message(bar_title="C'est fait !", geometry=current_geometry,message_text="Dignature terminée :D")

        logo_window.destroy()
        root.deiconify()

    # Boutons Précédent et Signer
    previous_button = Button(button_frame, text="Précédent", state="normal", command=go_back, width=10, height=1)
    previous_button.pack(side="left", padx=(window_width-240, 10))  

    run_button = Button(button_frame, text="Signer", state="normal", command=add_logo_to_folder, width=10, height=1)
    run_button.pack(side="left", padx=(0,10))

    logo_window.mainloop()

# ----------------------- Filigrane functions ----------------------------------

def add_filigrane_to_image(image_path, logo_path, output_path, opacity=50):
    # Open the main image and logo
    img = Image.open(image_path)
    logo = Image.open(logo_path)

    # Adjust the logo opacity
    logo = adjust_opacity(logo, opacity)

    # Get dimensions of the image
    img_width, img_height = img.size

     # Resize the logo to be 75% of the image's width
    max_logo_width = int(img_width * 0.75)
    logo_ratio = logo.height / logo.width
    max_logo_height = int(max_logo_width * logo_ratio)
    logo = logo.resize((max_logo_width, max_logo_height), Image.Resampling.LANCZOS)

    # Calculate the position to center the logo
    logo_width, logo_height = logo.size
    pos_x = (img_width - logo_width) // 2
    pos_y = (img_height - logo_height) // 2

    # Paste the logo in the center using its alpha channel for transparency
    img.paste(logo, (pos_x, pos_y), logo.convert("RGBA").split()[3])

    # Save the resulting image
    img.save(output_path)

def open_watermark_window():
    save_geometry(root)
    root.withdraw()
    watermark_window = Tk()
    watermark_window.title("Ajouter un filigrane")
    apply_geometry(watermark_window)
    watermark_window.deiconify()

    # Create a frame for layout
    frame = Frame(watermark_window)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # filigrane
    Label(frame, text="Interface d'ajout de filigrane").pack(pady=(0, 10))  

    # chemin pour dossier de photos a filigraner 
    Label(frame, text="Selectionne le dossier contenant les photos à filigraner:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    folder_frame = Frame(frame)
    folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    brut_folder_entry = Entry(folder_frame)
    brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut") 
    brut_folder_entry.config(fg='gray', width=50)  # Set width if needed
    brut_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder(event): # Function to clear placeholder text when the user starts typing
        if brut_folder_entry.get() == "ex: Chemin/pour/dossier/photos/brut":
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.config(fg='black')

    def on_focus_out_folder(event):   # Function to restore placeholder if nothing is entered
        if not brut_folder_entry.get():
            brut_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut")
            brut_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    brut_folder_entry.bind("<FocusIn>", on_click_folder)  # When Entry is clicked, remove placeholder
    brut_folder_entry.bind("<FocusOut>", on_focus_out_folder)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder():
        save_geometry(watermark_window)
        brut_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier contenant les photos à filigraner",geometry=current_geometry)
        # brut_folder = filedialog.askdirectory(title="Dossier contenant les photos à filigraner",initialdir=os.getcwd())
        if brut_folder:  # Only update if a folder was selected
            brut_folder_entry.delete(0, "end")
            brut_folder_entry.insert(0, brut_folder)
            brut_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button = Button(folder_frame, text="Parcourir", command=select_folder)
    Parcourir_button.pack(side="left")
    


    # chemin pour dossier de photos signées
    Label(frame, text="Selectionne le dossier pour déposer les photos filigranées:").pack(anchor="w")  # Align to the left within the frame
    # Create a horizontal frame to hold the Entry and Button
    compressed_folder_frame = Frame(frame)
    compressed_folder_frame.pack(fill="x", pady=5)

    # Entry for the folder path
    compress_folder_entry = Entry(compressed_folder_frame)
    compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut") 
    compress_folder_entry.config(fg='gray', width=50)  # Set width if needed
    compress_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))  # Allow Entry to expand

    def on_click_folder_compress(event): # Function to clear placeholder text when the user starts typing
        if compress_folder_entry.get() == "ex: Chemin/pour/dossier/photos/brut":
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.config(fg='black')

    def on_focus_out_folder_compress(event):   # Function to restore placeholder if nothing is entered
        if not compress_folder_entry.get():
            compress_folder_entry.insert(0, "ex: Chemin/pour/dossier/photos/brut")
            compress_folder_entry.config(fg='gray')  # Optional: Change text color to gray when placeholder is shown
    
    compress_folder_entry.bind("<FocusIn>", on_click_folder_compress)  # When Entry is clicked, remove placeholder
    compress_folder_entry.bind("<FocusOut>", on_focus_out_folder_compress)  # When Entry loses focus, restore placeholder if empty

    # Function to open the file dialog and update the Entry
    def select_folder_compress():
        save_geometry(watermark_window)
        compress_folder = custom_select_folder(initial_dir=os.getcwd(), title="Dossier de dépot de photos filigranées",geometry=current_geometry)
        # compress_folder= filedialog.askdirectory(title="Dossier de dépot de photos filigranées",initialdir=os.getcwd())
        if compress_folder_entry:  # Only update if a folder was selected
            compress_folder_entry.delete(0, "end")
            compress_folder_entry.insert(0, compress_folder)
            compress_folder_entry.config(fg='black')  # Change text color to black

    # Button to launch the folder selection
    Parcourir_button_compress = Button(compressed_folder_frame, text="Parcourir", command=select_folder_compress)
    Parcourir_button_compress.pack(side="left")

    def go_back(): # Fonction de retour à la fenêtre principale
        save_geometry(root)
        watermark_window.withdraw()
        apply_geometry(root)
        root.deiconify()

    # Frame for buttons
    button_frame = Frame(watermark_window)
    button_frame.pack(side="bottom", pady=10)  # Place buttons at the bottom with padding


    def add_filigrane_to_folder():    
        folder_path = brut_folder_entry.get() 
        output_folder = compress_folder_entry.get() 
        logo_path = 'logos/ec_nb.png'

        # List files in the folder and filter for images
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_files = len(image_files)
        
        # Create a progress bar window
        save_geometry(watermark_window)
        progress_window = Tk()
        progress_window.title("Processing...")
        apply_geometry(progress_window)
        progress_window.deiconify()

        ttk.Label(progress_window, text="Filigrane de photos, veillez attendre...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate', maximum=total_files)
        progress_bar.pack(pady=20)
        progress_window.update()




        for i, file_name in enumerate(image_files, start=1):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(folder_path, file_name)
                output_path = os.path.join(output_folder, file_name)
                add_filigrane_to_image(image_path, logo_path, output_path)

            # Update the progress bar
            progress_bar['value'] = i
            progress_window.update_idletasks()


        progress_window.destroy()  # Close the progress window
        current_geometry

        show_custom_message(bar_title="C'est fait !", geometry=current_geometry,message_text="Filigrane terminée :D")
        watermark_window.destroy()
        root.deiconify()


    # Boutons Précédent et Signer
    previous_button = Button(button_frame, text="Précédent", state="normal", command=go_back, width=10, height=1)
    previous_button.pack(side="left", padx=(window_width-240, 10))  

    run_button = Button(button_frame, text="Filigraner", state="normal", command=add_filigrane_to_folder, width=10, height=1)
    run_button.pack(side="left", padx=(0,10))

    watermark_window.mainloop()

# ----------------------- Window Geometry -------------------------------------
# Global variable to store the current window's geometry

def save_geometry(window):
    """Save the current geometry of the window."""
    global current_geometry
    current_geometry = window.geometry()

def apply_geometry(window):
    """Apply the saved geometry to the window."""
    window.geometry(current_geometry)


# ----------------------- Custom message --------------------------------------
def show_custom_message(bar_title, geometry,message_text):
    match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", geometry)
    if match:
        width_g, height_g, pos_x, pos_y = map(int, match.groups())  
    else:
        width_g, height_g, pos_x, pos_y = None, None, None, None

    width_w = 400
    height_w = 100

    # Create a new window for the message
    message_window = Tk()
    message_window.title(bar_title)
    message_window.geometry(str(width_w)+"x"+str(height_w)+"+"+str(int(pos_x+width_g/2-width_w/2))+"+"+str(int(pos_y+height_g/2-height_w/2)))  
    message_window.grab_set()  # Disable interactions with other windows
    
    ttk.Label(message_window, text=message_text).pack(pady=10)
    ttk.Button(message_window, text="Retour au menu principal", command=message_window.destroy).pack(pady=10)
    
    # Wait for this window to close before continuing
    message_window.wait_window()

    # Ensure focus returns to the root window
    root.deiconify()
    root.lift()  # Bring root to the foreground


# -----------------------------------------------------------------------------
# ----------------------- Debut de l'application ------------------------------
# -----------------------------------------------------------------------------
window_width = 600
window_height = 300
current_geometry = str(window_width)+"x"+str(window_height)+"+200+100"


# Créer la fenêtre principale
root = Tk()
root.title("Eternel Capture")
root.geometry(current_geometry)



# Variable pour enregistrer le choix de l'utilisateur
selected_option = StringVar()
selected_option.set("none")  # Initialisation avec aucune option sélectionnée

# Ajouter les boutons radio pour les choix
Label(root, text="Choisissez une option :").pack(pady=10)

Radiobutton(root, text="Compresser des photos", variable=selected_option, value="compression").pack(anchor="w")
Radiobutton(root, text="Ajouter une signature", variable=selected_option, value="logo").pack(anchor="w")
Radiobutton(root, text="Ajouter un filigrane", variable=selected_option, value="watermark").pack(anchor="w")

# Fonction pour passer à la fenêtre suivante selon le choix
def next_window():
    choice = selected_option.get()
    if choice == "compression":
        open_compression_window()
    elif choice == "logo":
        open_logo_window()
    elif choice == "watermark":
        open_watermark_window()

# Fonction pour activer/désactiver le bouton Next
def update_buttons_state():
    if selected_option.get() == "none":
        next_button.config(state="disabled")
    else:
        next_button.config(state="normal")

# Appeler update_buttons_state à chaque changement de choix
selected_option.trace_add("write", lambda *args: update_buttons_state())

# Boutons Précédent et Next
frame_buttons = Frame(root)
frame_buttons.pack(side="bottom", pady=10)

next_button = Button(frame_buttons, text="Suivant", state="disabled", command=next_window, width=10, height=1)
next_button.pack(side="right", padx=(window_width-200, 10))  

root.bind("<Return>", on_enter_key)  # Binds the Enter key globally to the main window

# Démarrer la boucle principale
root.mainloop()
