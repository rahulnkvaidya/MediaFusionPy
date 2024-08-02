import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import sys

def open_video_page():
    subprocess.Popen([sys.executable, "video.py"])

def open_imageresize_page():
    subprocess.Popen([sys.executable, "imageresize.py"])

def quit_app():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("MediaFusionPy")
root.state('zoomed')  # Start maximized

# Create a frame for the buttons
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

# Create buttons for each feature
btn_video_page = tk.Button(frame, text="Video Page", command=open_video_page, width=25, height=2)
btn_video_page.grid(row=0, column=0, padx=10, pady=10)

btn_imageresize_page = tk.Button(frame, text="Image Resize Page", command=open_imageresize_page, width=25, height=2)
btn_imageresize_page.grid(row=0, column=1, padx=10, pady=10)

# Quit button
btn_quit = tk.Button(frame, text="Quit", command=quit_app, width=25, height=2)
btn_quit.grid(row=1, column=0, columnspan=2, pady=10)

# Create a menu bar
menu_bar = tk.Menu(root)

# Create a 'File' menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Video Page", command=open_video_page)
file_menu.add_command(label="Image Resize Page", command=open_imageresize_page)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_app)
menu_bar.add_cascade(label="File", menu=file_menu)

# Set the menu bar to the root window
root.config(menu=menu_bar)

# Start the Tkinter event loop
root.mainloop()
