import customtkinter as ctk
import pygame
import json
import os
from tkinter import filedialog, colorchooser, messagebox

# --- Configuration Constants ---
CONFIG_FILE = "config.json"
DEFAULT_SETTINGS = {
    "theme": "dark",
    "accent_color": "blue",
    "columns": 4,
    "button_size": 120,
    "font_size": 12,
    "sounds": []
}

class SoundButton(ctk.CTkButton):
    """Custom component representing a single sound trigger."""
    def __init__(self, master, sound_data, play_command, edit_command, **kwargs):
        self.data = sound_data # Stores path, title, color, shape
        
        # Apply custom styling based on sound_data
        shape_corner = 20 if sound_data.get("shape") == "Round" else 2
        
        super().__init__(
            master, 
            text=sound_data["title"],
            fg_color=sound_data.get("color", "#1f538d"),
            corner_radius=shape_corner,
            command=lambda: play_command(sound_data["path"]),
            **kwargs
        )
        
        # Right-click for Edit Mode
        self.bind("<Button-3>", lambda e: edit_command(self))

class SoundboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Initialize Audio Engine
        pygame.mixer.init()

        # 2. Load Persistence Data
        self.config = self.load_config()

        # 3. Setup Window
        self.title("Pythonic Soundboard")
        self.geometry("1000x700")
        ctk.set_appearance_mode(self.config["theme"])
        ctk.set_default_color_theme(self.config["accent_color"])

        # 4. State Variables
        self.edit_mode = ctk.BooleanVar(value=False)
        self.sound_widgets = []

        # 5. Build UI
        self.setup_ui()
        self.refresh_grid()

    def setup_ui(self):
        """Creates the sidebar and the main scrollable sound area."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="SOUNDBOARD", font=("Roboto", 20, "bold")).pack(pady=20)

        # Add Sound Button
        self.add_btn = ctk.CTkButton(self.sidebar, text="+ Add Sound", command=self.add_sound_dialog)
        self.add_btn.pack(pady=10, padx=20)

        # Settings Dividers
        ctk.CTkLabel(self.sidebar, text="Grid Settings", font=("Roboto", 12, "bold")).pack(pady=(20, 5))
        
        # Columns Slider
        self.col_slider = ctk.CTkSlider(self.sidebar, from_=2, to=8, number_of_steps=6, command=self.update_grid_config)
        self.col_slider.set(self.config["columns"])
        self.col_slider.pack(padx=20)
        
        # Edit Mode Toggle
        self.edit_switch = ctk.CTkSwitch(self.sidebar, text="Edit Mode", variable=self.edit_mode)
        self.edit_switch.pack(pady=20)

        # Theme Toggle
        self.theme_btn = ctk.CTkButton(self.sidebar, text="Toggle Light/Dark", fg_color="transparent", border_width=1, command=self.toggle_theme)
        self.theme_btn.pack(side="bottom", pady=20, padx=20)

        # --- Main Sound Area ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Your Sounds")
        self.scrollable_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(tuple(range(10)), weight=1)

    # --- Core Functionality ---

    def add_sound_dialog(self, edit_target=None):
        """Popup dialog to add or edit sound metadata."""
        # If not editing, pick a file first
        if not edit_target:
            file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
            if not file_path: return
            initial_title = os.path.basename(file_path)
            initial_color = "#3a7ebf"
            initial_shape = "Round"
        else:
            file_path = edit_target.data["path"]
            initial_title = edit_target.data["title"]
            initial_color = edit_target.data["color"]
            initial_shape = edit_target.data["shape"]

        # Simple Toplevel Dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sound Properties")
        dialog.geometry("300x400")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Sound Title:").pack(pady=(10, 0))
        title_entry = ctk.CTkEntry(dialog)
        title_entry.insert(0, initial_title)
        title_entry.pack(pady=5)

        # Color Selection (Using colorchooser)
        color_val = [initial_color]
        def pick_color():
            color = colorchooser.askcolor(title="Pick Button Color")[1]
            if color: color_val[0] = color

        ctk.CTkButton(dialog, text="Pick Color", command=pick_color).pack(pady=5)

        shape_var = ctk.StringVar(value=initial_shape)
        ctk.CTkRadioButton(dialog, text="Round", variable=shape_var, value="Round").pack()
        ctk.CTkRadioButton(dialog, text="Square", variable=shape_var, value="Square").pack()

        def save_and_close():
            new_data = {
                "path": file_path,
                "title": title_entry.get(),
                "color": color_val[0],
                "shape": shape_var.get()
            }
            if edit_target:
                # Update existing
                idx = self.config["sounds"].index(edit_target.data)
                self.config["sounds"][idx] = new_data
            else:
                # Append new
                self.config["sounds"].append(new_data)
            
            self.save_config()
            self.refresh_grid()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save Sound", fg_color="green", command=save_and_close).pack(pady=20)
        
        if edit_target:
            def delete_sound():
                self.config["sounds"].remove(edit_target.data)
                self.save_config()
                self.refresh_grid()
                dialog.destroy()
            ctk.CTkButton(dialog, text="Delete", fg_color="red", command=delete_sound).pack()

    def play_sound(self, path):
        """Plays sound with polyphony (overlapping allowed)."""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError
            sound = pygame.mixer.Sound(path)
            sound.play()
        except Exception as e:
            messagebox.showerror("Audio Error", f"Could not play file: {e}")

    def on_button_right_click(self, button_widget):
        """Handles edit mode logic when a button is right-clicked."""
        if self.edit_mode.get():
            self.add_sound_dialog(edit_target=button_widget)

    def refresh_grid(self):
        """Clears and rebuilds the button grid based on current config."""
        # Clear existing
        for widget in self.sound_widgets:
            widget.destroy()
        self.sound_widgets = []

        cols = int(self.config["columns"])
        size = self.config["button_size"]

        for i, sound_data in enumerate(self.config["sounds"]):
            r, c = divmod(i, cols)
            btn = SoundButton(
                self.scrollable_frame, 
                sound_data, 
                play_command=self.play_sound,
                edit_command=self.on_button_right_click,
                width=size,
                height=size
            )
            btn.grid(row=r, column=c, padx=10, pady=10)
            self.sound_widgets.append(btn)

    # --- Settings & Persistence ---

    def update_grid_config(self, value):
        self.config["columns"] = int(value)
        self.save_config()
        self.refresh_grid()

    def toggle_theme(self):
        new_theme = "light" if self.config["theme"] == "dark" else "dark"
        self.config["theme"] = new_theme
        ctk.set_appearance_mode(new_theme)
        self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_SETTINGS.copy()

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

if __name__ == "__main__":
    app = SoundboardApp()
    app.mainloop()