import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
import os
import threading
import time
import subprocess

class VideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Generator")
        self.root.state('zoomed')  # Start maximized
        self.image_entries = []
        self.audio_path = None

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Select Images and Duration for Each").pack(pady=10)

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.add_image_entry()

        tk.Button(self.root, text="Add Another Image", command=self.add_image_entry).pack(pady=5)

        tk.Label(self.root, text="Select Audio File:").pack(pady=5)
        self.audio_button = tk.Button(self.root, text="Browse", command=self.select_audio)
        self.audio_button.pack(pady=5)

        self.selected_audio_label = tk.Label(self.root, text="No audio file selected")
        self.selected_audio_label.pack(pady=5)

        tk.Label(self.root, text="Audio Start Delay (seconds):").pack(pady=5)
        self.audio_start_delay_entry = tk.Entry(self.root)
        self.audio_start_delay_entry.pack(pady=5)

        tk.Label(self.root, text="Audio End Blank Duration (seconds):").pack(pady=5)
        self.audio_end_blank_entry = tk.Entry(self.root)
        self.audio_end_blank_entry.pack(pady=5)

        tk.Button(self.root, text="Generate Video", command=self.generate_video).pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def add_image_entry(self):
        entry_frame = tk.Frame(self.frame)
        entry_frame.pack(pady=5)

        img_label = tk.Label(entry_frame, text="Select Image(s):")
        img_label.pack(side=tk.LEFT)

        img_button = tk.Button(entry_frame, text="Browse", command=lambda: self.select_images(img_button))
        img_button.pack(side=tk.LEFT)

        duration_label = tk.Label(entry_frame, text="Duration (seconds):")
        duration_label.pack(side=tk.LEFT)

        duration_entry = tk.Entry(entry_frame)
        duration_entry.insert(0, '0')  # Set default value to 0
        duration_entry.pack(side=tk.LEFT)

        self.image_entries.append((img_button, duration_entry))

    def select_images(self, img_button):
        img_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if img_paths:
            img_button.config(text=", ".join([os.path.abspath(path) for path in img_paths]))

    def select_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if self.audio_path:
            self.audio_button.config(text="Change Audio File")
            self.selected_audio_label.config(text=f"Selected Audio: {os.path.basename(self.audio_path)}")

    def generate_video(self):
        image_paths = []
        durations = []

        for button, entry in self.image_entries:
            img_paths = button.cget("text").split(", ")
            duration_str = entry.get()

            for img_path in img_paths:
                if img_path and duration_str:
                    if not os.path.isfile(img_path):
                        messagebox.showerror("File Error", f"File not found: {img_path}")
                        return
                    try:
                        duration = float(duration_str)
                        if duration < 0:
                            raise ValueError
                        image_paths.append(img_path)
                        durations.append(duration)
                    except ValueError:
                        messagebox.showerror("Input Error", "Please enter a valid duration (0 or greater).")
                        return

        if not image_paths:
            messagebox.showwarning("No Images", "No images selected.")
            return

        if not self.audio_path:
            messagebox.showwarning("No Audio", "No audio file selected.")
            return

        audio_start_delay_str = self.audio_start_delay_entry.get()
        audio_end_blank_str = self.audio_end_blank_entry.get()

        try:
            audio_start_delay = float(audio_start_delay_str)
            audio_end_blank = float(audio_end_blank_str)
            if audio_start_delay < 0 or audio_end_blank < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid non-negative numbers for audio delay and end blank.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                   filetypes=[("MP4 files", "*.mp4")],
                                                   title="Save Video As")
        if not output_path:
            return

        threading.Thread(target=self.create_video, args=(output_path, image_paths, durations, audio_start_delay, audio_end_blank)).start()

    def create_video(self, output_path, image_paths, durations, audio_start_delay, audio_end_blank):
        clips = []

        try:
            audio = AudioFileClip(self.audio_path)
        except Exception as e:
            self.show_error("Audio Error", f"Error loading audio file {self.audio_path}: {e}")
            return

        audio_duration = audio.duration

        if all(duration == 0 for duration in durations):
            # Case 1: Automatic Duration Adjustment
            total_duration = audio_start_delay + audio_duration + audio_end_blank
            for img_path in image_paths:
                try:
                    image_clip = ImageClip(img_path).set_duration(total_duration / len(image_paths))
                    clips.append(image_clip)
                except Exception as e:
                    self.show_error("Image Error", f"Error loading image {img_path}: {e}")
                    return

        else:
            # Case 2: User-Defined Duration
            for img_path, duration in zip(image_paths, durations):
                if duration == 0:
                    duration = audio_duration
                try:
                    image_clip = ImageClip(img_path).set_duration(duration)
                    clips.append(image_clip)
                except Exception as e:
                    self.show_error("Image Error", f"Error loading image {img_path}: {e}")
                    return

            if clips:
                total_clips_duration = sum(clip.duration for clip in clips)
                if total_clips_duration < audio_duration + audio_start_delay + audio_end_blank:
                    # Extend the last clip to the end of the video
                    last_clip = clips[-1]
                    last_clip_duration = audio_duration + audio_start_delay + audio_end_blank - total_clips_duration
                    last_clip = last_clip.set_duration(last_clip_duration)
                    clips[-1] = last_clip

        if not clips:
            self.show_warning("No Valid Clips", "No valid clips were created.")
            return

        video = concatenate_videoclips(clips)

        # Handling silence and audio
        silence_clip = AudioFileClip("media/silence.mp3")
        silence_start = silence_clip.subclip(0, audio_start_delay) if audio_start_delay > 0 else None
        silence_end = silence_clip.subclip(0, audio_end_blank) if audio_end_blank > 0 else None
        
        audio_segments = [clip for clip in [silence_start, audio, silence_end] if clip]
        final_audio = concatenate_audioclips(audio_segments)

        final_video = video.set_audio(final_audio)

        # Update progress bar
        for i in range(101):
            time.sleep(0.05)
            self.update_progress(i)

        # Write video file
        final_video.write_videofile(output_path, fps=24)
        self.update_progress(100)
        self.show_success(f"Video created successfully!\nVideo path: {output_path}")
        self.open_video(output_path)

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress.config(value=value))

    def show_success(self, message):
        self.root.after(0, lambda: messagebox.showinfo("Success", message))

    def show_warning(self, title, message):
        self.root.after(0, lambda: messagebox.showwarning(title, message))

    def show_error(self, title, message):
        self.root.after(0, lambda: messagebox.showerror(title, message))

    def open_video(self, output_path):
        try:
            if os.name == 'nt':
                os.startfile(output_path)
            elif os.name == 'posix':
                subprocess.call(('xdg-open' if os.uname().sysname == 'Linux' else 'open', output_path))
        except Exception as e:
            self.show_error("Open File Error", f"An error occurred while trying to open the video: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoGeneratorApp(root)
    root.mainloop()
