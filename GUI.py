import customtkinter as ctk
import os
from threading import Thread
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import END, StringVar
from functions import transcribe as transcribe_file
from time import time, sleep
from PIL import Image
from config import *
CONFIG: dict = load_config()
STRINGS: dict = load_language(CONFIG["language"])
ctk.set_appearance_mode(CONFIG["appearance_mode"])
ctk.set_default_color_theme(CONFIG["theme"])
TITLE_FONT = ("Arial", 20, "bold")  # TODO: Load fonts from file

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Define StringVars
        self.api_key = CONFIG["api_key"]
        self.transcribed_text = ""
        self.time_elapsed = StringVar()
        self.settings_window = None
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        light_icon = Image.open(os.path.join(current_file_path, "icons", "settings_light_mode.png"))
        dark_icon = Image.open(os.path.join(current_file_path, "icons", "settings_dark_mode.png"))
        self.settings_icon = ctk.CTkImage(light_image=light_icon, dark_image=dark_icon, size=(30, 30))

        self.title(STRINGS["title"])
        # self.resizable(False, False)
        self.geometry("500x450")

        # create 2x6 grid system
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Define frames and widgets
        # Title label
        self.title_label = ctk.CTkLabel(self, text=STRINGS["title"], font=TITLE_FONT, width=750)
        self.title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Settings button
        self.settings_button = ctk.CTkButton(self, image=self.settings_icon, fg_color="transparent", height=40, width=40, text="", command=self.open_settings)
        self.settings_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Input CtkEntry for OpenAI API key
        self.api_key_entry = ctk.CTkEntry(self, placeholder_text=STRINGS["api_key_entry_placeholder"])
        if self.api_key != "": self.api_key_entry.insert(0, self.api_key)
        self.api_key_entry.bind("<FocusOut>", self.save_api_key)
        self.api_key_entry.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        # Input CtkEntry for file path
        self.file_path_entry = ctk.CTkEntry(self, placeholder_text=STRINGS["file_path_entry_placeholder"])
        self.file_path_entry.bind("<FocusOut>", self.check_file_path)
        self.choose_file_button = ctk.CTkButton(self, text=STRINGS["choose_file_button"], command=self.choose_file)
        self.file_path_entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.choose_file_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Output CtkTextbox for generated text
        self.generated_text = ctk.CTkTextbox(self, width=50, height=10)
        self.generated_text.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # Time elapsed label
        self.time_elapsed_label = ctk.CTkLabel(self, textvariable=self.time_elapsed)
        self.time_elapsed_label.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        # Transcribe and save buttons
        self.transcribe_button = ctk.CTkButton(self, text=STRINGS["transcribe_button"], state="disabled", command=self.transcribe)
        self.transcribe_button.grid(row=5, column=0, padx=10, pady=10)
        self.save_to_file_button = ctk.CTkButton(self, text=STRINGS["save_to_file_button"], state="disabled", command=self.save_to_file)
        self.save_to_file_button.grid(row=5, column=1, padx=10, pady=10, sticky="e")

    def choose_file(self):
        """Open a file dialog to choose a file."""
        self.file_path_entry.delete(0, END)
        self.file_path_entry.insert(0, askopenfilename(title=STRINGS["choose_file_dialog_title"],
                                           filetypes=(
                                                ("MP3 files", " .mp3 .MP3"),
                                                ("MP4 files", " .mp4 .MP4"),
                                                ("MPEG files", " .mpeg .MPEG"),
                                                ("MPGA files", " .mpga .MPGA"),
                                                ("M4A files", " .m4a .M4A"),
                                                ("WAV files", " .wav .WAV"),
                                                ("WEBM files", " .webm .WEBM"),
                                                (STRINGS["choose_all_files_types_dialog"], "*.*"),
                                           )))
        self.check_file_path()

    def check_file_path(self, event=None):
        """Check if the file path is valid."""
        file_path = self.file_path_entry.get()
        if file_path == "" or not os.path.isfile(file_path) or not self.check_api_format():
            self.transcribe_button.configure(state="disabled")
        else:
            self.transcribe_button.configure(state="normal")

    def transcribe(self):
        """Transcribe the file."""
        file_path = self.file_path_entry.get()
        
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.generated_text.delete('1.0', END)
        def thread_function():
            self.transcribed_text = transcribe_file(file_path, self.api_key_entry.get())
            self.generated_text.insert("1.0", self.transcribed_text)
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.save_to_file_button.configure(state="normal")
            self.progress_bar.set(100)
        transcribe_thread = Thread(target=thread_function, daemon=True)
        transcribe_thread.start()
        start_time = time()
        def update_time():
            while transcribe_thread.is_alive():
                self.time_elapsed.set(f"{time() - start_time:.2f}")
                sleep(0.05)
        update_time_thread = Thread(target=update_time, daemon=True)
        update_time_thread.start()
            
    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            # create window if its None or destroyed
            self.settings_window = ConfigWindow()
        else:
            self.settings_window.focus()  # if window exists focus it

    def save_to_file(self):
        """Save the generated text to a file."""
        file_path = asksaveasfilename()
        with open(file_path, "w") as f:
            f.write(self.transcribed_text)

    def check_api_format(self, event = None):
        if self.api_key_entry.get().startswith("sk-"):
            return True
        return False

    def save_api_key(self, event):
        """Save the config to the config file."""
        # If it doesn't start with "sk-" then it's not a valid API key
        if not self.check_api_format():
            self.api_key_entry.delete(0, END)
            self.api_key_entry.insert(0, self.api_key)
            self.transcribe_button.configure(state="disabled")
            return
        CONFIG["api_key"] = self.api_key_entry.get()
        save_config(CONFIG)
        self.transcribe_button.configure(state="normal")

class ConfigWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        # self.geometry("300x200")
        self.resizable(False, False)
        self.title(STRINGS["config_window_title"])

        # Title label
        self.title_label = ctk.CTkLabel(self, text=STRINGS["config_window_title"], font=TITLE_FONT)
        self.title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Appearance mode
        self.appearance_mode_label = ctk.CTkLabel(self, text=STRINGS["appearance_mode_label"])
        values = [
            STRINGS["appearance_mode_light"],
            STRINGS["appearance_mode_dark"],
            STRINGS["appearance_mode_system"]
        ]
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=values, command=self.change_appearance_mode_event)
        # Check current config value
        if CONFIG["appearance_mode"] == "light":
            self.appearance_mode_optionemenu.set(STRINGS["appearance_mode_light"])
        elif CONFIG["appearance_mode"] == "dark":
            self.appearance_mode_optionemenu.set(STRINGS["appearance_mode_dark"])
        elif CONFIG["appearance_mode"] == "system":
            self.appearance_mode_optionemenu.set(STRINGS["appearance_mode_system"])
        self.appearance_mode_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.appearance_mode_optionemenu.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Language
        self.language_label = ctk.CTkLabel(self, text=STRINGS["language_label"])
        values = [
            STRINGS["language_english"],
            STRINGS["language_french"]
        ]
        self.language_optionemenu = ctk.CTkOptionMenu(self, values=values, command=self.change_language_event)
        # Check current config value
        if CONFIG["language"] == "en":
            self.language_optionemenu.set(STRINGS["language_english"])
        elif CONFIG["language"] == "fr":
            self.language_optionemenu.set(STRINGS["language_french"])
        self.language_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.language_optionemenu.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Color scheme
        self.color_scheme_label = ctk.CTkLabel(self, text=STRINGS["color_scheme_label"])
        values = [
            STRINGS["color_scheme_blue"],
            STRINGS["color_scheme_green"],
            STRINGS["color_scheme_darkblue"]
        ]
        self.color_scheme_optionemenu = ctk.CTkOptionMenu(self, values=values, command=self.change_color_scheme_event)
        # Check current config value
        if CONFIG["theme"] == "blue":
            self.color_scheme_optionemenu.set(STRINGS["color_scheme_blue"])
        elif CONFIG["theme"] == "green":
            self.color_scheme_optionemenu.set(STRINGS["color_scheme_green"])
        elif CONFIG["theme"] == "dark-blue":
            self.color_scheme_optionemenu.set(STRINGS["color_scheme_darkblue"])
        self.color_scheme_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.color_scheme_optionemenu.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        # Reboot required label
        self.reboot_required_label = ctk.CTkLabel(self, text=STRINGS["reboot_required_label"])
        self.reboot_required_label.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

    def change_appearance_mode_event(self, event):
        """Change the appearance mode."""
        if event == STRINGS["appearance_mode_light"]:
            CONFIG["appearance_mode"] = "light"
        elif event == STRINGS["appearance_mode_dark"]:
            CONFIG["appearance_mode"] = "dark"
        elif event == STRINGS["appearance_mode_system"]:
            CONFIG["appearance_mode"] = "system"
        save_config(CONFIG)
        ctk.set_appearance_mode(CONFIG["appearance_mode"])

    def change_language_event(self, event):
        """Change the language."""
        if event == STRINGS["language_english"]:
            CONFIG["language"] = "en"
        elif event == STRINGS["language_french"]:
            CONFIG["language"] = "fr"
        save_config(CONFIG)

    def change_color_scheme_event(self, event):
        """Change the color scheme."""
        if event == STRINGS["color_scheme_blue"]:
            CONFIG["theme"] = "blue"
        elif event == STRINGS["color_scheme_green"]:
            CONFIG["theme"] = "green"
        elif event == STRINGS["color_scheme_darkblue"]:
            CONFIG["theme"] = "dark-blue"
        save_config(CONFIG)


if __name__ == "__main__":
    app = App()
    app.mainloop()