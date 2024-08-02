import os
import subprocess
from tkinter import Tk, filedialog, Menu, Label, Button, Canvas, NW, messagebox
from PIL import Image, ImageTk

def resize_image(image_path, output_path, size=(1280, 720)):
    with Image.open(image_path) as img:
        img.thumbnail(size, Image.LANCZOS)
        background = Image.new('RGB', size, (255, 255, 255))
        offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
        background.paste(img, offset)
        background.save(output_path)

def show_thumbnails(file_paths, canvas, thumb_size=(150, 150)):
    canvas.delete("all")  # Clear the canvas before displaying new thumbnails
    for idx, file_path in enumerate(file_paths):
        with Image.open(file_path) as img:
            img.thumbnail(thumb_size)
            thumb = ImageTk.PhotoImage(img)
            canvas.create_image(10, 10 + idx * (thumb_size[1] + 10), anchor=NW, image=thumb)
            # Keep a reference to prevent garbage collection
            canvas.image = thumb
            canvas.images.append(thumb)

def open_output_folder(output_folder):
    if os.name == 'nt':  # Windows
        os.startfile(output_folder)
    elif os.name == 'posix':  # macOS or Linux
        subprocess.run(['open', output_folder])

def create_menu(root):
    menu = Menu(root)
    root.config(menu=menu)

    script_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Scripts", menu=script_menu)
    script_menu.add_command(label="Home", command=lambda: subprocess.run(['python', 'main.py']))
    script_menu.add_command(label="Video", command=lambda: subprocess.run(['python', 'video.py']))
    script_menu.add_command(label="Image", command=lambda: subprocess.run(['python', 'image.py']))
    script_menu.add_command(label="Chat", command=lambda: subprocess.run(['python', 'chat.py']))
    script_menu.add_command(label="TImage", command=lambda: subprocess.run(['python', 'timage.py']))

def select_images(canvas, file_paths):
    Tk().withdraw()  # Hide the root window
    paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])

    if not paths:
        messagebox.showinfo("No Selection", "No images selected.")
        return

    file_paths.clear()
    file_paths.extend(paths)
    show_thumbnails(file_paths, canvas)

def resize_selected_images(file_paths):
    if not file_paths:
        messagebox.showwarning("No Images", "No images selected for resizing.")
        return

    output_folder = "resized_images"
    os.makedirs(output_folder, exist_ok=True)

    for idx, file_path in enumerate(file_paths):
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        new_file_name = f"image_{idx + 1}{ext}"
        output_path = os.path.join(output_folder, new_file_name)

        resize_image(file_path, output_path)
        print(f"Saved resized image to: {output_path}")

    messagebox.showinfo("Success", f"Images have been resized and saved to {output_folder}.")
    open_output_folder(output_folder)

def main():
    root = Tk()
    root.title("Image Resizer")
    root.state('zoomed')  # Start maximized

    create_menu(root)

    canvas = Canvas(root, width=200, height=500)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.images = []

    file_paths = []

    Button(root, text="Select Images", command=lambda: select_images(canvas, file_paths)).pack()
    Button(root, text="Submit", command=lambda: resize_selected_images(file_paths)).pack()
    Button(root, text="Open Output Folder", command=lambda: open_output_folder("resized_images")).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
