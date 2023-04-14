import customtkinter as ctk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from functions import transcribe as transcribe_file
from config import *
CONFIG: dict = load_config()
STRINGS: dict = load_language(CONFIG["language"])
ctk.set_appearance_mode(CONFIG["appearance_mode"])
ctk.set_default_color_theme(CONFIG["theme"])
TITLE_FONT = ("Arial", 20, "bold")  # TODO: Load fonts from file

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(STRINGS["title"])
        # self.resizable(False, False)
        self.geometry("500x500")

        # create 2x6 grid system
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # Define frames and widgets
        # Title label
        self.title_label = ctk.CTkLabel(self, text=STRINGS["title"], font=TITLE_FONT, width=750)
        self.title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Input CtkEntry for OpenAI API key
        self.api_key_entry = ctk.CTkEntry(self, placeholder_text=STRINGS["api_key_entry_placeholder"])
        self.api_key_entry.configure(textvariable=(CONFIG["api_key"]))
        self.api_key_entry.bind("<Return>", self.save_api_key)
        self.api_key_entry.grid(row=1, column=0, padx=10, pady=10)

        # Input CtkEntry for file path
        self.file_path_entry = ctk.CTkEntry(
            self, placeholder_text=STRINGS["file_path_entry_placeholder"])
        self.choose_file_button = ctk.CTkButton(
            self, text=STRINGS["choose_file_button"], command=self.choose_file)
        self.file_path_entry.grid(row=2, column=0, padx=10, pady=10)
        self.choose_file_button.grid(row=2, column=1, padx=10, pady=10)

        # Output CtkTextbox for generated text
        self.generated_text = ctk.CTkTextbox(self, width=50, height=10)
        self.generated_text.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=50)
        self.progress_bar.grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        # Transcribe and save buttons
        self.transcribe_button = ctk.CTkButton(
            self, text=STRINGS["transcribe_button"], command=self.transcribe)
        self.transcribe_button.grid(row=5, column=0, padx=10, pady=10)
        self.save_to_file_button = ctk.CTkButton(
            self, text=STRINGS["save_to_file_button"], command=self.save_to_file)
        self.save_to_file_button.grid(row=5, column=1, padx=10, pady=10)

    def choose_file(self):
        """Open a file dialog to choose a file."""
        file_path = askopenfilename()
        self.file_path_entry.set(file_path)

    def transcribe(self):
        """Transcribe the file."""
        file_path = self.file_path_entry.get()
        
        generated_text = transcribe_file(file_path)
        self.generated_text.set(generated_text)

    def save_to_file(self):
        """Save the generated text to a file."""
        file_path = asksaveasfilename()
        with open(file_path, "w") as f:
            f.write(self.generated_text.get())

    def save_api_key(self, event):
        """Save the config to the config file."""
        CONFIG["api_key"] = self.api_key_entry.get()
        save_config(CONFIG)

if __name__ == "__main__":
    app = App()
    app.mainloop()